"""
File: test_ap4_integration.py
Work Package: tests
Responsible Engineer: Engineer D
Purpose: Verify AP4 can be driven entirely through AP5 (no competing FSM): a normal payload sequence progresses the FSM through its real states, using the approved mapping and the compressed demo recipe.
"""
from project.ap5.services.fsm_integration_service import FsmIntegrationService


def _values(step, **over):
    v = {
        "Aktueller_Schritt": step,
        "K1_Temperatur": 75.0,   # Nachguss in-window (70..82)
        "K1_Füllstand_OK": True,
        "K2_Temperatur": 66.0,   # Mash in-window (62..76)
        "K2_Füllstand": 12.0,
        "K3_Temperatur": 100.0,  # Boil in-window (98..102)
        "K3_Füllstand": 8.0,
        "MobilerSensor_Temperatur": 18.0,  # Ferment in-window (15..22)
        "Durchfluss_NachgussMaische": 1.0,
        "emergency_stop": False,
        "sensor_ok": True,
        "acknowledge": False,
    }
    v.update(over)
    return v


def test_normal_sequence_progresses_through_ap4_states():
    # Step 9 opens all derived actuators; AP4 then advances purely on the
    # measured values + the compressed demo durations.
    svc = FsmIntegrationService(demo_mode=True)
    assert svc.current_state == "IDLE"

    visited = ["IDLE"]
    for _ in range(700):
        svc.update(_values(step=9, start_requested=True), dt_s=1.0)
        if svc.current_state != visited[-1]:
            visited.append(svc.current_state)

    # AP4 (driven only through AP5) must walk the real normal sequence.
    expected_order = ["IDLE", "PRECHECK", "NACHGUSS", "MASHING", "LAUTERING", "BOILING"]
    positions = [visited.index(s) for s in expected_order if s in visited]
    assert all(s in visited for s in expected_order), visited
    assert positions == sorted(positions), visited


def test_emergency_stop_takes_priority():
    svc = FsmIntegrationService(demo_mode=True)
    svc.update(_values(2), dt_s=1.0)
    result = svc.update(_values(3, emergency_stop=True), dt_s=1.0)
    assert result.state == "EMERGENCY"
    assert result.active_fault_code is not None
    assert any(a.severity == "CRITICAL" for a in result.alarms)
