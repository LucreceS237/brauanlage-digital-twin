from __future__ import annotations

import logging
from dataclasses import dataclass

from diagnostics import Diagnostic, Severity
from monitor import ProcessMonitor
from outputs import ExpectedOutputs, outputs_for_state
from process_snapshot import ProcessSnapshot
from recipe import DEFAULT_RECIPE, Recipe, StateSetpoints
from safety import SafetySystem
from states import BrewState
from config import LIMITS

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransitionResult:
    old_state: BrewState
    new_state: BrewState
    reason: str | None
    diagnostics: list[Diagnostic]


class BrewStateMachine:
    """Zustandsautomat des Brauprozesses.

    Designentscheidungen:
    - SafetySystem ist injiziert und entscheidet EMERGENCY.
    - ProcessMonitor ist injiziert und entscheidet ERROR.
    - OPC-UA wird nicht direkt in der FSM gelesen. Die FSM bekommt nur einen
      normierten ProcessSnapshot. Das folgt Single Responsibility und DIP.
    """

    def __init__(
        self,
        recipe: Recipe | None = None,
        safety: SafetySystem | None = None,
        monitor: ProcessMonitor | None = None,
    ) -> None:
        self.state = BrewState.IDLE
        self.recipe = recipe or DEFAULT_RECIPE
        self.safety = safety or SafetySystem()
        self.monitor = monitor or ProcessMonitor()
        self.time_in_state_s = 0.0
        self.last_transition_reason: str | None = None
        self.last_diagnostics: list[Diagnostic] = []

    @property
    def setpoints(self) -> StateSetpoints:
        return self.recipe.get(self.state, StateSetpoints())

    @property
    def outputs(self) -> ExpectedOutputs:
        return outputs_for_state(self.state)

    def update(self, snapshot: ProcessSnapshot, dt_s: float = 1.0) -> TransitionResult:
        if dt_s < 0:
            raise ValueError("dt_s darf nicht negativ sein")

        old_state = self.state
        self.last_transition_reason = None
        self.last_diagnostics = []

        # 1) Safety dominiert immer.
        safety_diags = self.safety.evaluate(snapshot)
        self.last_diagnostics.extend(safety_diags)
        if any(d.severity is Severity.EMERGENCY for d in safety_diags):
            self._transition(BrewState.EMERGENCY, "safety_emergency")
            return self._result(old_state)

        # 2) Emergency verlassen nur nach Quittierung und ohne aktive Safety-Störung.
        if self.state is BrewState.EMERGENCY:
            if snapshot.acknowledge:
                self._transition(BrewState.IDLE, "emergency_acknowledged")
            return self._result(old_state)

        # 3) Prozessüberwachung: Soll/Ist-Fehler führen zu ERROR, nicht direkt EMERGENCY.
        monitor_diags = self.monitor.evaluate(self.state, snapshot, self.setpoints)
        self.last_diagnostics.extend(monitor_diags)
        if any(d.severity is Severity.ERROR for d in monitor_diags):
            self._transition(BrewState.ERROR, "process_monitor_error")
            return self._result(old_state)

        # 4) Error verlassen nur nach Quittierung und störungsfreiem Zustand.
        if self.state is BrewState.ERROR:
            if snapshot.acknowledge:
                self._transition(BrewState.IDLE, "error_acknowledged")
            return self._result(old_state)

        # 5) Normale Schrittlogik.
        self.time_in_state_s += dt_s
        self._normal_process_step(snapshot)
        return self._result(old_state)

    def _normal_process_step(self, snapshot: ProcessSnapshot) -> None:
        sp = self.setpoints
        t = self.time_in_state_s

        if self.state is BrewState.IDLE:
            if self._can_start(snapshot):
                self._transition(BrewState.MASHING, "start_conditions_ok")

        elif self.state is BrewState.MASHING:
            if self._duration_finished(t, sp) and self._mash_temperature_reached(snapshot, sp):
                self._transition(BrewState.LAUTERING, "mashing_finished")

        elif self.state is BrewState.LAUTERING:
            if self._duration_finished(t, sp) and snapshot.durchfluss_nachguss_maische >= LIMITS.min_lautering_flow_l_min:
                self._transition(BrewState.BOILING, "lautering_finished")

        elif self.state is BrewState.BOILING:
            if self._duration_finished(t, sp):
                self._transition(BrewState.COOLING, "boiling_finished")

        elif self.state is BrewState.COOLING:
            if sp.cooling_target_c is not None and snapshot.fermenting_temperature <= sp.cooling_target_c:
                self._transition(BrewState.FERMENTING, "cooling_finished")

        elif self.state is BrewState.FERMENTING:
            if self._duration_finished(t, sp):
                self._transition(BrewState.FINISHED, "fermentation_finished")

    def _transition(self, new_state: BrewState, reason: str) -> None:
        if new_state is not self.state:
            log.info("%s -> %s | Grund=%s", self.state.value, new_state.value, reason)
            self.state = new_state
            self.time_in_state_s = 0.0
            self.last_transition_reason = reason

    def _result(self, old_state: BrewState) -> TransitionResult:
        return TransitionResult(old_state, self.state, self.last_transition_reason, list(self.last_diagnostics))

    @staticmethod
    def _duration_finished(time_in_state_s: float, sp: StateSetpoints) -> bool:
        return sp.duration_s is not None and time_in_state_s >= sp.duration_s

    @staticmethod
    def _mash_temperature_reached(snapshot: ProcessSnapshot, sp: StateSetpoints) -> bool:
        return sp.temperature_min_c is None or snapshot.mash_temperature >= sp.temperature_min_c

    @staticmethod
    def _can_start(snapshot: ProcessSnapshot) -> bool:
        # Excel: K2 = Maischebehälter. Start ist erlaubt, wenn Bedienerstart
        # vorhanden und K2 plausibel gefüllt ist. Falls Literwert nicht sinnvoll
        # skaliert ist, genügt alternativ das boolesche Vollsignal.
        return snapshot.start_requested and (
            snapshot.k2_fuellstand >= LIMITS.min_start_level_l or snapshot.k2_fuellstand_voll
        )