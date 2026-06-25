from __future__ import annotations

from enum import Enum


class BrewState(Enum):
    """Diskrete Prozesszustände der Labor-Brauanlage."""

    IDLE = "idle"
    MASHING = "mashing"
    LAUTERING = "lautering"
    BOILING = "boiling"
    COOLING = "cooling"
    FERMENTING = "fermenting"
    FINISHED = "finished"
    ERROR = "error"
    EMERGENCY = "emergency"