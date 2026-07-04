from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrewRecipe:
    """Engineering-Rezept für AP4-Simulation und Terminalabnahme.

    Die Werte sind bewusst kurz gewählt, damit der gesamte Prozess im Terminal
    reproduzierbar getestet werden kann. In der realen Anlage werden die Werte
    durch Rezeptdaten bzw. Laborparameter ersetzt.
    """

    nachguss_min_duration_s: float = 120.0
    mashing_duration_s: float = 180.0
    transfer_to_k3_duration_s: float = 60.0
    lautering_duration_s: float = 120.0
    boiling_duration_s: float = 180.0
    transfer_to_k4_duration_s: float = 60.0
    fermentation_duration_s: float = 180.0

    min_k1_start_level_l: float = 10.0
    min_k2_mashing_level_l: float = 15.0
    min_k3_lautering_level_l: float = 10.0
    min_k4_fermentation_level_l: float = 10.0

    nachguss_temperature_min_c: float = 70.0
    nachguss_temperature_max_c: float = 82.0
    mashing_temperature_min_c: float = 62.0
    mashing_temperature_max_c: float = 76.0
    boiling_temperature_min_c: float = 98.0
    boiling_temperature_max_c: float = 102.0
    cooling_target_c: float = 25.0
    fermentation_temperature_min_c: float = 15.0
    fermentation_temperature_max_c: float = 22.0

    min_nachguss_flow_l_min: float = 0.5


DEFAULT_RECIPE = BrewRecipe()
