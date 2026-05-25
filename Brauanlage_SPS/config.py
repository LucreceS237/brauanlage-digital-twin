from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringLimits:
    """Feste, rezeptunabhängige Schutzgrenzen.

    Diese Grenzen sind bewusst konservativ. Prozessabweichungen führen nicht
    automatisch zu EMERGENCY, sondern zunächst zu ERROR. EMERGENCY ist für
    echte Gefährdungen reserviert: Not-Aus, unplausible Messwerte, Überlauf,
    Trockenlauf oder extrem gefährliche Temperaturen.
    """

    absolute_min_temperature_c: float = -5.0
    absolute_max_temperature_c: float = 120.0
    process_temperature_tolerance_c: float = 5.0
    min_start_level_l: float = 1.0
    min_lautering_flow_l_min: float = 0.5
    max_missing_value_age_s: float = 10.0


LIMITS = EngineeringLimits()

# Default-Dateiname der von AP1 gelieferten Knotenliste.
DEFAULT_NODE_XLSX = "OPCUA_Knotenpunktliste_final.xlsx"