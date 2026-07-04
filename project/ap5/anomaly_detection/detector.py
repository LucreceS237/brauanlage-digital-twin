"""
File: detector.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Runs the EXTRA (transport/integration) anomaly rules against each incoming MQTT payload and returns the alarms that fired. Keeps small cross-cycle memory (previous values + timestamp) for rate-based rules. AP4 process/safety faults arrive separately via ap4_alarm_adapter and are NOT re-checked here.
"""
from __future__ import annotations

import time

from .alarm import Alarm
from .rules import EXTRA_RULES


class Ap5Detector:
    def __init__(self, expected_mode: str = "") -> None:
        self.expected_mode = expected_mode
        self._previous_values: dict = {}
        self._last_monotonic = time.monotonic()

    def evaluate(
        self,
        payload: dict,
        fsm_state: str,
        invalid_payload: bool = False,
        invalid_reason: str | None = None,
    ) -> list[Alarm]:
        now = time.monotonic()
        meta = {
            "expected_mode": self.expected_mode,
            "fsm_state": fsm_state,
            "seconds_since_last": now - self._last_monotonic,
            "previous_values": self._previous_values,
            "invalid_payload": invalid_payload,
            "invalid_reason": invalid_reason,
        }
        alarms = [a for rule in EXTRA_RULES if (a := rule(payload, meta)) is not None]

        if not invalid_payload and isinstance(payload.get("values"), dict):
            self._previous_values = dict(payload["values"])
        self._last_monotonic = now
        return alarms
