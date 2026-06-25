# src/anomaly_detection/alarm.py

"""
===========================================================
ALARM MODEL
===========================================================

This module defines the common alarm structure used by the
anomaly detection system.

Why is this file important?
---------------------------
In the digital twin, different modules need to exchange alarm
information:

- anomaly rules create alarms
- detector.py tracks active alarms
- api.py exposes alarms through /api/status
- tests verify alarm behavior
- documentation explains alarm meaning

Therefore, every alarm should follow one common structure.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class Severity(str, Enum):
    """
    Severity levels for anomaly alarms.

    LOW:
        Informational warning.
        The process can usually continue.

    MEDIUM:
        Process deviation.
        Operator should observe the situation.

    HIGH:
        Serious process deviation.
        The system or process quality may be affected.

    CRITICAL:
        Potential safety or equipment risk.
        Immediate attention required.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlarmStatus(str, Enum):
    """
    Lifecycle status of an alarm.

    ACTIVE:
        The anomaly is currently detected.

    CLEARED:
        The anomaly condition is no longer present.

    ACKNOWLEDGED:
        The operator has seen the alarm.
        This is useful for later versions with manual acknowledgement.
    """

    ACTIVE = "ACTIVE"
    CLEARED = "CLEARED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


@dataclass
class Alarm:
    """
    Standard alarm object.

    Every rule should return alarms using this structure.

    Attributes
    ----------
    timestamp:
        Time when the alarm was first created.

    rule_id:
        Unique rule identifier.
        Example: R003

    code:
        Human-readable alarm code.
        Example: TEMP_TOO_HIGH

    severity:
        Alarm severity level.

    state:
        Current FSM state when the alarm occurred.
        Example: MASHING, LAUTERING, IDLE

    component:
        Physical or logical system component.
        Example: K1, K2, K3, FLOW_PATH

    variable:
        SPS/OPC-UA variable that triggered the alarm.
        Example: K2_Temperatur

    value:
        Current measured value.

    threshold:
        Limit or expected condition.

    message:
        Short explanation of the anomaly.

    status:
        Current alarm lifecycle status.

    cleared_at:
        Time when the alarm was cleared.
        None while alarm is active.

    acknowledged:
        True if the operator acknowledged the alarm.
        Not required for v0.1, but useful for future versions.
    """

    timestamp: str
    rule_id: str
    code: str
    severity: Severity
    state: str
    component: str
    variable: str
    value: Any
    threshold: Any
    message: str
    status: AlarmStatus = AlarmStatus.ACTIVE
    cleared_at: Optional[str] = None
    acknowledged: bool = False

    def key(self) -> tuple[str, str, str]:
        """
        Create a stable identifier for this alarm.

        Why?
        ----
        Since the SPS sends values every second, the same anomaly may
        be detected repeatedly.

        The key helps detector.py avoid duplicated alarms.

        Example:
            ("R003", "K2_Temperatur", "TEMP_TOO_HIGH")
        """

        return self.rule_id, self.variable, self.code

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert alarm to JSON-compatible dictionary.

        The API can directly return this dictionary.
        """

        data = asdict(self)

        data["severity"] = self.severity.value
        data["status"] = self.status.value

        return data

    def clear(self) -> None:
        """
        Mark the alarm as cleared.

        This does not delete the alarm.
        It only changes its lifecycle state.

        Useful for alarm history in later versions.
        """

        self.status = AlarmStatus.CLEARED
        self.cleared_at = utc_now()

    def acknowledge(self) -> None:
        """
        Mark the alarm as acknowledged by an operator.

        In v0.1 this is optional.
        In v0.2 it could be connected to the API or HMI.
        """

        self.acknowledged = True
        self.status = AlarmStatus.ACKNOWLEDGED


def utc_now() -> str:
    """
    Return current UTC timestamp in ISO format.

    Using UTC avoids problems with local timezone differences between:
    - SPS
    - development laptops
    - API clients
    - logs
    """

    return datetime.now(timezone.utc).isoformat()


def create_alarm(
    rule_id: str,
    code: str,
    severity: Severity,
    state: str,
    component: str,
    variable: str,
    value: Any,
    threshold: Any,
    message: str,
) -> Alarm:
    """
    Factory function to create a standard alarm.

    Why use this function?
    ----------------------
    It avoids repeating the timestamp and Alarm constructor in every rule.

    Example:
        create_alarm(
            rule_id="R003",
            code="TEMP_TOO_HIGH",
            severity=Severity.HIGH,
            state="MASHING",
            component="K2",
            variable="K2_Temperatur",
            value=85.0,
            threshold=78.0,
            message="K2 temperature exceeds upper limit."
        )
    """

    return Alarm(
        timestamp=utc_now(),
        rule_id=rule_id,
        code=code,
        severity=severity,
        state=state,
        component=component,
        variable=variable,
        value=value,
        threshold=threshold,
        message=message,
    )