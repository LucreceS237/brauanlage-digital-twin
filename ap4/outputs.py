from __future__ import annotations

from .fsm_contract import ExpectedOutputs
from .states import BrewState


def expected_outputs_for_state(state: BrewState) -> ExpectedOutputs:
    """Soll-Aktorik pro Zustand für AP5-Plausibilisierung und AP6-Dashboard."""
    if state == BrewState.NACHGUSS:
        return ExpectedOutputs(v3_open=True)
    if state == BrewState.MASHING:
        return ExpectedOutputs(heater_k2_on=True, agitator_on=True)
    if state == BrewState.TRANSFER_TO_K3:
        return ExpectedOutputs(v4_open=True)
    if state == BrewState.BOILING:
        return ExpectedOutputs(heater_k2_on=True)
    if state == BrewState.TRANSFER_TO_K4:
        return ExpectedOutputs(v5_open=True, pump_on=True)
    return ExpectedOutputs()
