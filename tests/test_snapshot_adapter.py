"""
File: test_snapshot_adapter.py
Work Package: tests
Responsible Engineer: Engineer D
Purpose: Verify the approved K1-K4 vessel mapping is respected when converting an MQTT payload into an AP4 ProcessSnapshot (the rotation in mapping.py), and that the step-derived actuator signals let AP4 progress.
"""
from project.ap5.adapters.snapshot_adapter import build_snapshot


def _values(**over):
    v = {
        "Aktueller_Schritt": 4,
        "K1_Temperatur": 75.0,   # Nachguss
        "K1_Füllstand_OK": True,
        "K2_Temperatur": 65.0,   # Maische
        "K2_Füllstand": 12.0,
        "K3_Temperatur": 99.0,   # Läuter/Boil
        "K3_Füllstand": 8.0,
        "MobilerSensor_Temperatur": 18.0,  # Gär
        "Durchfluss_NachgussMaische": 0.9,
        "emergency_stop": False,
        "sensor_ok": True,
        "acknowledge": False,
    }
    v.update(over)
    return v


def test_temperature_rotation_matches_approved_mapping():
    snap = build_snapshot(_values())
    # K1 Nachguss -> AP4 k3 (nachguss role)
    assert snap.k3_temperature_c == 75.0
    # K2 Maische -> AP4 k1 (mash role)
    assert snap.k1_temperature_c == 65.0
    # K3 Läuter/Boil -> AP4 k2 (lauter/boil role)
    assert snap.k2_temperature_c == 99.0
    # K4 Gär (MobilerSensor) -> AP4 k4
    assert snap.k4_temperature_c == 18.0


def test_level_and_flow_rotation():
    snap = build_snapshot(_values())
    assert snap.k1_level_l == 12.0            # K2_Füllstand -> mash level
    assert snap.k2_level_l == 8.0             # K3_Füllstand -> lauter level
    assert snap.flow_k3_to_k1_l_min == 0.9    # Durchfluss Nachguss->Maische
    assert snap.k3_level_l == 10.0            # derived from K1_Füllstand_OK


def test_safety_flags_pass_through():
    snap = build_snapshot(_values(emergency_stop=True, sensor_ok=False))
    assert snap.emergency_stop is True
    assert snap.sensor_ok is False


def test_actuators_derived_from_step():
    early = build_snapshot(_values(Aktueller_Schritt=2))
    assert early.start_requested is True
    assert early.v3_open is False
    late = build_snapshot(_values(Aktueller_Schritt=8))
    assert late.v5_open is True
    assert late.pump_on_feedback is True
    assert late.flow_k2_to_k4_l_min >= 0.5
