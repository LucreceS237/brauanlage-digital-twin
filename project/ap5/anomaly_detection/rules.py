"""
File: rules.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: EXTRA anomaly rules that AP4 does NOT own. AP4 already handles process/safety faults (temperature windows, levels, valves, emergency stop, stale via missing_value_age). AP5 must not duplicate those. These rules cover the MQTT/transport and integration layer instead:
"""
from __future__ import annotations

from numbers import Number
from typing import Any, Optional

from .alarm import Alarm, AlarmSeverity, make_alarm

# Thresholds (transport layer).
STALE_SECONDS = 10.0
MAX_TEMP_RISE_C_PER_S = 5.0
_TEMP_KEYS = ("K1_Temperatur", "K2_Temperatur", "K3_Temperatur", "MobilerSensor_Temperatur")


def r_mqtt_stale(payload: dict, meta: dict) -> Optional[Alarm]:
    age = meta.get("seconds_since_last", 0.0)
    if age > STALE_SECONDS:
        return make_alarm(
            rule_id="AP5_001", code="AP5_001_MQTT_DATA_STALE", severity=AlarmSeverity.HIGH,
            state=meta.get("fsm_state", "-"), component="MQTT link", variable="seconds_since_last",
            value=round(age, 1), threshold=f"<= {STALE_SECONDS}s",
            message="No fresh SPS data received via MQTT within the timeout.",
        )
    return None


def r_publisher_disconnected(payload: dict, meta: dict) -> Optional[Alarm]:
    if str(payload.get("connectionStatus", "")).upper() == "DISCONNECTED":
        return make_alarm(
            rule_id="AP5_002", code="AP5_002_PUBLISHER_DISCONNECTED", severity=AlarmSeverity.HIGH,
            state=meta.get("fsm_state", "-"), component="SPS publisher", variable="connectionStatus",
            value="DISCONNECTED", threshold="CONNECTED",
            message="MQTT publisher reports the SPS is disconnected.",
        )
    return None


def r_invalid_payload(payload: dict, meta: dict) -> Optional[Alarm]:
    if meta.get("invalid_payload"):
        return make_alarm(
            rule_id="AP5_003", code="AP5_003_INVALID_MQTT_PAYLOAD", severity=AlarmSeverity.MEDIUM,
            state=meta.get("fsm_state", "-"), component="MQTT link", variable="payload",
            value=meta.get("invalid_reason", "invalid"), threshold="valid schema",
            message="A malformed MQTT payload was received and discarded.",
        )
    return None


def r_temp_rise_too_fast(payload: dict, meta: dict) -> Optional[Alarm]:
    prev = meta.get("previous_values") or {}
    dt = meta.get("seconds_since_last", 0.0) or 0.0
    if dt <= 0:
        return None
    values = payload.get("values", {})
    for key in _TEMP_KEYS:
        cur, old = values.get(key), prev.get(key)
        if isinstance(cur, Number) and isinstance(old, Number):
            rate = (float(cur) - float(old)) / dt
            if rate > MAX_TEMP_RISE_C_PER_S:
                return make_alarm(
                    rule_id="AP5_004", code="AP5_004_TEMP_RISE_TOO_FAST", severity=AlarmSeverity.MEDIUM,
                    state=meta.get("fsm_state", "-"), component=key, variable=key,
                    value=round(rate, 2), threshold=f"<= {MAX_TEMP_RISE_C_PER_S} °C/s",
                    message=f"{key} rising faster than plausible ({rate:.1f} °C/s).",
                )
    return None


def r_source_mismatch(payload: dict, meta: dict) -> Optional[Alarm]:
    expected = str(meta.get("expected_mode", "")).upper()  # REAL / SIMULATION / ""
    source = str(payload.get("source", "")).upper()
    if expected == "REAL" and source.startswith("FAKE"):
        return make_alarm(
            rule_id="AP5_005", code="AP5_005_SOURCE_MISMATCH_FAKE_WHILE_REAL", severity=AlarmSeverity.HIGH,
            state=meta.get("fsm_state", "-"), component="SPS publisher", variable="source",
            value=payload.get("source"), threshold="REAL_SPS",
            message="Fake SPS data received while REAL mode was expected.",
        )
    return None


EXTRA_RULES = (
    r_mqtt_stale,
    r_publisher_disconnected,
    r_invalid_payload,
    r_temp_rise_too_fast,
    r_source_mismatch,
)
