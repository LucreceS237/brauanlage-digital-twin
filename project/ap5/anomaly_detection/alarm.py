"""
File: alarm.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Self-contained alarm data model for AP5. An Alarm is the serialisable record that AP5 produces both from AP4 diagnostics (via ap4_alarm_adapter) and from AP5's own extra anomaly rules. Kept independent of the database layer (AP3) so AP5 can be unit-tested without MongoDB; AP3 stores these via `to_doc`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AlarmSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlarmStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLEARED = "CLEARED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


@dataclass
class Alarm:
    """One anomaly occurrence. Field names match the alarms collection schema."""

    ruleId: str
    code: str
    severity: str
    state: str
    component: str
    variable: str
    value: Any
    threshold: str
    message: str
    status: str = AlarmStatus.ACTIVE.value
    createdAt: Any = field(default_factory=utcnow)
    clearedAt: Optional[Any] = None

    def to_doc(self, session_id: str, snapshot_id: Optional[str] = None) -> dict:
        doc = asdict(self)
        doc["sessionId"] = session_id
        doc["snapshotId"] = snapshot_id
        return doc


def make_alarm(
    *,
    rule_id: str,
    code: str,
    severity: AlarmSeverity,
    state: str,
    component: str,
    variable: str,
    value: Any,
    threshold: str,
    message: str,
) -> Alarm:
    return Alarm(
        ruleId=rule_id,
        code=code,
        severity=severity.value if isinstance(severity, AlarmSeverity) else str(severity),
        state=state,
        component=component,
        variable=variable,
        value=value,
        threshold=threshold,
        message=message,
    )
