"""
===========================================================
ANOMALY DETECTOR
===========================================================

This module coordinates the anomaly detection process for the
Digital Twin of the Brewing System.

The brewing system is not static. The SPS sends new values every
second. The digital twin must therefore evaluate a continuous stream
of process snapshots.

A single bad value should not always create a permanent alarm.
The detector gives structure to the real-time behavior.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Tuple

from .rules import Alarm, evaluate_rules


class AnomalyDetector:
    """
    Main anomaly detection engine.

    Responsibilities
    ----------------
    1. Receive live snapshots from the OPC-UA collector.
    2. Store recent snapshots in memory.
    3. Call all anomaly rules.
    4. Track currently active alarms.
    5. Return active alarms to the API or logging system.

    Important concept
    -----------------
    The detector does not directly read from the SPS.
    It receives already collected data from Engineer B's data layer.

    Expected input
    --------------
    A snapshot is a dictionary representing the current digital-twin state.

    Example:

        {
            "_received_at": "2026-06-01T10:15:00+00:00",
            "state": "MASHING",
            "K2_Temperatur": 70.5,
            "K2_Temperatur_SollwertObereGrenze": 78.0,
            "K2_Temperatur_SollwertUntereGrenze": 62.0,
            "Durchfluss_NachgussMaische": 0.0,
            "_meta": {
                "K2_Temperatur": {
                    "timestamp": "2026-06-01T10:15:00+00:00",
                    "quality": "Good"
                }
            }
        }
    """

    def __init__(
        self,
        history_seconds: int = 300,
        expected_sampling_interval_seconds: float = 1.0,
    ) -> None:
        """
        Initialize the detector.

        Parameters
        ----------
        history_seconds:
            How long snapshots should be kept in memory.

            Example:
                300 seconds = 5 minutes of history.

            We need history for trend-based rules like:
                - temperature rise too fast
                - cooling too slow
                - flow instability

        expected_sampling_interval_seconds:
            Expected SPS polling interval.

            Since the SPS values are received every second, we expect
            approximately 1 snapshot per second.
        """

        self.history_seconds = history_seconds
        self.expected_sampling_interval_seconds = expected_sampling_interval_seconds

        # Maximum number of snapshots stored in memory.
        #
        # Example:
        # history_seconds = 300
        # sampling interval = 1 s
        # maxlen = 300 snapshots
        max_history_length = int(
            history_seconds / expected_sampling_interval_seconds
        )

        self.history: Deque[Dict[str, Any]] = deque(maxlen=max_history_length)

        # Active alarms are stored using a stable alarm key.
        #
        # The key prevents the same alarm from being duplicated every second.
        #
        # Example key:
        # ("R003", "K2_Temperatur", "TEMP_TOO_HIGH")
        self.active_alarms: Dict[Tuple[str, str, str], Alarm] = {}

    def update(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate a new real-time snapshot.

        This method should be called once for every new SPS/OPC-UA update.

        Typical usage:
            detector = AnomalyDetector()
            alarms = detector.update(snapshot)

        Processing steps
        ----------------
        1. Ensure the snapshot has a timestamp.
        2. Store the snapshot in history.
        3. Run all rules from rules.py.
        4. Update the active alarm list.
        5. Return alarms as dictionaries for API/JSON output.
        """

        # Step 1:
        # If the collector did not provide a timestamp, we add one here.
        # This makes the detector robust during early development.
        if "_received_at" not in snapshot:
            snapshot["_received_at"] = datetime.now(timezone.utc).isoformat()

        # Step 2:
        # Store the current snapshot.
        #
        # This history enables trend-based rules such as temperature gradient.
        self.history.append(snapshot)

        # Step 3:
        # Evaluate all anomaly rules using:
        # - current snapshot
        # - recent history
        detected_alarms = evaluate_rules(
            snapshot=snapshot,
            history=list(self.history),
        )

        # Step 4:
        # Update internal alarm state.
        self._update_active_alarms(detected_alarms)

        # Step 5:
        # Return currently active alarms in JSON-compatible form.
        return self.get_active_alarms()

    def _update_active_alarms(self, detected_alarms: List[Alarm]) -> None:
        """
        Update the active alarm registry.

        Why is this needed?
        -------------------
        The SPS sends data every second. If a temperature stays too high
        for 2 minutes, the rule would detect the same problem 120 times.

        We do NOT want 120 duplicated alarms.

        Instead:
            - first detection creates/activates the alarm
            - repeated detections keep the alarm active
            - when the rule no longer detects it, the alarm disappears

        Note:
        -----
        This is a simple v0.1 alarm lifecycle.
        Later versions can add:
            - acknowledgement
            - alarm history
            - alarm reset delay
            - hysteresis
        """

        new_active_alarms: Dict[Tuple[str, str, str], Alarm] = {}

        for alarm in detected_alarms:
            key = self._alarm_key(alarm)

            # If alarm already existed, keep the original timestamp.
            # This tells us when the problem first appeared.
            if key in self.active_alarms:
                existing_alarm = self.active_alarms[key]

                alarm.timestamp = existing_alarm.timestamp

            new_active_alarms[key] = alarm

        # Replace active alarm set.
        #
        # Any alarm that was active before but is not detected now
        # is automatically cleared.
        self.active_alarms = new_active_alarms

    def _alarm_key(self, alarm: Alarm) -> Tuple[str, str, str]:
        """
        Create a stable identifier for an alarm.

        We use:
            rule_id + variable + code

        Example:
            R003 + K2_Temperatur + TEMP_TOO_HIGH

        This is stable enough for v0.1.
        """

        return (
            alarm.rule_id,
            alarm.variable,
            alarm.code,
        )

    def get_active_alarms(self) -> List[Dict[str, Any]]:
        """
        Return all currently active alarms.

        The API layer can directly use this method for /api/status.

        Since dataclasses are not automatically JSON serializable,
        we convert each Alarm object into a dictionary.
        """

        return [
            self._alarm_to_dict(alarm)
            for alarm in self.active_alarms.values()
        ]

    def _alarm_to_dict(self, alarm: Alarm) -> Dict[str, Any]:
        """
        Convert Alarm dataclass to JSON-compatible dictionary.
        """

        data = asdict(alarm)

        # Enum values need to be converted to strings for JSON responses.
        data["severity"] = alarm.severity.value

        return data

    def clear_all_alarms(self) -> None:
        """
        Manually clear all active alarms.

        This is useful for:
            - tests
            - demo reset
            - future acknowledge/reset mechanism
        """

        self.active_alarms.clear()

    def get_history_size(self) -> int:
        """
        Return number of stored snapshots.

        Useful for debugging and tests.
        """

        return len(self.history)
