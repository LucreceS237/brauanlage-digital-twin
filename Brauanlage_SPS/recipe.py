from __future__ import annotations

from dataclasses import dataclass

from states import BrewState


@dataclass(frozen=True)
class StateSetpoints:
    """Sollwerte und Schrittzeiten je Prozessphase.

    temperature_min/temperature_max sind Prozessgrenzen für ERROR.
    absolute Safety-Grenzen liegen in config.EngineeringLimits.
    """

    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    duration_s: float | None = None
    cooling_target_c: float | None = None


Recipe = dict[BrewState, StateSetpoints]


DEFAULT_RECIPE: Recipe = {
    BrewState.IDLE: StateSetpoints(),
    BrewState.MASHING: StateSetpoints(temperature_min_c=62.0, temperature_max_c=76.0, duration_s=3600),
    BrewState.LAUTERING: StateSetpoints(duration_s=3600),
    BrewState.BOILING: StateSetpoints(temperature_min_c=98.0, temperature_max_c=102.0, duration_s=3600),
    BrewState.COOLING: StateSetpoints(cooling_target_c=25.0),
    BrewState.FERMENTING: StateSetpoints(temperature_min_c=15.0, temperature_max_c=22.0, duration_s=3600),
    BrewState.FINISHED: StateSetpoints(),
    BrewState.ERROR: StateSetpoints(),
    BrewState.EMERGENCY: StateSetpoints(),
}