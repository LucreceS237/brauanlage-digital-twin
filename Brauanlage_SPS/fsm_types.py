# fsm_types.py – gemeinsame Typ-Aliase (nicht „types“ – Kollision mit Stdlib)
from typing import TypeAlias

from states import BrewState

StateTransition: TypeAlias = tuple[BrewState, BrewState]
