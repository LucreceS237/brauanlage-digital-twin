"""
File: recipe.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: recipe.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrewRecipe:
    """Rezept- und Prozessparameter für AP4.

    Die Werte sind Engineering-Arbeitswerte. Für die reale Laboranlage müssen
    endgültige Rezeptparameter und empirisch validierte Grenzwerte ergänzt werden.
    """

    nachguss_min_duration_s: float = 60.0
    mashing_duration_s: float = 60.0 * 45.0
    lautering_duration_s: float = 60.0 * 20.0
    boiling_duration_s: float = 60.0 * 30.0
    transfer_to_k4_duration_s: float = 60.0 * 5.0
    fermentation_duration_s: float = 60.0 * 60.0 * 24.0 * 5.0

    min_k3_start_level_l: float = 5.0
    min_k1_mashing_level_l: float = 3.0
    min_k2_boiling_level_l: float = 3.0
    min_k4_fermentation_level_l: float = 2.0

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
    min_transfer_flow_l_min: float = 0.5


DEFAULT_RECIPE = BrewRecipe()
