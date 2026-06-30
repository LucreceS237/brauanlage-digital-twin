from __future__ import annotations

from .config import EngineeringLimits, LIMITS
from .diagnostics import Diagnostic, Severity, make_diagnostic
from .fault_catalog import FaultCode
from .process_snapshot import ProcessSnapshot
from .recipe import BrewRecipe, DEFAULT_RECIPE
from .states import BrewState


class ProcessMonitor:
    """Zustandsabhängige Prozessüberwachung für eindeutige ERROR-Codes."""

    def __init__(self, recipe: BrewRecipe = DEFAULT_RECIPE, limits: EngineeringLimits = LIMITS) -> None:
        self.recipe = recipe
        self.limits = limits

    def evaluate(self, state: BrewState, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        if state in {BrewState.IDLE, BrewState.PRECHECK, BrewState.FINISHED, BrewState.ERROR, BrewState.EMERGENCY}:
            return []
        checks = {
            BrewState.NACHGUSS: self._check_nachguss,
            BrewState.MASHING: self._check_mashing,
            BrewState.LAUTERING: self._check_lautering,
            BrewState.BOILING: self._check_boiling,
            BrewState.COOLING: self._check_cooling,
            BrewState.TRANSFER_TO_K4: self._check_transfer_to_k4,
            BrewState.FERMENTING: self._check_fermenting,
        }
        return checks.get(state, lambda _s: [])(snapshot)

    def _temperature_window(self, signal: str, value: float, minimum: float, maximum: float, low_code: FaultCode, high_code: FaultCode) -> list[Diagnostic]:
        tol = self.limits.process_temperature_tolerance_c
        if value < minimum - tol:
            return [make_diagnostic(Severity.ERROR, low_code, signal, value, minimum)]
        if value > maximum + tol:
            return [make_diagnostic(Severity.ERROR, high_code, signal, value, maximum)]
        return []

    def _check_nachguss(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        if not snapshot.v3_open:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS, "v3_open", False, True))
        if snapshot.flow_k3_to_k1_l_min < self.recipe.min_nachguss_flow_l_min:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_004_FLOW_K3_TO_K1_LOW, "flow_k3_to_k1_l_min", snapshot.flow_k3_to_k1_l_min, self.recipe.min_nachguss_flow_l_min))
        diagnostics.extend(self._temperature_window("k3_temperature_c", snapshot.k3_temperature_c, self.recipe.nachguss_temperature_min_c, self.recipe.nachguss_temperature_max_c, FaultCode.ERROR_001_K3_NACHGUSS_TEMP_LOW, FaultCode.ERROR_002_K3_NACHGUSS_TEMP_HIGH))
        return diagnostics

    def _check_mashing(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        diagnostics = self._temperature_window("k1_temperature_c", snapshot.k1_temperature_c, self.recipe.mashing_temperature_min_c, self.recipe.mashing_temperature_max_c, FaultCode.ERROR_005_K1_MASHING_TEMP_LOW, FaultCode.ERROR_006_K1_MASHING_TEMP_HIGH)
        if snapshot.k1_level_l < self.recipe.min_k1_mashing_level_l:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_007_K1_LEVEL_LOW_MASHING, "k1_level_l", snapshot.k1_level_l, self.recipe.min_k1_mashing_level_l))
        return diagnostics

    def _check_lautering(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        if not snapshot.v4_open:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_008_V4_CLOSED_IN_LAUTERING, "v4_open", False, True))
        if snapshot.flow_k1_to_k2_l_min < self.recipe.min_transfer_flow_l_min:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_009_FLOW_K1_TO_K2_LOW, "flow_k1_to_k2_l_min", snapshot.flow_k1_to_k2_l_min, self.recipe.min_transfer_flow_l_min))
        return diagnostics

    def _check_boiling(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        diagnostics = self._temperature_window("k2_temperature_c", snapshot.k2_temperature_c, self.recipe.boiling_temperature_min_c, self.recipe.boiling_temperature_max_c, FaultCode.ERROR_010_K2_BOILING_TEMP_LOW, FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH)
        if snapshot.k2_level_l < self.recipe.min_k2_boiling_level_l:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_012_K2_LEVEL_LOW_BOILING, "k2_level_l", snapshot.k2_level_l, self.recipe.min_k2_boiling_level_l))
        return diagnostics

    def _check_cooling(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        if snapshot.k2_temperature_c > self.recipe.boiling_temperature_max_c + self.limits.process_temperature_tolerance_c:
            return [make_diagnostic(Severity.ERROR, FaultCode.ERROR_013_COOLING_TEMP_IMPLAUSIBLE, "k2_temperature_c", snapshot.k2_temperature_c, self.recipe.cooling_target_c)]
        return []

    def _check_transfer_to_k4(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        if not snapshot.v5_open:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_014_V5_CLOSED_TRANSFER_K4, "v5_open", False, True))
        if not snapshot.pump_on_feedback:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4, "pump_on_feedback", False, True))
        if snapshot.flow_k2_to_k4_l_min < self.recipe.min_transfer_flow_l_min:
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_016_FLOW_K2_TO_K4_LOW, "flow_k2_to_k4_l_min", snapshot.flow_k2_to_k4_l_min, self.recipe.min_transfer_flow_l_min))
        return diagnostics

    def _check_fermenting(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        return self._temperature_window("k4_temperature_c", snapshot.k4_temperature_c, self.recipe.fermentation_temperature_min_c, self.recipe.fermentation_temperature_max_c, FaultCode.ERROR_017_K4_FERMENT_TEMP_LOW, FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH)
