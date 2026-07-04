"""
File: logbook_service.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Builds the downloadable CSV logbook offered before runtime data is deleted (section 17 / FR-12). The logbook joins, per snapshot, the measured values, the FSM state/transition info and any alarms raised at that snapshot, so the run can be retraced offline. For the MVP a single CSV file is produced.
"""
from __future__ import annotations

import csv
import io
from typing import Any

from project.ap3.database import mongodb

# CSV column order (section 17). Measurement columns map to data-point names.
CSV_COLUMNS = [
    "session_id", "timestamp", "source", "connection_mode",
    "fsm_state", "display_state", "previous_fsm_state", "transition_reason", "time_in_state_s",
    "aktueller_schritt",
    "K1_Temperatur", "K1_Füllstand_OK", "K2_Temperatur", "K2_Füllstand",
    "K3_Temperatur", "K3_Füllstand", "K3_MinimalerFüllstand", "K3_MaximalerFüllstand",
    "MobilerSensor_Temperatur", "Durchfluss_NachgussMaische",
    "sensor_ok", "emergency_stop", "active_fault",
    "alarm_active", "alarm_codes", "alarm_severities", "alarm_messages",
    "system_events",
]


async def _load_session(session_id: str) -> dict:
    """Load a session document (for the connection_mode column)."""
    return await mongodb.sessions().find_one({"sessionId": session_id}) or {}


async def build_rows(session_id: str) -> list[dict[str, Any]]:
    """
    Build one logbook row per snapshot, enriched with measurements, alarms and
    nearby system events. Returned as a list of dicts keyed by CSV_COLUMNS.
    """
    session = await _load_session(session_id)
    mode = session.get("mode", "")

    snapshots = await mongodb.snapshots().find(
        {"sessionId": session_id}
    ).sort("receivedAt", 1).to_list(length=100000)

    # Group measurements and alarms by snapshotId for an efficient join.
    measurements = await mongodb.measurements().find(
        {"sessionId": session_id}
    ).to_list(length=1000000)
    meas_by_snap: dict[str, dict[str, Any]] = {}
    for m in measurements:
        meas_by_snap.setdefault(m.get("snapshotId"), {})[m["name"]] = m["value"]

    alarms = await mongodb.alarms().find({"sessionId": session_id}).to_list(length=100000)
    alarms_by_snap: dict[str, list[dict]] = {}
    for a in alarms:
        alarms_by_snap.setdefault(a.get("snapshotId"), []).append(a)

    events = await mongodb.system_events().find(
        {"sessionId": session_id}
    ).sort("createdAt", 1).to_list(length=100000)
    event_summary = "; ".join(f"{e.get('eventType')}:{e.get('message')}" for e in events)

    rows: list[dict[str, Any]] = []
    for snap in snapshots:
        sid = str(snap.get("_id"))
        vals = meas_by_snap.get(sid, {})
        snap_alarms = alarms_by_snap.get(sid, [])
        row = {
            "session_id": session_id,
            "timestamp": _iso(snap.get("receivedAt")),
            "source": snap.get("source"),
            "connection_mode": mode,
            "fsm_state": snap.get("fsmState"),
            "display_state": snap.get("displayState"),
            "previous_fsm_state": snap.get("previousFsmState"),
            "transition_reason": snap.get("transitionReason"),
            "time_in_state_s": snap.get("timeInStateSeconds"),
            "aktueller_schritt": snap.get("aktuellerSchritt"),
            "sensor_ok": snap.get("sensorOk"),
            "emergency_stop": snap.get("emergencyStop"),
            "active_fault": snap.get("activeFault"),
            "alarm_active": bool(snap_alarms),
            "alarm_codes": "|".join(a.get("code", "") for a in snap_alarms),
            "alarm_severities": "|".join(a.get("severity", "") for a in snap_alarms),
            "alarm_messages": "|".join(a.get("message", "") for a in snap_alarms),
            "system_events": event_summary,
        }
        # Fill measurement columns (only those present in CSV_COLUMNS).
        for col in CSV_COLUMNS:
            if col in vals:
                row[col] = vals[col]
        rows.append(row)
    return rows


async def build_csv(session_id: str) -> str:
    """Render the logbook rows as a single CSV string."""
    rows = await build_rows(session_id)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


# Reduced column set used by the live logbook view in the GUI (FR-12). These
# are the "important" columns a demonstrator watches in real time.
REDUCED_COLUMNS = [
    "timestamp", "fsm_state", "aktueller_schritt",
    "K2_Temperatur", "K3_Temperatur", "MobilerSensor_Temperatur",
    "Durchfluss_NachgussMaische",
    "alarm_active", "alarm_codes", "alarm_severities",
]


async def preview(session_id: str, limit: int = 25) -> dict:
    """
    Return a small live preview for the GUI (FR-12).

    The MOST RECENT `limit` rows are returned (newest last) so the dashboard's
    logbook view updates in real time and the snapshot that caused an alarm
    (alarm_active = true) is visible as it happens. Both the full and the
    reduced column sets are reported so the client can choose.
    """
    rows = await build_rows(session_id)
    return {
        "sessionId": session_id,
        "columns": CSV_COLUMNS,
        "reducedColumns": REDUCED_COLUMNS,
        "totalRows": len(rows),
        "rows": rows[-limit:],
    }


def _iso(value: Any) -> Any:
    """Format a datetime as ISO-8601 for the CSV (passthrough otherwise)."""
    try:
        return value.isoformat()
    except AttributeError:
        return value
