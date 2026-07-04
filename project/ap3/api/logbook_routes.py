"""
File: logbook_routes.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Serves the logbook preview and the CSV download offered before runtime data is deleted (section 17 / FR-12). The CSV is streamed as an attachment so the browser downloads it directly.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from project.ap3.services import collector_service, logbook_service

router = APIRouter(prefix="/api/logbook", tags=["logbook"])


def _require_session() -> str:
    session_id = collector_service.runtime.session_id
    if session_id is None:
        raise HTTPException(status_code=409, detail="No active session to export.")
    return session_id


@router.get("/preview")
async def preview():
    """Return a small preview of the logbook (columns + first rows)."""
    return await logbook_service.preview(_require_session())


@router.get("/export/csv")
async def export_csv():
    """Download the full session logbook as a CSV attachment."""
    session_id = _require_session()
    csv_text = await logbook_service.build_csv(session_id)
    filename = f"logbook_{session_id}.csv"
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
