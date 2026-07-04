"""
File: simulation_routes.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Implements the simulation control endpoints (section 21 / FR-08, FR-10). Each scenario starts a fresh session with a clean runtime state; starting / resetting a scenario follows the guarded request -> confirm flow so previous runtime data is only deleted after confirmation (and an optional logbook download).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from project.ap3.database import mongodb
from project.ap3.database.models import ConnectionMode, ScenarioSelectRequest, SimulationStartRequest
from project.ap3.services import collector_service
from project.ap3.simulation.scenarios import SCENARIOS
from project.ap3.utils.serialization import clean_doc

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.get("/scenarios")
async def list_scenarios():
    """Return the available simulation scenarios (from MongoDB, with fallback)."""
    docs = await mongodb.simulation_scenarios().find().to_list(length=100)
    if docs:
        return [clean_doc(d) for d in docs]
    # Fallback to the in-code catalogue if seeding has not run yet.
    return [
        {"name": s.name, "description": s.description,
         "targetState": s.target_state, "expectedAlarm": s.expected_alarm}
        for s in SCENARIOS
    ]


@router.post("/start")
async def start_simulation(req: SimulationStartRequest):
    """Start a simulation scenario in a fresh session."""
    session = await collector_service.start(
        mode=ConnectionMode.SIMULATION, scenario=req.scenario, endpoint=None
    )
    return {"message": "Simulation mode started successfully.", "session": session}


@router.post("/scenario")
async def select_scenario(req: ScenarioSelectRequest):
    """Switch to another scenario (alias of starting a new scenario session)."""
    session = await collector_service.start(
        mode=ConnectionMode.SIMULATION, scenario=req.scenario, endpoint=None
    )
    return {"message": f"Scenario '{req.scenario}' started.", "session": session}


@router.post("/stop/request")
async def stop_request():
    """Warn before stopping a simulation (mirrors disconnect/request)."""
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active simulation.")
    return {
        "warning": (
            "Stopping the simulation will delete all runtime values stored "
            "during this scenario."
        ),
        "sessionId": collector_service.runtime.session_id,
        "options": ["Download logbook and stop", "Stop without logbook", "Cancel"],
    }


@router.post("/stop/confirm")
async def stop_confirm():
    """Stop the simulation and delete runtime data after confirmation."""
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active simulation.")
    deleted = await collector_service.stop(delete_runtime=True)
    return {"message": "Simulation stopped. Runtime data deleted.", "deleted": deleted}


@router.post("/reset/request")
async def reset_request():
    """Warn before resetting (deleting) previous simulation runtime data."""
    return {
        "warning": (
            "Starting a new scenario will delete the previous simulation runtime "
            "data. Download a CSV logbook first if you want to keep it."
        ),
        "sessionId": collector_service.runtime.session_id,
        "options": [
            "Download logbook and start new scenario",
            "Start new scenario without logbook",
            "Cancel",
        ],
    }


@router.post("/reset/confirm")
async def reset_confirm(req: ScenarioSelectRequest):
    """Delete previous runtime data and start the selected scenario fresh."""
    if collector_service.runtime.active:
        await collector_service.stop(delete_runtime=True)
    session = await collector_service.start(
        mode=ConnectionMode.SIMULATION, scenario=req.scenario, endpoint=None
    )
    return {"message": f"New scenario '{req.scenario}' started.", "session": session}
