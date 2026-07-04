"""
File: alarm_routes.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Serves active and historical alarms to the Alarm Center and handles per-alarm acknowledge (section 21 / FR-06). Alarms are scoped to the active session.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from project.ap5.services import alarm_service
from project.ap3.services import collector_service

router = APIRouter(prefix="/api/alarms", tags=["alarms"])


def _require_session() -> str:
    session_id = collector_service.runtime.session_id
    if session_id is None:
        raise HTTPException(status_code=409, detail="No active session.")
    return session_id


@router.get("/active")
async def active_alarms():
    """Currently ACTIVE alarms for the session."""
    return await alarm_service.get_active(_require_session())


@router.get("/history")
async def alarm_history():
    """All alarms (active + cleared + acknowledged) for the session."""
    return await alarm_service.get_history(_require_session())


@router.post("/{alarm_id}/acknowledge")
async def acknowledge_alarm(alarm_id: str):
    """Acknowledge a single alarm by id."""
    ok = await alarm_service.acknowledge(_require_session(), alarm_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Alarm not found.")
    return {"message": "Alarm acknowledged.", "id": alarm_id}
