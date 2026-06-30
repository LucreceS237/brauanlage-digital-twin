from __future__ import annotations

from dataclasses import dataclass, field

from .diagnostics import Diagnostic
from .states import BrewState


@dataclass(frozen=True)
class ExpectedOutputs:
    heater_k1_on: bool = False
    heater_k2_on: bool = False
    agitator_on: bool = False
    pump_on: bool = False
    v3_open: bool = False
    v4_open: bool = False
    v5_open: bool = False


@dataclass(frozen=True)
class FsmContext:
    """Offizielle AP4-Ausgangsschnittstelle für AP5 und AP6."""

    state: str
    display_state: str
    time_in_state_s: float
    outputs: ExpectedOutputs
    diagnostics: tuple[Diagnostic, ...]
    active_fault_code: str | None
    active_fault_title: str | None
    active_fault_signal: str | None
    active_fault_value: float | bool | str | None
    active_fault_limit: float | str | None
    last_transition_reason: str | None
    transition_counter: int
    error_counter: int
    emergency_counter: int
    fault_counters: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class FsmMetrics:
    transition_counter: int
    error_counter: int
    emergency_counter: int
    blocked_transition_counter: int
    fault_counters: dict[str, int]


@dataclass(frozen=True)
class TransitionRecord:
    counter: int
    old_state: BrewState
    new_state: BrewState
    display_state: str
    reason_code: str
    message: str
    time_in_old_state_s: float
    active_fault_code: str | None = None

    def terminal_line(self) -> str:
        fault = f" | fault={self.active_fault_code}" if self.active_fault_code else ""
        return f"#{self.counter}: {self.old_state.name} -> {self.display_state} | reason={self.reason_code}{fault} | t={self.time_in_old_state_s:.1f}s"


@dataclass(frozen=True)
class TransitionResult:
    previous_state: BrewState
    state: BrewState
    display_state: str
    changed: bool
    reason_code: str
    message: str
    diagnostics: tuple[Diagnostic, ...]
    expected_outputs: ExpectedOutputs
    active_fault: Diagnostic | None = None

    def terminal_lines(self) -> list[str]:
        lines = [
            f"Übergang: {self.previous_state.name} -> {self.display_state}",
            f"Jetzt ist Zustand: {self.display_state}",
            f"Grund: {self.reason_code} - {self.message}",
            f"Geändert: {'JA' if self.changed else 'NEIN'}",
        ]
        if self.active_fault:
            lines.append(f"Aktiver Fehlerzustand: {self.active_fault.code_text}")
            lines.append(f"Fehlertitel: {self.active_fault.descriptor_title}")
        for diag in self.diagnostics:
            lines.append(diag.terminal_line())
        return lines
