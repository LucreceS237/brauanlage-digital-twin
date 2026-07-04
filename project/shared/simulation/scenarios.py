"""
File: scenarios.py
Work Package: shared
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: a fault at the appropriate phase so AP4/AP5 alarms can be demonstrated.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    description: str
    target_state: str
    expected_alarm: str | None
    fault: str | None


SCENARIOS: list[Scenario] = [
    Scenario(
        "NORMAL_PROCESS",
        "Normal process",
        "Full brewing run with smooth, coherent demo values and no injected faults.",
        "FINISHED", None, None,
    ),
    Scenario(
        "TEMPERATURE_TOO_HIGH",
        "Temperature too high",
        "Boiling temperature climbs above the allowed range during BOILING.",
        "BOILING", "TEMP_OUT_OF_RANGE", "temp_high",
    ),
    Scenario(
        "LOW_FLOW_DURING_LAUTERING",
        "Low flow during lautering",
        "Lautering runs with insufficient flow (< 0.5 l/min).",
        "LAUTERING", "LOW_FLOW_DURING_LAUTERING", "low_flow",
    ),
    Scenario(
        "SENSOR_FAILURE",
        "Sensor failure",
        "A sensor reports not-OK during the run.",
        "MASHING", "SENSOR_VALUE_INVALID", "sensor_fail",
    ),
    Scenario(
        "STALE_DATA",
        "Stale data",
        "Fresh values stop arriving (stale-data path).",
        "MASHING", "DATA_STALE", "stale",
    ),
    Scenario(
        "COOLING_FAILURE",
        "Cooling failure",
        "During COOLING the K3 temperature fails to decrease.",
        "COOLING", "COOLING_NOT_DECREASING", "cooling_fail",
    ),
    Scenario(
        "FERMENTATION_TEMP_OUT_OF_RANGE",
        "Fermentation temperature out of range",
        "Fermentation temperature leaves the 16–22 °C window.",
        "FERMENTING", "FERMENTATION_TEMP_OUT_OF_RANGE", "ferment_temp",
    ),
    Scenario(
        "EMERGENCY_STOP",
        "Emergency stop",
        "Operator emergency stop during the process.",
        "EMERGENCY", "EMERGENCY_STOP_ACTIVE", "emergency",
    ),
    Scenario(
        "ABSOLUTE_LIMIT_EXCEEDED",
        "Absolute limit exceeded",
        "A temperature crosses the absolute safety limit.",
        "EMERGENCY", "ABSOLUTE_LIMIT_EXCEEDED", "absolute_limit",
    ),
]

SCENARIO_KEYS = {s.key: s for s in SCENARIOS}
SCENARIOS_BY_NAME = {s.name: s for s in SCENARIOS}


def get_scenario(name_or_key: str) -> Scenario:
    """Resolve a scenario by key (NORMAL_PROCESS) or display name (Normal process)."""
    key = name_or_key.strip().upper().replace(" ", "_")
    if key in SCENARIO_KEYS:
        return SCENARIO_KEYS[key]
    if name_or_key in SCENARIOS_BY_NAME:
        return SCENARIOS_BY_NAME[name_or_key]
    return SCENARIO_KEYS["NORMAL_PROCESS"]
