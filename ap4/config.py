from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringLimits:
    """Rezeptunabhängige Schutz- und Plausibilitätsgrenzen."""

    absolute_min_temperature_c: float = -5.0
    absolute_max_temperature_c: float = 120.0
    min_level_l: float = 0.0
    max_level_l: float = 100.0
    max_missing_value_age_s: float = 10.0
    max_dt_s: float = 300.0
    max_signal_age_s: float = 5.0


LIMITS = EngineeringLimits()
