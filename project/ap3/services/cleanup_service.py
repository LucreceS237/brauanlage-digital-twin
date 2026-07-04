"""
File: cleanup_service.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Session runtime-data cleanup on disconnect / simulation reset.
"""
from __future__ import annotations

from project.ap3.services import session_service


async def cleanup_session_runtime(session_id: str) -> dict[str, int]:
    return await session_service.cleanup_runtime(session_id)
