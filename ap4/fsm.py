from __future__ import annotations

from dataclasses import dataclass, field

from .diagnostics import Diagnostic, Severity, make_diagnostic
from .fault_catalog import FaultCode
from .fsm_contract import FsmContext, FsmMetrics, TransitionRecord, TransitionResult
from .outputs import expected_outputs_for_state
from .process_monitor import ProcessMonitor
from .process_snapshot import ProcessSnapshot
from .recipe import BrewRecipe, DEFAULT_RECIPE
from .safety import SafetySystem
from .states import ALLOWED_NORMAL_TRANSITIONS, BrewState


@dataclass
class BrewStateMachine:
    """AP4-Zustandsautomat Version 4 mit eindeutigen Fehlerzuständen."""

    recipe: BrewRecipe = DEFAULT_RECIPE
    safety_system: SafetySystem = field(default_factory=SafetySystem)
    process_monitor: ProcessMonitor = field(default_factory=ProcessMonitor)
    state: BrewState = BrewState.IDLE
    previous_state: BrewState = BrewState.IDLE
    time_in_state_s: float = 0.0
    transition_counter: int = 0
    error_counter: int = 0
    emergency_counter: int = 0
    blocked_transition_counter: int = 0
    last_transition_reason: str | None = None
    last_diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)
    active_fault: Diagnostic | None = None
    fault_counters: dict[str, int] = field(default_factory=dict)
    transition_history: list[TransitionRecord] = field(default_factory=list)

    def update(self, snapshot: ProcessSnapshot, dt_s: float = 1.0) -> TransitionResult:
        if dt_s < 0:
            raise ValueError("dt_s must be positive")
        dt_s = min(dt_s, 300.0)
        self.time_in_state_s += dt_s

        safety_diagnostics = self.safety_system.evaluate(snapshot)
        if safety_diagnostics and self.state != BrewState.EMERGENCY:
            primary = safety_diagnostics[0]
            return self._transition(BrewState.EMERGENCY, primary.code_text, primary.message, safety_diagnostics, primary)

        if self.state == BrewState.EMERGENCY:
            if snapshot.acknowledge and not safety_diagnostics:
                return self._transition(BrewState.IDLE, "EMERGENCY_ACKNOWLEDGED", "EMERGENCY wurde quittiert. Rückkehr nach IDLE.", [], None)
            self.last_diagnostics = tuple(safety_diagnostics)
            return self._stay("EMERGENCY_ACTIVE", "EMERGENCY bleibt aktiv.", safety_diagnostics, self.active_fault)

        if self.state == BrewState.ERROR:
            if snapshot.acknowledge:
                return self._transition(BrewState.IDLE, "ERROR_ACKNOWLEDGED", "ERROR wurde quittiert. Rückkehr nach IDLE.", [], None)
            return self._stay("ERROR_ACTIVE", "ERROR bleibt bis zur Quittierung aktiv.", list(self.last_diagnostics), self.active_fault)

        process_diagnostics = self.process_monitor.evaluate(self.state, snapshot)
        if process_diagnostics:
            primary = process_diagnostics[0]
            return self._transition(BrewState.ERROR, primary.code_text, primary.message, process_diagnostics, primary)

        target, reason, message = self._evaluate_normal_transition(snapshot)
        if target is not None:
            return self._transition(target, reason, message, [], None)

        self.last_diagnostics = tuple()
        return self._stay("NO_TRANSITION", "Keine Übergangsbedingung erfüllt.", [], None)

    def _evaluate_normal_transition(self, snapshot: ProcessSnapshot) -> tuple[BrewState | None, str, str]:
        s = self.state
        r = self.recipe
        t = self.time_in_state_s

        if s == BrewState.IDLE and snapshot.start_requested:
            return BrewState.PRECHECK, "START_REQUESTED", "Startanforderung erhalten. Vorprüfung beginnt."

        if s == BrewState.PRECHECK:
            if (
                snapshot.k3_level_l >= r.min_k3_start_level_l
                and r.nachguss_temperature_min_c <= snapshot.k3_temperature_c <= r.nachguss_temperature_max_c
                and snapshot.nv1_closed
                and snapshot.nv2_closed
                and snapshot.nv3_closed
            ):
                return BrewState.NACHGUSS, "PRECHECK_OK", "Vorprüfung erfolgreich. Nachguss aus K3 startet."
            return None, "PRECHECK_WAIT", "Vorbedingungen für Nachguss noch nicht erfüllt."

        if s == BrewState.NACHGUSS:
            if t >= r.nachguss_min_duration_s and snapshot.v3_open and snapshot.flow_k3_to_k1_l_min >= r.min_nachguss_flow_l_min and snapshot.k1_level_l >= r.min_k1_mashing_level_l:
                return BrewState.MASHING, "NACHGUSS_COMPLETE", "K1 ist für Maischen bereit."
            return None, "NACHGUSS_WAIT", "Nachguss läuft."

        if s == BrewState.MASHING:
            if t >= r.mashing_duration_s and r.mashing_temperature_min_c <= snapshot.k1_temperature_c <= r.mashing_temperature_max_c and snapshot.v4_open and snapshot.flow_k1_to_k2_l_min >= r.min_transfer_flow_l_min:
                return BrewState.LAUTERING, "MASHING_COMPLETE", "Maischen abgeschlossen. Läutern wird freigegeben."
            return None, "MASHING_WAIT", "Maischen noch nicht abgeschlossen."

        if s == BrewState.LAUTERING:
            if t >= r.lautering_duration_s and snapshot.k2_level_l >= r.min_k2_boiling_level_l:
                return BrewState.BOILING, "LAUTERING_COMPLETE", "Läutern abgeschlossen. Kochen wird freigegeben."
            return None, "LAUTERING_WAIT", "Läutern läuft."

        if s == BrewState.BOILING:
            if t >= r.boiling_duration_s and r.boiling_temperature_min_c <= snapshot.k2_temperature_c <= r.boiling_temperature_max_c:
                return BrewState.COOLING, "BOILING_COMPLETE", "Kochen abgeschlossen. Kühlung startet."
            return None, "BOILING_WAIT", "Kochen läuft."

        if s == BrewState.COOLING:
            if snapshot.k2_temperature_c <= r.cooling_target_c and snapshot.v5_open and snapshot.pump_on_feedback:
                return BrewState.TRANSFER_TO_K4, "COOLING_COMPLETE", "Kühlziel erreicht. Austrag nach K4 wird freigegeben."
            return None, "COOLING_WAIT", "Kühlung läuft."

        if s == BrewState.TRANSFER_TO_K4:
            if t >= r.transfer_to_k4_duration_s and snapshot.flow_k2_to_k4_l_min >= r.min_transfer_flow_l_min and snapshot.k4_level_l >= r.min_k4_fermentation_level_l:
                return BrewState.FERMENTING, "TRANSFER_TO_K4_COMPLETE", "Austrag nach K4 abgeschlossen. Gärung beginnt."
            return None, "TRANSFER_WAIT", "Austrag läuft."

        if s == BrewState.FERMENTING:
            if t >= r.fermentation_duration_s and r.fermentation_temperature_min_c <= snapshot.k4_temperature_c <= r.fermentation_temperature_max_c:
                return BrewState.FINISHED, "FERMENTATION_COMPLETE", "Gärung abgeschlossen."
            return None, "FERMENTING_WAIT", "Gärung läuft."

        return None, "NO_RULE", "Für diesen Zustand ist kein Normalübergang aktiv."

    def request_transition_for_test(self, target: BrewState) -> TransitionResult:
        if (self.state, target) not in ALLOWED_NORMAL_TRANSITIONS:
            self.blocked_transition_counter += 1
            diag = make_diagnostic(Severity.ERROR, FaultCode.ERROR_019_FORBIDDEN_TRANSITION, "transition", f"{self.state.name}->{target.name}", "allowed sequence")
            return self._transition(BrewState.ERROR, diag.code_text, diag.message, [diag], diag)
        return self._transition(target, "MANUAL_TEST_TRANSITION", "Manueller Testübergang erlaubt.", [], None)

    def _display_state_for(self, state: BrewState, active_fault: Diagnostic | None = None) -> str:
        if active_fault and state.is_fault_superstate:
            return active_fault.display_state
        return state.name

    def _transition(self, target: BrewState, reason: str, message: str, diagnostics: list[Diagnostic], active_fault: Diagnostic | None) -> TransitionResult:
        old = self.state
        self.previous_state = old
        self.state = target
        self.transition_counter += 1
        self.last_transition_reason = reason
        self.last_diagnostics = tuple(diagnostics)
        self.active_fault = active_fault

        if active_fault:
            key = active_fault.code_text
            self.fault_counters[key] = self.fault_counters.get(key, 0) + 1
        if target == BrewState.ERROR:
            self.error_counter += 1
        if target == BrewState.EMERGENCY:
            self.emergency_counter += 1
        if target == BrewState.IDLE and old in {BrewState.ERROR, BrewState.EMERGENCY}:
            self.active_fault = None
            self.last_diagnostics = tuple()

        display_state = self._display_state_for(target, self.active_fault)
        self.transition_history.append(
            TransitionRecord(self.transition_counter, old, target, display_state, reason, message, self.time_in_state_s, self.active_fault.code_text if self.active_fault else None)
        )
        self.time_in_state_s = 0.0
        return TransitionResult(old, target, display_state, old != target, reason, message, tuple(diagnostics), expected_outputs_for_state(target), self.active_fault)

    def _stay(self, reason: str, message: str, diagnostics: list[Diagnostic], active_fault: Diagnostic | None) -> TransitionResult:
        self.last_transition_reason = reason
        self.last_diagnostics = tuple(diagnostics)
        if active_fault is not None:
            self.active_fault = active_fault
        display_state = self._display_state_for(self.state, self.active_fault)
        return TransitionResult(self.state, self.state, display_state, False, reason, message, tuple(diagnostics), expected_outputs_for_state(self.state), self.active_fault)

    def get_context_for_anomaly(self) -> FsmContext:
        active = self.active_fault
        return FsmContext(
            state=self.state.name,
            display_state=self._display_state_for(self.state, active),
            time_in_state_s=self.time_in_state_s,
            outputs=expected_outputs_for_state(self.state),
            diagnostics=self.last_diagnostics,
            active_fault_code=active.code_text if active else None,
            active_fault_title=active.descriptor_title if active else None,
            active_fault_signal=active.signal if active else None,
            active_fault_value=active.value if active else None,
            active_fault_limit=active.limit if active else None,
            last_transition_reason=self.last_transition_reason,
            transition_counter=self.transition_counter,
            error_counter=self.error_counter,
            emergency_counter=self.emergency_counter,
            fault_counters=dict(self.fault_counters),
        )

    def get_metrics(self) -> FsmMetrics:
        return FsmMetrics(self.transition_counter, self.error_counter, self.emergency_counter, self.blocked_transition_counter, dict(self.fault_counters))
