from __future__ import annotations

from enum import Enum


class BrewState(Enum):
    """Diskrete Zustände des AP4-Zustandsautomaten.

    Equipment-Zuordnung Version 5:
    - K1 = Nachgussbehälter
    - K2 = Maische-/Kochbehälter
    - K3 = Läuterbehälter
    - K4 = Gärbehälter

    Hinweis: ERROR und EMERGENCY bleiben steuerungstechnische Superzustände.
    Der konkrete Fehler wird über FaultCode/display_state ausgegeben.
    """

    IDLE = "idle"
    PRECHECK = "precheck"
    NACHGUSS = "nachguss"
    MASHING = "mashing"
    TRANSFER_TO_K3 = "transfer_to_k3"
    LAUTERING = "lautering"
    BOILING = "boiling"
    COOLING = "cooling"
    TRANSFER_TO_K4 = "transfer_to_k4"
    FERMENTING = "fermenting"
    FINISHED = "finished"
    ERROR = "error"
    EMERGENCY = "emergency"

    @property
    def is_production_state(self) -> bool:
        return self in {
            BrewState.NACHGUSS,
            BrewState.MASHING,
            BrewState.TRANSFER_TO_K3,
            BrewState.LAUTERING,
            BrewState.BOILING,
            BrewState.COOLING,
            BrewState.TRANSFER_TO_K4,
            BrewState.FERMENTING,
        }

    @property
    def is_fault_superstate(self) -> bool:
        return self in {BrewState.ERROR, BrewState.EMERGENCY}


NORMAL_SEQUENCE: tuple[BrewState, ...] = (
    BrewState.IDLE,
    BrewState.PRECHECK,
    BrewState.NACHGUSS,
    BrewState.MASHING,
    BrewState.TRANSFER_TO_K3,
    BrewState.LAUTERING,
    BrewState.BOILING,
    BrewState.COOLING,
    BrewState.TRANSFER_TO_K4,
    BrewState.FERMENTING,
    BrewState.FINISHED,
)

ALLOWED_NORMAL_TRANSITIONS: set[tuple[BrewState, BrewState]] = set(zip(NORMAL_SEQUENCE, NORMAL_SEQUENCE[1:]))

FORBIDDEN_DIRECT_TRANSITIONS: set[tuple[BrewState, BrewState]] = {
    (BrewState.BOILING, BrewState.MASHING),
    (BrewState.COOLING, BrewState.MASHING),
    (BrewState.FERMENTING, BrewState.BOILING),
    (BrewState.LAUTERING, BrewState.NACHGUSS),
    (BrewState.NACHGUSS, BrewState.BOILING),
}
