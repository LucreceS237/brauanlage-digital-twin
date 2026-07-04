"""
File: session_service.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Owns the session lifecycle (section 13). Every real SPS connection or simulation run is one session, identified by a sessionId that is stamped on all runtime documents. This service creates sessions, records system events, ends sessions and triggers the per-session runtime cleanup on disconnect / reset.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from project.ap3.database import mongodb
from project.ap3.database.models import (
    EventLevel,
    SessionStatus,
    SystemEvent,
    utcnow,
)


def new_session_id() -> str:
    """Build a human-readable, sortable session id: session_YYYY_MM_DD_HHMMSS."""
    return datetime.now(timezone.utc).strftime("session_%Y_%m_%d_%H%M%S")


async def create_session(mode: str, scenario: Optional[str] = None) -> dict:
    """Insert a new ACTIVE session document and return it."""
    doc = {
        "sessionId": new_session_id(),
        "mode": mode,
        "scenario": scenario,
        "status": SessionStatus.ACTIVE.value,
        "startedAt": utcnow(),
        "endedAt": None,
    }
    await mongodb.sessions().insert_one(doc)
    doc.pop("_id", None)
    return doc


async def end_session(session_id: str) -> None:
    """Mark a session as ENDED with an end timestamp."""
    await mongodb.sessions().update_one(
        {"sessionId": session_id},
        {"$set": {"status": SessionStatus.ENDED.value, "endedAt": utcnow()}},
    )


async def log_event(
    session_id: str,
    event_type: str,
    message: str,
    level: EventLevel = EventLevel.INFO,
    details: Optional[dict] = None,
) -> None:
    """Append a system event for the session (used across services)."""
    event = SystemEvent(
        sessionId=session_id,
        level=level.value,
        eventType=event_type,
        message=message,
        details=details,
    )
    await mongodb.system_events().insert_one(event.model_dump())


async def cleanup_runtime(session_id: str) -> dict[str, int]:
    """
    Delete all runtime data for a session (FR-09/FR-10) and log the result.

    Returns the per-collection deletion counts.
    """
    deleted = await mongodb.delete_runtime_data(session_id)
    # The deletion of system_events also removes earlier events for this
    # session; we log a final event AFTER deletion so there is a trace that the
    # cleanup ran (it belongs to the now mostly-empty session).
    await log_event(
        session_id,
        "RUNTIME_DATA_DELETED",
        "Runtime session data deleted from MongoDB.",
        level=EventLevel.WARNING,
        details=deleted,
    )
    return deleted
