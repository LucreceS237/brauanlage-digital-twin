"""
File: states.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: states.
"""
from __future__ import annotations

from enum import Enum


class BrewState(Enum):
    """Diskrete Superzustände des AP4-Zustandsautomaten.

    Version 4 nutzt bewusst eine zweistufige Fehlerarchitektur:
    - `BrewState.ERROR` und `BrewState.EMERGENCY` bleiben steuerungstechnische
      Superzustände. Dadurch bleibt die FSM stabil und beherrschbar.
    - Der konkrete Fehler wird über `FaultCode` und `FsmContext.display_state`
      abgebildet, z. B. `ERROR_005_K1_MASHING_TEMP_LOW`.
    """

    IDLE = "idle"
    PRECHECK = "precheck"
    NACHGUSS = "nachguss"
    MASHING = "mashing"
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
}
