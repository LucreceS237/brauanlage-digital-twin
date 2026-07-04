"""
File: twin_service.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Builds the frontend-ready digital twin status payload from AP3 runtime state, MongoDB and AP4/AP5 outputs.
"""
from __future__ import annotations

from typing import Any, Optional

from project.ap3.database import mongodb
from project.ap3.services import collector_service
from project.ap3.utils.serialization import clean_doc
from project.ap4.states import NORMAL_SEQUENCE
from project.ap5.adapters.mapping import APPROVED_VESSELS, PHASE_PRIMARY_VESSEL
from project.ap5.services import alarm_service


def connection_status() -> dict:
    rt = collector_service.runtime
    return {
        "active": rt.active,
        "mode": rt.mode,
        "connectionStatus": rt.connection_status,
        "endpoint": rt.endpoint,
        "sessionId": rt.session_id,
        "scenario": rt.session.get("scenario") if rt.session else None,
        "fsmState": rt.latest_fsm.get("current_state") if rt.latest_fsm else None,
        "displayState": rt.latest_fsm.get("display_state") if rt.latest_fsm else None,
        "publisherMode": rt.publisher_mode,
        "source": rt.source,
    }


def timeline() -> list[dict]:
    current = collector_service.runtime.latest_fsm.get("current_state", "IDLE") if collector_service.runtime.latest_fsm else "IDLE"
    return [
        {
            "state": s.name,
            "current": s.name == current,
            "mainVessel": PHASE_PRIMARY_VESSEL.get(s.name, "-"),
            "vesselLabel": APPROVED_VESSELS.get(PHASE_PRIMARY_VESSEL.get(s.name, ""), "-"),
        }
        for s in NORMAL_SEQUENCE
    ] + [
        {"state": "ERROR", "current": current == "ERROR", "mainVessel": "-", "vesselLabel": "-"},
        {"state": "EMERGENCY", "current": current == "EMERGENCY", "mainVessel": "-", "vesselLabel": "-"},
    ]


async def get_status() -> dict:
    rt = collector_service.runtime
    if not rt.active or rt.session_id is None:
        return {"connected": False, "connection": connection_status()}

    session_id = rt.session_id
    active_alarms = await alarm_service.get_active(session_id)
    events = await mongodb.system_events().find({"sessionId": session_id}).sort("createdAt", -1).to_list(length=25)
    transitions = await mongodb.fsm_states().find({"sessionId": session_id}).sort("createdAt", 1).to_list(length=100)
    fsm = rt.latest_fsm or {}
    values = {m["name"]: m["value"] for m in rt.latest_measurements}
    clean_events = [clean_doc(e) for e in events]
    mode_label = "REAL_SPS" if rt.mode == "real" else "SIMULATION"

    return {
        "connectionStatus": rt.connection_status,
        "mode": mode_label,
        "source": rt.source,
        "publisherMode": rt.publisher_mode,
        "latestSnapshotTime": rt.latest_snapshot.get("receivedAt") if rt.latest_snapshot else None,
        "currentState": fsm.get("current_state"),
        "displayState": fsm.get("display_state"),
        "previousState": fsm.get("previous_state"),
        "transitionReason": fsm.get("transition_reason"),
        "timeInStateSeconds": fsm.get("time_in_state"),
        "values": values,
        "alarms": active_alarms,
        "systemEvents": clean_events,
        "connected": True,
        "connection": connection_status(),
        "session": clean_doc(rt.session),
        "fsm": rt.latest_fsm,
        "mainVessel": PHASE_PRIMARY_VESSEL.get(fsm.get("current_state", "IDLE"), "-"),
        "snapshot": rt.latest_snapshot,
        "measurements": values,
        "activeAlarms": active_alarms,
        "alarmCount": len(active_alarms),
        "timeline": timeline(),
        "transitions": [clean_doc(t) for t in transitions],
        "events": clean_events,
    }


async def latest_snapshot() -> Optional[dict]:
    return collector_service.runtime.latest_snapshot


async def measurement_history(name: str, limit: int = 120) -> list[dict]:
    if collector_service.runtime.session_id is None:
        return []
    docs = await mongodb.measurements().find(
        {"sessionId": collector_service.runtime.session_id, "name": name}
    ).sort("timestamp", -1).to_list(length=limit)
    docs.reverse()
    return [clean_doc(d) for d in docs]
