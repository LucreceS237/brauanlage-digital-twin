"""
File: __init__.py
Work Package: shared
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: FSM-aligned process simulator shared by AP2 (fake MQTT) and AP3 (simulation mode).
"""
from .payload_builder import build_sps_payload
from .process_simulator import ProcessSimulator
from .scenarios import SCENARIOS, SCENARIO_KEYS, Scenario, get_scenario

__all__ = [
    "ProcessSimulator",
    "build_sps_payload",
    "Scenario",
    "SCENARIOS",
    "SCENARIO_KEYS",
    "get_scenario",
]
