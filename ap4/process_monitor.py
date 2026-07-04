from __future__ import annotations

from .diagnostics import Diagnostic, Severity, make_diagnostic
from .fault_catalog import FaultCode
from .process_snapshot import ProcessSnapshot
from .recipe import BrewRecipe, DEFAULT_RECIPE
from .states import BrewState


class ProcessMonitor:
    """Prozess- und Guard-Prüfung mit eindeutigen ERROR-Codes."""

    def __init__(self, recipe: BrewRecipe = DEFAULT_RECIPE) -> None:
        self.recipe = recipe

    def evaluate(self, state: BrewState, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        r = self.recipe
        diagnostics: list[Diagnostic] = []
        if snapshot.data_quality.upper() != "GOOD":
            diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_021_DATA_QUALITY_BAD, "data_quality", snapshot.data_quality, "GOOD"))
            return diagnostics

        if state == BrewState.NACHGUSS:
            if snapshot.k1_temperature_c < r.nachguss_temperature_min_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_001_K1_NACHGUSS_TEMP_LOW, "k1_temperature_c", snapshot.k1_temperature_c, r.nachguss_temperature_min_c))
            if snapshot.k1_temperature_c > r.nachguss_temperature_max_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_002_K1_NACHGUSS_TEMP_HIGH, "k1_temperature_c", snapshot.k1_temperature_c, r.nachguss_temperature_max_c))
            if not snapshot.v3_open:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS, "v3_open", False, True))
            if snapshot.durchfluss_k1_k2_l_min < r.min_nachguss_flow_l_min:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_004_FLOW_K1_TO_K2_LOW, "durchfluss_k1_k2_l_min", snapshot.durchfluss_k1_k2_l_min, r.min_nachguss_flow_l_min))

        elif state == BrewState.MASHING:
            if snapshot.k2_level_l < r.min_k2_mashing_level_l:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_007_K2_LEVEL_LOW_MASHING, "k2_level_l", snapshot.k2_level_l, r.min_k2_mashing_level_l))
            if snapshot.k2_temperature_c < r.mashing_temperature_min_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_005_K2_MASHING_TEMP_LOW, "k2_temperature_c", snapshot.k2_temperature_c, r.mashing_temperature_min_c))
            if snapshot.k2_temperature_c > r.mashing_temperature_max_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_006_K2_MASHING_TEMP_HIGH, "k2_temperature_c", snapshot.k2_temperature_c, r.mashing_temperature_max_c))

        elif state == BrewState.TRANSFER_TO_K3:
            if not snapshot.v4_open:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_008_V4_CLOSED_TRANSFER_K3, "v4_open", False, True))

        elif state == BrewState.LAUTERING:
            if snapshot.k3_level_l < r.min_k3_lautering_level_l:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_009_K3_LEVEL_LOW_LAUTERING, "k3_level_l", snapshot.k3_level_l, r.min_k3_lautering_level_l))

        elif state == BrewState.BOILING:
            if snapshot.k2_level_l < r.min_k2_mashing_level_l:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_012_K2_LEVEL_LOW_BOILING, "k2_level_l", snapshot.k2_level_l, r.min_k2_mashing_level_l))
            if snapshot.k2_temperature_c < r.boiling_temperature_min_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_010_K2_BOILING_TEMP_LOW, "k2_temperature_c", snapshot.k2_temperature_c, r.boiling_temperature_min_c))
            if snapshot.k2_temperature_c > r.boiling_temperature_max_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH, "k2_temperature_c", snapshot.k2_temperature_c, r.boiling_temperature_max_c))

        elif state == BrewState.COOLING:
            # Kein sofortiger ERROR nur weil Kühlung noch läuft. ERROR erst wenn Prozess
            # extern diese Abweichung prüft oder Zeitlimit ergänzt wird.
            pass

        elif state == BrewState.TRANSFER_TO_K4:
            if not snapshot.v5_open:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_014_V5_CLOSED_TRANSFER_K4, "v5_open", False, True))
            if not snapshot.pump_on:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4, "pump_on", False, True))

        elif state == BrewState.FERMENTING:
            if snapshot.k4_level_l < r.min_k4_fermentation_level_l:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_016_K4_LEVEL_LOW_TRANSFER, "k4_level_l", snapshot.k4_level_l, r.min_k4_fermentation_level_l))
            if snapshot.k4_temperature_c < r.fermentation_temperature_min_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_017_K4_FERMENT_TEMP_LOW, "k4_temperature_c", snapshot.k4_temperature_c, r.fermentation_temperature_min_c))
            if snapshot.k4_temperature_c > r.fermentation_temperature_max_c:
                diagnostics.append(make_diagnostic(Severity.ERROR, FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH, "k4_temperature_c", snapshot.k4_temperature_c, r.fermentation_temperature_max_c))
        return diagnostics
