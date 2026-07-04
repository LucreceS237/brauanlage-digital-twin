"""
File: status_routes.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Serves the aggregated dashboard status and the snapshot / measurement reads used by the live dashboard and trend chart (section 21, FR-07). Also exposes the FSM endpoints (current state, transition history, acknowledge).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from project.ap3.database import mongodb
from project.ap3.services import collector_service
from project.ap5.services import twin_service
from project.ap3.utils.serialization import clean_doc

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
async def status():
    """Full dashboard status payload (connection, FSM, values, alarms, events)."""
    return await twin_service.get_status()


@router.get("/snapshot/latest")
async def latest_snapshot():
    """Most recent snapshot of the active session."""
    snap = await twin_service.latest_snapshot()
    if snap is None:
        raise HTTPException(status_code=404, detail="No snapshot available.")
    return snap


@router.get("/measurements/latest")
async def latest_measurements():
    """Latest measurement values as a name->value map plus the raw list."""
    return {
        "values": {m["name"]: m["value"] for m in collector_service.runtime.latest_measurements},
        "measurements": collector_service.runtime.latest_measurements,
    }


@router.get("/measurements/history")
async def measurement_history(
    name: str = Query(..., description="Process variable name, e.g. K3_Temperatur"),
    limit: int = Query(120, ge=1, le=2000),
):
    """Recent values of one variable for the trend chart."""
    return {"name": name, "points": await twin_service.measurement_history(name, limit)}


# --- FSM endpoints ----------------------------------------------------------

@router.get("/fsm/current")
async def fsm_current():
    """Current FSM evaluation result (FR-04 structure)."""
    if collector_service.runtime.latest_fsm is None:
        raise HTTPException(status_code=404, detail="FSM not initialised.")
    return collector_service.runtime.latest_fsm


@router.get("/fsm/transitions")
async def fsm_transitions():
    """Full FSM transition history for the active session."""
    session_id = collector_service.runtime.session_id
    if session_id is None:
        return []
    docs = await mongodb.fsm_states().find(
        {"sessionId": session_id}
    ).sort("createdAt", 1).to_list(length=1000)
    return [clean_doc(d) for d in docs]


@router.post("/fsm/acknowledge")
async def fsm_acknowledge():
    """Acknowledge an ERROR / EMERGENCY so the FSM can recover to IDLE."""
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active session.")
    collector_service.request_acknowledge()
    return {"message": "Acknowledge accepted. The FSM will attempt recovery."}
