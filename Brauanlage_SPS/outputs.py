from __future__ import annotations

from dataclasses import dataclass

from states import BrewState


@dataclass(frozen=True)
class ExpectedOutputs:
    """Erwartete Aktorzustände pro FSM-Zustand.

    Wichtig: Die Excel-Liste kennzeichnet Pumpe/Ventile als read-only
    SPS-Ausgangsstatus. Dieses Projekt schreibt deshalb nicht aktiv auf die SPS,
    sondern nutzt die erwarteten Ausgänge für Anzeige, Plausibilisierung und API.
    """

    heater_on: bool = False
    pump_on: bool = False
    valve_3_open: bool = False
    valve_4_open: bool = False
    valve_5_open: bool = False
    agitator_on: bool = False


STATE_OUTPUTS: dict[BrewState, ExpectedOutputs] = {
    BrewState.IDLE: ExpectedOutputs(),
    BrewState.MASHING: ExpectedOutputs(heater_on=True, agitator_on=True),
    BrewState.LAUTERING: ExpectedOutputs(pump_on=True, valve_4_open=True),
    BrewState.BOILING: ExpectedOutputs(heater_on=True),
    BrewState.COOLING: ExpectedOutputs(),
    BrewState.FERMENTING: ExpectedOutputs(),
    BrewState.FINISHED: ExpectedOutputs(),
    BrewState.ERROR: ExpectedOutputs(),
    BrewState.EMERGENCY: ExpectedOutputs(),
}


def outputs_for_state(state: BrewState) -> ExpectedOutputs:
    return STATE_OUTPUTS.get(state, ExpectedOutputs()) 