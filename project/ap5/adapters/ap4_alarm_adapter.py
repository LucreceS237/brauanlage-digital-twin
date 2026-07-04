"""
File: ap4_alarm_adapter.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Converts AP4 diagnostics (safety + process faults produced by Engineer C's FSM) into AP5 Alarm objects with the approved vessel labels. AP5 does NOT re-implement AP4's process/safety fault logic; it only reformats AP4's findings into the alarm schema used by AP3 storage and the AP6 frontend.
"""
from __future__ import annotations

from project.ap4.diagnostics import Diagnostic, Severity
from project.ap4.fsm_contract import TransitionResult

from ..anomaly_detection.alarm import Alarm, AlarmSeverity, make_alarm
from .mapping import APPROVED_VESSELS

# AP4 canonical signal -> approved physical vessel key (reverse of the rotation).
_AP4_SIGNAL_TO_VESSEL: dict[str, str] = {
    "k3_temperature_c": "K1", "k3_level_l": "K1",
    "k1_temperature_c": "K2", "k1_level_l": "K2",
    "k2_temperature_c": "K3", "k2_level_l": "K3",
    "k4_temperature_c": "K4", "k4_level_l": "K4",
    "flow_k3_to_k1_l_min": "K1",
}

_SEVERITY_MAP: dict[Severity, AlarmSeverity] = {
    Severity.INFO: AlarmSeverity.LOW,
    Severity.WARNING: AlarmSeverity.MEDIUM,
    Severity.ERROR: AlarmSeverity.HIGH,
    Severity.EMERGENCY: AlarmSeverity.CRITICAL,
}


def _component_for(signal: str | None) -> str:
    """Resolve an approved-vessel component label from an AP4 signal name."""
    if not signal:
        return "Anlage"
    vessel = _AP4_SIGNAL_TO_VESSEL.get(signal)
    if vessel:
        return f"{vessel} {APPROVED_VESSELS[vessel]}"
    return signal


def diagnostic_to_alarm(diag: Diagnostic, display_state: str) -> Alarm:
    """Map a single AP4 Diagnostic into an AP5 Alarm."""
    severity = _SEVERITY_MAP.get(diag.severity, AlarmSeverity.MEDIUM)
    return make_alarm(
        rule_id=diag.code_text,                 # AP4 fault code is the stable rule id
        code=diag.code_text,
        severity=severity,
        state=display_state,
        component=_component_for(diag.signal),
        variable=diag.signal or "-",
        value=diag.value,
        threshold="-" if diag.limit is None else str(diag.limit),
        message=diag.message,
    )


def transition_to_alarms(result: TransitionResult) -> list[Alarm]:
    """Convert all diagnostics from an AP4 TransitionResult into alarms."""
    return [diagnostic_to_alarm(d, result.display_state) for d in result.diagnostics]
