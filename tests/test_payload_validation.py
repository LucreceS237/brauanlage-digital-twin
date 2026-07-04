"""
File: test_payload_validation.py
Work Package: tests
Responsible Engineer: Engineer D
Purpose: MQTT payload validation and AP2 publisher contract.
"""
from project.ap3.mqtt.payload_validator import validate_payload
from project.shared.simulation import ProcessSimulator


def _valid_payload():
    return {
        "timestamp": "2026-07-01T12:00:00Z",
        "source": "REAL_SPS",
        "publisherMode": "REAL",
        "connectionStatus": "CONNECTED",
        "simulationPhase": "LIVE",
        "spsEndpoint": "opc.tcp://192.168.0.1:4840",
        "values": {
            "Aktueller_Schritt": 3,
            "K1_Temperatur": 55.0,
            "K1_Füllstand_OK": True,
            "K2_Temperatur": 65.2,
            "Durchfluss_NachgussMaische": 0.7,
            "emergency_stop": False,
            "sensor_ok": True,
            "acknowledge": False,
        },
    }


def test_valid_payload_passes():
    ok, reason = validate_payload(_valid_payload())
    assert ok is True and reason is None


def test_rejects_missing_publisher_mode():
    p = _valid_payload()
    del p["publisherMode"]
    ok, _ = validate_payload(p)
    assert ok is False


def test_rejects_wrong_bool_type():
    p = _valid_payload()
    p["values"]["emergency_stop"] = "yes"
    ok, _ = validate_payload(p)
    assert ok is False


def test_fake_publisher_payload_matches_backend_contract():
    sim = ProcessSimulator(speed_factor=50.0)
    for _ in range(30):
        payload = sim.next_payload(source="Fake_SPS", publisher_mode="FAKE")
        ok, reason = validate_payload(payload)
        assert ok is True, f"fake payload rejected: {reason}"
        sim.advance(1.0)
