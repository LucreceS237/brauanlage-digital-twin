"""
File: seed_data_points.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Seeds (or re-seeds) the static collections that survive runtime cleanup: - data_points: OPC-UA variable definitions (from opcua/data_points.py) - simulation_scenarios: the selectable demo scenarios (from simulation/scenarios.py)
"""
from __future__ import annotations

from project.ap3.database import mongodb
from project.ap3.database.data_points import DATA_POINTS
from project.ap3.simulation.scenarios import SCENARIOS


async def seed_data_points() -> int:
    """Upsert every OPC-UA data point definition. Returns count seeded."""
    coll = mongodb.data_points()
    for dp in DATA_POINTS:
        await coll.update_one({"name": dp["name"]}, {"$set": dp}, upsert=True)
    return len(DATA_POINTS)


async def seed_scenarios() -> int:
    """Upsert every available simulation scenario. Returns count seeded."""
    coll = mongodb.simulation_scenarios()
    for sc in SCENARIOS:
        doc = {
            "name": sc.name,
            "description": sc.description,
            "targetState": sc.target_state,
            "expectedAlarm": sc.expected_alarm,
        }
        await coll.update_one({"name": sc.name}, {"$set": doc}, upsert=True)
    return len(SCENARIOS)


async def seed_all() -> dict[str, int]:
    """Seed both static catalogues. Called once on backend startup."""
    return {
        "data_points": await seed_data_points(),
        "simulation_scenarios": await seed_scenarios(),
    }
