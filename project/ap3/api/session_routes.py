"""
File: session_routes.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Session lifecycle endpoints (cleanup, current session info).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from project.ap3.services import collector_service

router = APIRouter(prefix="/api", tags=["session"])


@router.get("/session/current")
async def current_session():
    if not collector_service.runtime.active or collector_service.runtime.session is None:
        raise HTTPException(status_code=404, detail="No active session.")
    return collector_service.runtime.session


@router.delete("/session/current/runtime-data")
async def delete_runtime_data():
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active session.")
    deleted = await collector_service.stop(delete_runtime=True)
    return {"message": "Runtime data deleted.", "deleted": deleted}
