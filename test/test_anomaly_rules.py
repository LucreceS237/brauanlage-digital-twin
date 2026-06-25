# test/test_anomaly_rules.py

"""
===========================================================
TESTS FOR ANOMALY DETECTION RULES
===========================================================

These tests verify that the anomaly detection module behaves
correctly using simulated SPS snapshots.

Why do we use mock data?
------------------------
The real SPS is not always available during development.
Mock snapshots allow us to test the logic independently from
the physical brewing system.
"""

from datetime import datetime, timedelta, timezone

from src.anomaly_detection.detector import AnomalyDetector


def make_timestamp(seconds_offset: int = 0) -> str:
    """
    Create UTC timestamps for test snapshots.
    """

    return (
        datetime.now(timezone.utc) + timedelta(seconds=seconds_offset)
    ).isoformat()


def base_snapshot():
    now = make_timestamp()

    return {
        "_received_at": now,
        "state": "MASHING",

        "K1_Temperatur": 70.0,
        "K1_Temperatur_SollwertUntereGrenze": 60.0,
        "K1_Temperatur_SollwertObereGrenze": 80.0,

        "K2_Temperatur": 68.0,
        "K2_Temperatur_SollwertUntereGrenze": 62.0,
        "K2_Temperatur_SollwertObereGrenze": 78.0,

        "K3_Temperatur": 70.0,
        "K3_Temperatur_SollwertUntereGrenze": 60.0,
        "K3_Temperatur_SollwertObereGrenze": 90.0,

        "MobilerSensor_Temperatur": 18.0,
        "Durchfluss_NachgussMaische": 0.0,

        "_meta": {
            "K1_Temperatur": {"timestamp": now, "quality": "Good"},
            "K2_Temperatur": {"timestamp": now, "quality": "Good"},
            "K3_Temperatur": {"timestamp": now, "quality": "Good"},
            "MobilerSensor_Temperatur": {"timestamp": now, "quality": "Good"},
            "Durchfluss_NachgussMaische": {"timestamp": now, "quality": "Good"},
        },
    }

def get_alarm_codes(alarms):
    """
    Helper function to extract alarm codes from detector output.
    """

    return [alarm["code"] for alarm in alarms]


def test_no_alarm_for_normal_snapshot():
    detector = AnomalyDetector()

    snapshot = base_snapshot()
    print("\nSNAPSHOT KEYS:", snapshot.keys())

    alarms = detector.update(snapshot)

    print("\nALARMS:")
    for alarm in alarms:
        print(alarm)

    assert alarms == []


def test_temperature_too_high_alarm():
    """
    If K2 temperature exceeds the upper limit,
    TEMP_TOO_HIGH should be detected.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["K2_Temperatur"] = 85.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    assert "TEMP_TOO_HIGH" in codes


def test_temperature_too_low_alarm():
    """
    If K2 temperature is below the lower limit,
    TEMP_TOO_LOW should be detected.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["K2_Temperatur"] = 50.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    assert "TEMP_TOO_LOW" in codes


def test_low_flow_during_lautering():
    """
    During LAUTERING, flow must be at least 0.5 l/min.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["state"] = "LAUTERING"
    snapshot["Durchfluss_NachgussMaische"] = 0.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    assert "LOW_FLOW_DURING_LAUTERING" in codes


def test_unexpected_flow_in_idle():
    """
    If the system is IDLE, flow should normally be zero.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["state"] = "IDLE"
    snapshot["Durchfluss_NachgussMaische"] = 1.2

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    assert "UNEXPECTED_FLOW_IN_IDLE" in codes


def test_invalid_sensor_value():
    """
    A physically impossible temperature value should create
    a SENSOR_VALUE_INVALID alarm.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["K2_Temperatur"] = 999.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    assert "SENSOR_VALUE_INVALID" in codes


def test_data_stale_alarm():
    """
    If a measurement timestamp is too old,
    DATA_STALE should be detected.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    old_timestamp = make_timestamp(seconds_offset=-10)

    snapshot["_meta"]["K2_Temperatur"]["timestamp"] = old_timestamp

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    assert "DATA_STALE" in codes


def test_temperature_rise_too_fast():
    """
    Test trend-based anomaly detection.

    The SPS delivers values every second. Therefore we simulate
    61 snapshots so that the detector has enough history for a
    60-second window.

    If K2 temperature rises from 60°C to 70°C in 60 seconds,
    the ramp rate is 10°C/min.

    Since the default limit is 5°C/min, this should trigger
    TEMP_RISE_TOO_FAST.
    """

    detector = AnomalyDetector(history_seconds=120)

    start_time = datetime.now(timezone.utc)

    for second in range(61):
        snapshot = base_snapshot()

        timestamp = (start_time + timedelta(seconds=second)).isoformat()

        snapshot["_received_at"] = timestamp
        snapshot["_meta"]["K2_Temperatur"]["timestamp"] = timestamp

        # Linear temperature increase:
        # second 0  -> 60°C
        # second 60 -> 70°C
        snapshot["K2_Temperatur"] = 60.0 + (10.0 / 60.0) * second

        alarms = detector.update(snapshot)

    codes = get_alarm_codes(alarms)

    assert "TEMP_RISE_TOO_FAST" in codes