"""
File: config.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: config.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringLimits:
    """Rezeptunabhängige Schutz- und Plausibilitätsgrenzen."""

    absolute_min_temperature_c: float = -5.0
    absolute_max_temperature_c: float = 120.0
    max_level_l: float = 100.0
    min_level_l: float = 0.0
    max_missing_value_age_s: float = 10.0
    min_flow_l_min: float = 0.5
    process_temperature_tolerance_c: float = 5.0
    terminal_temperature_tolerance_c: float = 2.0
    max_dt_s: float = 300.0


LIMITS = EngineeringLimits()
DEFAULT_NODE_XLSX = "OPCUA_Knotenpunktliste_final.xlsx"
