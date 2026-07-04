"""
File: payload_validator.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Validates MQTT payloads from AP2 before AP5/AP4 consume them. Malformed payloads must never crash the backend; they are rejected and logged as system events.
"""
from __future__ import annotations

from numbers import Number
from typing import Any

_NUMERIC_KEYS = {
    "Aktueller_Schritt", "K1_Temperatur", "K2_Temperatur", "K2_Füllstand",
    "K3_Temperatur", "K3_Füllstand", "K3_MinimalerFüllstand",
    "K3_MaximalerFüllstand", "MobilerSensor_Temperatur", "Durchfluss_NachgussMaische",
}
_BOOL_KEYS = {"K1_Füllstand_OK", "emergency_stop", "sensor_ok", "acknowledge"}


def validate_payload(raw: Any) -> tuple[bool, str | None]:
    if not isinstance(raw, dict):
        return False, "payload is not a JSON object"
    if "values" not in raw or not isinstance(raw["values"], dict):
        return False, "missing or invalid 'values' object"
    if not raw["values"]:
        return False, "'values' object is empty"
    if "timestamp" not in raw:
        return False, "missing 'timestamp'"
    if "source" not in raw:
        return False, "missing 'source'"
    if "publisherMode" not in raw:
        return False, "missing 'publisherMode'"
    if "connectionStatus" not in raw:
        return False, "missing 'connectionStatus'"

    values = raw["values"]
    for key, value in values.items():
        if key in _NUMERIC_KEYS and not isinstance(value, Number):
            return False, f"field '{key}' must be numeric, got {type(value).__name__}"
        if key in _BOOL_KEYS and not isinstance(value, bool):
            return False, f"field '{key}' must be boolean, got {type(value).__name__}"
    return True, None
