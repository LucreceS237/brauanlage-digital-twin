"""
File: storage_service.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Persists runtime snapshots, measurements and FSM transition records in MongoDB.
"""
from __future__ import annotations

from typing import Any, Optional

from project.ap3.database import mongodb
from project.ap3.database.data_points import DATA_POINTS_BY_NAME
from project.ap3.database.models import utcnow

_META_KEYS = {
    "start_requested", "mash_finished", "lautering_finished", "boiling_finished",
    "cooled_down", "fermentation_finished", "active_fault", "absolute_limit",
}


async def store_snapshot(
    session_id: str,
    *,
    source: str,
    publisher_mode: str,
    connection_status: str,
    collector_status: str,
    fsm_state: str,
    display_state: str,
    previous_state: str,
    transition_reason: str,
    time_in_state_s: float,
    values: dict[str, Any],
    emergency_stop: bool,
    acknowledge: bool,
    sensor_ok: bool,
    active_fault: bool,
) -> tuple[str, list[dict], dict]:
    snapshot_doc = {
        "sessionId": session_id,
        "receivedAt": utcnow(),
        "source": source,
        "publisherMode": publisher_mode,
        "connectionStatus": connection_status,
        "collectorStatus": collector_status,
        "fsmState": fsm_state,
        "displayState": display_state,
        "previousFsmState": previous_state,
        "transitionReason": transition_reason,
        "timeInStateSeconds": round(time_in_state_s, 2),
        "aktuellerSchritt": values.get("Aktueller_Schritt") or values.get("aktueller_schritt"),
        "emergencyStop": emergency_stop,
        "acknowledge": acknowledge,
        "sensorOk": sensor_ok,
        "activeFault": active_fault,
    }
    inserted = await mongodb.snapshots().insert_one(snapshot_doc)
    snapshot_id = str(inserted.inserted_id)
    measurements = _build_measurements(session_id, snapshot_id, values)
    if measurements:
        await mongodb.measurements().insert_many(measurements)
    return snapshot_id, measurements, snapshot_doc


async def store_fsm_transition(
    session_id: str,
    snapshot_id: str,
    *,
    current_state: str,
    display_state: str,
    previous_state: str,
    transition_reason: str,
) -> None:
    await mongodb.fsm_states().insert_one({
        "sessionId": session_id,
        "snapshotId": snapshot_id,
        "currentState": current_state,
        "displayState": display_state,
        "previousState": previous_state,
        "transitionReason": transition_reason,
        "timeInStateSeconds": 0,
        "createdAt": utcnow(),
    })


def _build_measurements(session_id: str, snapshot_id: str, values: dict) -> list[dict]:
    now = utcnow()
    out: list[dict] = []
    for name, value in values.items():
        if name in _META_KEYS or name.startswith("_"):
            continue
        definition = DATA_POINTS_BY_NAME.get(name)
        if definition is None and name != "Aktueller_Schritt":
            continue
        out.append({
            "sessionId": session_id,
            "snapshotId": snapshot_id,
            "name": name if name != "Aktueller_Schritt" else "aktueller_schritt",
            "value": value,
            "unit": definition.get("unit", "") if definition else "",
            "component": definition.get("component", "") if definition else "",
            "quality": "Good",
            "timestamp": now,
        })
    return out
