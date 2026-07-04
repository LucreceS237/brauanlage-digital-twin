"""
File: data_points.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Single source of truth for the SPS/PLC process variables (NodeIds, units, components, validation status and polling recommendations). Engineer A owns the NodeId mapping and the read-only SPS boundary; nothing here ever writes back to the PLC.
"""
from __future__ import annotations

from typing import Any

# Canonical process-variable keys used across the whole backend. Using stable
# string keys (not NodeIds) lets the simulator and the real SPS feed the same
# downstream logic.
K1_TEMPERATUR = "K1_Temperatur"
K1_FUELLSTAND_OK = "K1_Füllstand_OK"
K2_TEMPERATUR = "K2_Temperatur"
K2_FUELLSTAND = "K2_Füllstand"
K3_TEMPERATUR = "K3_Temperatur"
K3_FUELLSTAND = "K3_Füllstand"
K3_MIN_FUELLSTAND = "K3_MinimalerFüllstand"
K3_MAX_FUELLSTAND = "K3_MaximalerFüllstand"
MOBILER_SENSOR_TEMPERATUR = "MobilerSensor_Temperatur"
DURCHFLUSS = "Durchfluss_NachgussMaische"
AKTUELLER_SCHRITT = "aktueller_schritt"
EMERGENCY_STOP = "emergency_stop"
ACKNOWLEDGE = "acknowledge"
SENSOR_OK = "sensor_ok"


def _node(name: str) -> str:
    """Build the OPC-UA NodeId string for a process variable (Engineer A)."""
    return f'ns=3;s="Datenbaustein_Prozessvariablen"."{name}"'


# The catalogue seeded into the data_points collection. Mirrors section 20 of
# the MVP description. pollGroup/pollInterval are Engineer A's recommendations.
DATA_POINTS: list[dict[str, Any]] = [
    {
        "name": K1_TEMPERATUR, "nodeId": _node(K1_TEMPERATUR), "dataType": "Float",
        "unit": "°C", "component": "K1", "category": "temperature",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": K1_FUELLSTAND_OK, "nodeId": _node(K1_FUELLSTAND_OK), "dataType": "Bool",
        "unit": "", "component": "K1", "category": "level",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": False,
        "validationStatus": "plausible",
    },
    {
        "name": K2_TEMPERATUR, "nodeId": _node(K2_TEMPERATUR), "dataType": "Float",
        "unit": "°C", "component": "K2", "category": "temperature",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": K2_FUELLSTAND, "nodeId": _node(K2_FUELLSTAND), "dataType": "Float",
        "unit": "%", "component": "K2", "category": "level",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": K3_TEMPERATUR, "nodeId": _node(K3_TEMPERATUR), "dataType": "Float",
        "unit": "°C", "component": "K3", "category": "temperature",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": K3_FUELLSTAND, "nodeId": _node(K3_FUELLSTAND), "dataType": "Float",
        "unit": "%", "component": "K3", "category": "level",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        # Engineer A flagged this as still under validation (see LAUTERING).
        "validationStatus": "validation_candidate",
    },
    {
        "name": K3_MIN_FUELLSTAND, "nodeId": _node(K3_MIN_FUELLSTAND), "dataType": "Float",
        "unit": "%", "component": "K3", "category": "level_limit",
        "pollGroup": "static", "pollIntervalSeconds": 30,
        "useInFSM": False, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": K3_MAX_FUELLSTAND, "nodeId": _node(K3_MAX_FUELLSTAND), "dataType": "Float",
        "unit": "%", "component": "K3", "category": "level_limit",
        "pollGroup": "static", "pollIntervalSeconds": 30,
        "useInFSM": False, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": MOBILER_SENSOR_TEMPERATUR, "nodeId": _node(MOBILER_SENSOR_TEMPERATUR),
        "dataType": "Float", "unit": "°C", "component": "K4", "category": "temperature",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": DURCHFLUSS, "nodeId": _node(DURCHFLUSS), "dataType": "Float",
        "unit": "l/min", "component": "FLOW_PATH", "category": "flow",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": AKTUELLER_SCHRITT, "nodeId": _node(AKTUELLER_SCHRITT), "dataType": "Int",
        "unit": "", "component": "CONTROL", "category": "step",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": False,
        "validationStatus": "plausible",
    },
    {
        "name": EMERGENCY_STOP, "nodeId": _node(EMERGENCY_STOP), "dataType": "Bool",
        "unit": "", "component": "SAFETY", "category": "safety",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
    {
        "name": ACKNOWLEDGE, "nodeId": _node(ACKNOWLEDGE), "dataType": "Bool",
        "unit": "", "component": "CONTROL", "category": "control",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": False,
        "validationStatus": "plausible",
    },
    {
        "name": SENSOR_OK, "nodeId": _node(SENSOR_OK), "dataType": "Bool",
        "unit": "", "component": "DIAGNOSTICS", "category": "quality",
        "pollGroup": "dynamic", "pollIntervalSeconds": 1,
        "useInFSM": True, "useInAPI": True, "useInAnomalyDetection": True,
        "validationStatus": "plausible",
    },
]

# Convenience lookup: name -> definition.
DATA_POINTS_BY_NAME = {dp["name"]: dp for dp in DATA_POINTS}
