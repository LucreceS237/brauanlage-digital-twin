"""
File: connection_routes.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Implements the connection workflow endpoints (section 21). The user connects in real SPS or simulation mode, queries the connection status, and runs the guarded two-step disconnect (request -> confirm) that deletes runtime data only after explicit confirmation (FR-09 / FR-11).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from project.ap3.database.models import ConnectionMode, ConnectRequest
from project.ap3.services import collector_service
from project.ap5.services import twin_service
from project.ap3.services.collector_service import SpsConnectionError

router = APIRouter(prefix="/api", tags=["connection"])


@router.post("/connect")
async def connect(req: ConnectRequest):
    """
    Start a real SPS connection (via MQTT) or a simulation run; creates a
    session. For real mode this subscribes to the broker and waits for the first
    valid SPS payload before reporting success (§8).
    """
    try:
        session = await collector_service.start(
            mode=req.mode, scenario=req.scenario, endpoint=req.opcuaEndpoint
        )
    except SpsConnectionError as exc:
        # Expected failure (broker down / no live data): report, do not 500.
        return {"success": False, "message": str(exc)}
    except Exception as exc:  # noqa: BLE001 - unexpected error
        return {
            "success": False,
            "message": f"Connection failed: {exc}. Tip: use simulation mode as a fallback.",
        }

    if req.mode == ConnectionMode.REAL:
        message = "Connection successful – live SPS data received via MQTT."
    else:
        message = "Simulation mode started successfully."
    return {
        "success": True,
        "message": message,
        "session": session,
        "status": twin_service.connection_status(),
    }


@router.get("/connection-status")
async def connection_status():
    """Return the current connection status for the GUI status card."""
    return twin_service.connection_status()


@router.post("/disconnect/request")
async def disconnect_request():
    """
    Step 1 of disconnect: warn the user. No data is deleted here. The GUI shows
    the confirmation modal and may download the logbook first.
    """
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active connection.")
    return {
        "warning": (
            "You are about to disconnect the Anlage. All runtime values stored "
            "during this session will be deleted from the database to protect "
            "data and avoid conflicts with the next connection."
        ),
        "sessionId": collector_service.runtime.session_id,
        "options": [
            "Download logbook and disconnect",
            "Disconnect without logbook",
            "Cancel",
        ],
    }


@router.post("/disconnect/confirm")
async def disconnect_confirm():
    """
    Step 2 of disconnect: delete runtime data, end the session and disconnect
    the source. The GUI is expected to download the logbook (if requested)
    BEFORE calling this endpoint.
    """
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active connection.")
    deleted = await collector_service.stop(delete_runtime=True)
    return {"message": "Disconnected. Runtime session data deleted.", "deleted": deleted}


@router.delete("/session/current/runtime-data")
async def delete_runtime_data():
    """Explicit cleanup endpoint (FR-09): delete current session runtime data."""
    if not collector_service.runtime.active:
        raise HTTPException(status_code=409, detail="No active session.")
    deleted = await collector_service.stop(delete_runtime=True)
    return {"message": "Runtime data deleted.", "deleted": deleted}
