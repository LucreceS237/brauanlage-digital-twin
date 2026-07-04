"""
File: outputs.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: outputs.
"""
from __future__ import annotations

from .fsm_contract import ExpectedOutputs
from .states import BrewState


def expected_outputs_for_state(state: BrewState) -> ExpectedOutputs:
    if state == BrewState.NACHGUSS:
        return ExpectedOutputs(v3_open=True)
    if state == BrewState.MASHING:
        return ExpectedOutputs(heater_k1_on=True, agitator_on=True)
    if state == BrewState.LAUTERING:
        return ExpectedOutputs(v4_open=True)
    if state == BrewState.BOILING:
        return ExpectedOutputs(heater_k2_on=True)
    if state == BrewState.TRANSFER_TO_K4:
        return ExpectedOutputs(v5_open=True, pump_on=True)
    return ExpectedOutputs()
