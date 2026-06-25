from __future__ import annotations

from diagnostics import Severity
from fsm import BrewStateMachine
from process_snapshot import ProcessSnapshot
from states import BrewState


def values(**overrides):
    data = {
        "aktueller_schritt": 0,
        "durchfluss_nachguss_maische": 1.0,
        "k1_fuellstand_voll": False,
        "k1_temperatur": 22.0,
        "k1_temperatur_sollwert_obere_grenze": 0.0,
        "k1_temperatur_sollwert_untere_grenze": 0.0,
        "k2_fuellstand": 10.0,
        "k2_fuellstand_voll": True,
        "k2_temperatur": 65.0,
        "k2_temperatur_sollwert_obere_grenze": 0.0,
        "k2_temperatur_sollwert_untere_grenze": 0.0,
        "k3_fuellstand": 20.0,
        "k3_temperatur": 70.0,
        "k3_temperatur_sollwert_obere_grenze": 0.0,
        "k3_temperatur_sollwert_untere_grenze": 0.0,
        "k3_maximaler_fuellstand": 50.0,
        "k3_minimaler_fuellstand": 6.0,
        "mobiler_sensor_temperatur": 20.0,
    }
    data.update(overrides)
    return data


def snap(**overrides):
    start = overrides.pop("start_requested", False)
    ack = overrides.pop("acknowledge", False)
    e_stop = overrides.pop("emergency_stop", False)
    return ProcessSnapshot.from_opc_values(values(**overrides), start_requested=start, acknowledge=ack, emergency_stop=e_stop)


def test_initial_state_idle():
    fsm = BrewStateMachine()
    assert fsm.state is BrewState.IDLE


def test_start_to_mashing_uses_k2_mash_vessel_from_excel_mapping():
    fsm = BrewStateMachine()
    result = fsm.update(snap(start_requested=True, k2_fuellstand=10, k2_fuellstand_voll = True , k2_temperatur=65.0), 0)
    assert result.old_state is BrewState.IDLE
    assert result.new_state is BrewState.MASHING
    assert result.reason == "start_conditions_ok"


def test_full_process_path():
    fsm = BrewStateMachine()

    # IDLE -> MASHING
    fsm.update(snap(start_requested=True, k2_temperatur=65.0), 0)
    assert fsm.state is BrewState.MASHING

    # MASHING -> LAUTERING
    fsm.update(snap(k2_temperatur=65.0), 3600)
    assert fsm.state is BrewState.LAUTERING

    # LAUTERING -> BOILING
    fsm.update(snap(durchfluss_nachguss_maische=1.0), 3600)
    assert fsm.state is BrewState.BOILING

    # BOILING -> COOLING
    fsm.update(snap(k2_temperatur=102.0), 3600)
    assert fsm.state is BrewState.COOLING

    # Noch nicht kalt genug: bleibt COOLING
    fsm.update(snap(mobiler_sensor_temperatur=29.0), 0)
    assert fsm.state is BrewState.COOLING

    # Kalt genug: COOLING -> FERMENTING
    fsm.update(snap(mobiler_sensor_temperatur=24.0), 0)
    assert fsm.state is BrewState.FERMENTING

    # FERMENTING -> FINISHED
    fsm.update(snap(mobiler_sensor_temperatur=20.0), 3600)
    assert fsm.state is BrewState.FINISHED


def test_estop_leads_to_emergency_and_ack_to_idle():
    fsm = BrewStateMachine()
    fsm.update(snap(start_requested=True), 0)
    result = fsm.update(snap(emergency_stop=True), 0)
    assert result.new_state is BrewState.EMERGENCY
    assert any(d.severity is Severity.EMERGENCY for d in result.diagnostics)

    result = fsm.update(snap(acknowledge=True), 0)
    assert result.new_state is BrewState.IDLE


def test_process_deviation_leads_to_error_not_emergency():
    fsm = BrewStateMachine()
    fsm.update(snap(start_requested=True, k2_temperatur=65.0), 0)
    result = fsm.update(snap(k2_temperatur=82.0), 0)
    assert result.new_state is BrewState.ERROR
    assert not any(d.severity is Severity.EMERGENCY for d in result.diagnostics)


def test_absolute_temperature_limit_leads_to_emergency():
    fsm = BrewStateMachine()
    fsm.update(snap(start_requested=True, k2_temperatur=65.0), 0)
    result = fsm.update(snap(k2_temperatur=121.0), 0)
    assert result.new_state is BrewState.EMERGENCY


def test_zero_excel_limits_are_ignored_and_recipe_limits_are_used():
    fsm = BrewStateMachine()
    result = fsm.update(snap(start_requested=True, k2_temperatur=65.0, k2_temperatur_sollwert_obere_grenze=0, k2_temperatur_sollwert_untere_grenze=0), 0)
    assert result.new_state is BrewState.MASHING