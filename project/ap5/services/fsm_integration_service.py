"""
File: fsm_integration_service.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: The single clean interface between the rest of the system and Engineer C's AP4 FSM. AP5 does NOT create a competing FSM; it drives AP4:
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from project.ap4.fsm import BrewStateMachine
from project.ap4.recipe import BrewRecipe

from ..adapters.ap4_alarm_adapter import transition_to_alarms
from ..adapters.snapshot_adapter import build_snapshot
from ..anomaly_detection.alarm import Alarm

# Durations aligned with the shared ProcessSimulator (~30 min compressed demo).
# Temperature/level windows keep AP4's engineering defaults.
DEMO_RECIPE = BrewRecipe(
    nachguss_min_duration_s=5.0,
    mashing_duration_s=350.0,
    lautering_duration_s=180.0,
    boiling_duration_s=270.0,
    transfer_to_k4_duration_s=30.0,
    fermentation_duration_s=570.0,
)


@dataclass
class FsmUpdate:
    """Normalised, frontend-ready result of one AP4 update."""

    state: str
    display_state: str
    previous_state: str
    changed: bool
    reason_code: str
    message: str
    time_in_state_s: float
    active_fault_code: str | None
    diagnostics: list[str] = field(default_factory=list)
    alarms: list[Alarm] = field(default_factory=list)


class FsmIntegrationService:
    """Owns one AP4 BrewStateMachine for the active session."""

    def __init__(self, demo_mode: bool = True) -> None:
        recipe = DEMO_RECIPE if demo_mode else BrewRecipe()
        self.machine = BrewStateMachine(recipe=recipe)

    def update(
        self,
        values: Mapping[str, Any],
        dt_s: float = 1.0,
        missing_value_age_s: float = 0.0,
    ) -> FsmUpdate:
        """Feed one MQTT/SPS payload's values through AP4 and return the result."""
        snapshot = build_snapshot(values, missing_value_age_s=missing_value_age_s)
        result = self.machine.update(snapshot, dt_s=dt_s)
        alarms = transition_to_alarms(result)
        return FsmUpdate(
            state=result.state.name,
            display_state=result.display_state,
            previous_state=result.previous_state.name,
            changed=result.changed,
            reason_code=result.reason_code,
            message=result.message,
            time_in_state_s=self.machine.time_in_state_s,
            active_fault_code=result.active_fault.code_text if result.active_fault else None,
            diagnostics=[d.terminal_line() for d in result.diagnostics],
            alarms=alarms,
        )

    @property
    def current_state(self) -> str:
        return self.machine.state.name
