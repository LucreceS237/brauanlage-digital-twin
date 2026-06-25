from datetime import datetime, timedelta, timezone
from pprint import pprint

from src.anomaly_detection.detector import AnomalyDetector


# ============================================================
# Helper functions
# ============================================================

def make_timestamp(seconds_offset: int = 0) -> str:
    """
    Creates an ISO timestamp.

    seconds_offset = 0      -> current time
    seconds_offset = -10    -> 10 seconds in the past
    seconds_offset = +10    -> 10 seconds in the future
    """

    return (datetime.now(timezone.utc) + timedelta(seconds=seconds_offset)).isoformat()


def base_snapshot():
    """
    Base snapshot representing a normal process situation.

    This is the default input used by most tests.
    Each test modifies only the variable needed for its scenario.
    """

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
    Extracts only the alarm codes from the detector output.
    """

    return [alarm["code"] for alarm in alarms]


def print_test_report(title, snapshot, alarms, expected_codes):
    """
    Prints a readable test report for presentation purposes.

    This makes the unit test understandable during live demonstration.
    """

    print("\n" + "=" * 80)
    print(f"TEST SCENARIO: {title}")
    print("=" * 80)

    print("\nINPUT SNAPSHOT:")
    print(f"FSM State: {snapshot.get('state')}")
    print(f"K1_Temperatur: {snapshot.get('K1_Temperatur')}")
    print(f"K2_Temperatur: {snapshot.get('K2_Temperatur')}")
    print(f"K3_Temperatur: {snapshot.get('K3_Temperatur')}")
    print(f"MobilerSensor_Temperatur: {snapshot.get('MobilerSensor_Temperatur')}")
    print(f"Durchfluss_NachgussMaische: {snapshot.get('Durchfluss_NachgussMaische')}")

    print("\nEXPECTED ALARM CODES:")
    print(expected_codes if expected_codes else "No alarm expected")

    print("\nDETECTED ALARMS:")
    if not alarms:
        print("No alarms detected")
    else:
        for alarm in alarms:
            pprint(alarm)

    print("\nRESULT:")
    actual_codes = get_alarm_codes(alarms)

    if sorted(actual_codes) == sorted(expected_codes):
        print("TEST PASSED: Detected alarms match expected result.")
    else:
        print("TEST FAILED: Detected alarms do not match expected result.")

    print("=" * 80 + "\n")


# ============================================================
# Tests
# ============================================================

def test_no_alarm_for_normal_snapshot():
    """
    Normal valid data should not create alarms.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    alarms = detector.update(snapshot)

    print_test_report(
        title="Normal operation without anomaly",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=[],
    )

    assert alarms == []


def test_temperature_too_high_alarm():
    """
    If a temperature exceeds its upper process limit,
    the detector should raise TEMP_TOO_HIGH.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["K2_Temperatur"] = 85.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    print_test_report(
        title="K2 temperature exceeds upper limit",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=["TEMP_TOO_HIGH"],
    )

    assert "TEMP_TOO_HIGH" in codes


def test_temperature_too_low_alarm():
    """
    If a temperature falls below its lower process limit,
    the detector should raise TEMP_TOO_LOW.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["K2_Temperatur"] = 55.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    print_test_report(
        title="K2 temperature below lower limit",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=["TEMP_TOO_LOW"],
    )

    assert "TEMP_TOO_LOW" in codes


def test_low_flow_during_lautering():
    """
    During lautering, flow is expected.

    If the process is in LAUTERING state and the measured flow
    is too low, the detector should raise LOW_FLOW_DURING_LAUTERING.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["state"] = "LAUTERING"
    snapshot["Durchfluss_NachgussMaische"] = 0.1

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    print_test_report(
        title="Low flow during lautering",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=["LOW_FLOW_DURING_LAUTERING"],
    )

    assert "LOW_FLOW_DURING_LAUTERING" in codes


def test_unexpected_flow_in_idle():
    """
    In IDLE state, no process flow is expected.

    If flow is detected while the plant is idle,
    the detector should raise UNEXPECTED_FLOW_IN_IDLE.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["state"] = "IDLE"
    snapshot["Durchfluss_NachgussMaische"] = 2.5

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    print_test_report(
        title="Unexpected flow while system is idle",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=["UNEXPECTED_FLOW_IN_IDLE"],
    )

    assert "UNEXPECTED_FLOW_IN_IDLE" in codes


def test_invalid_sensor_value():
    """
    Physically impossible values should be detected.

    Example:
    K2 temperature = 999 °C is impossible for this brewing system.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    snapshot["K2_Temperatur"] = 999.0

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    print_test_report(
        title="Invalid physical sensor value",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=["SENSOR_VALUE_INVALID"],
    )

    assert "SENSOR_VALUE_INVALID" in codes


def test_data_stale_alarm():
    """
    If a measurement timestamp is too old,
    the detector should raise DATA_STALE.
    """

    detector = AnomalyDetector()
    snapshot = base_snapshot()

    old_timestamp = make_timestamp(seconds_offset=-10)

    snapshot["_meta"]["K2_Temperatur"]["timestamp"] = old_timestamp

    alarms = detector.update(snapshot)
    codes = get_alarm_codes(alarms)

    print_test_report(
        title="Stale K2 temperature measurement",
        snapshot=snapshot,
        alarms=alarms,
        expected_codes=["DATA_STALE"],
    )

    assert "DATA_STALE" in codes


def test_temperature_rise_too_fast():
    """
    Temperature should not rise unrealistically fast.

    This test simulates a temperature increase from 60 °C to 70 °C
    within 60 seconds. That means 10 °C/min.

    If the configured maximum is 5 °C/min, the detector should raise
    TEMP_RISE_TOO_FAST.
    """

    detector = AnomalyDetector()

    alarms = []

    print("\n" + "=" * 80)
    print("TEST SCENARIO: Temperature rise too fast")
    print("=" * 80)
    print("\nSimulating 61 sensor snapshots over 60 seconds...\n")

    for i in range(61):
        snapshot = base_snapshot()

        timestamp = make_timestamp(seconds_offset=-60 + i)
        temperature = 60.0 + (10.0 / 60.0) * i

        snapshot["_received_at"] = timestamp
        snapshot["K2_Temperatur"] = temperature
        snapshot["_meta"]["K2_Temperatur"]["timestamp"] = timestamp

        alarms = detector.update(snapshot)

        if i in [0, 15, 30, 45, 60]:
            print(
                f"t={i:02d}s | "
                f"K2_Temperatur={temperature:.2f} °C | "
                f"Detected alarms={get_alarm_codes(alarms)}"
            )

    codes = get_alarm_codes(alarms)

    print("\nFINAL DETECTED ALARMS:")
    if not alarms:
        print("No alarms detected")
    else:
        for alarm in alarms:
            pprint(alarm)

    print("\nEXPECTED ALARM CODE:")
    print("TEMP_RISE_TOO_FAST")

    print("\nRESULT:")
    if "TEMP_RISE_TOO_FAST" in codes:
        print("TEST PASSED: Temperature rise was correctly detected as too fast.")
    else:
        print("TEST FAILED: Temperature rise alarm was not detected.")

    print("=" * 80 + "\n")

    assert "TEMP_RISE_TOO_FAST" in codes