from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .fault_catalog import descriptor_for, FaultCode
from .fsm_contract import FsmContext


def build_ap5_payload(context: FsmContext) -> dict[str, Any]:
    """Payload für AP5 Anomalieerkennung.

    AP5 erhält den Prozesszustand, den eindeutigen Fehlercode, Diagnosen,
    erwartete Aktorzustände und Zähler. AP5 muss nicht direkt die FSM lesen.
    """
    payload: dict[str, Any] = {
        "consumer": "AP5_Anomalieerkennung",
        "state": context.state,
        "display_state": context.display_state,
        "time_in_state_s": context.time_in_state_s,
        "active_fault_code": context.active_fault_code,
        "active_fault_title": context.active_fault_title,
        "active_fault_signal": context.active_fault_signal,
        "active_fault_value": context.active_fault_value,
        "active_fault_limit": context.active_fault_limit,
        "diagnostics": [
            {
                "severity": d.severity.value,
                "code": d.code_text,
                "title": d.descriptor_title,
                "signal": d.signal,
                "value": d.value,
                "limit": d.limit,
                "message": d.message,
            }
            for d in context.diagnostics
        ],
        "expected_outputs": asdict(context.outputs),
        "metrics": {
            "transition_counter": context.transition_counter,
            "error_counter": context.error_counter,
            "emergency_counter": context.emergency_counter,
            "fault_counters": context.fault_counters,
        },
        "last_transition_reason": context.last_transition_reason,
    }
    return payload


def build_ap6_dashboard_payload(context: FsmContext) -> dict[str, Any]:
    """Payload für AP6 Dashboard/REST-API."""
    severity = "NORMAL"
    operator_message = f"Aktueller Zustand: {context.display_state}"
    recommended_action = "Keine Aktion erforderlich."
    subsystem = None
    if context.active_fault_code:
        code = FaultCode(context.active_fault_code)
        desc = descriptor_for(code)
        severity = desc.superstate
        operator_message = desc.title
        recommended_action = desc.recommended_action
        subsystem = desc.subsystem
    return {
        "consumer": "AP6_Dashboard_REST_API",
        "current_state": context.state,
        "display_state": context.display_state,
        "severity": severity,
        "active_fault_code": context.active_fault_code,
        "operator_message": operator_message,
        "recommended_action": recommended_action,
        "subsystem": subsystem,
        "signal": context.active_fault_signal,
        "value": context.active_fault_value,
        "limit": context.active_fault_limit,
        "expected_outputs": asdict(context.outputs),
        "transition_counter": context.transition_counter,
        "last_transition_reason": context.last_transition_reason,
    }
