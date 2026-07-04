"""
File: alarm_service.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Alarm persistence and lifecycle (dedupe, auto-clear, acknowledge). AP4 process faults arrive as Alarm objects via ap4_alarm_adapter; AP5 extra rules via detector.
"""
from __future__ import annotations

from typing import Optional

from project.ap3.database import mongodb
from project.ap3.database.models import AlarmStatus, utcnow
from project.ap3.utils.serialization import clean_doc
from project.ap5.anomaly_detection.alarm import Alarm


async def sync_alarms(
    session_id: str,
    snapshot_id: Optional[str],
    fired: list[Alarm],
) -> list[dict]:
    coll = mongodb.alarms()
    fired_keys = {(a.ruleId, a.variable) for a in fired}
    active_docs = await coll.find(
        {"sessionId": session_id, "status": AlarmStatus.ACTIVE.value}
    ).to_list(length=500)
    active_keys = {(d["ruleId"], d["variable"]) for d in active_docs}

    created: list[dict] = []
    for alarm in fired:
        if (alarm.ruleId, alarm.variable) not in active_keys:
            doc = alarm.to_doc(session_id, snapshot_id)
            await coll.insert_one(doc)
            created.append(clean_doc(doc))

    for doc in active_docs:
        if (doc["ruleId"], doc["variable"]) not in fired_keys:
            await coll.update_one(
                {"_id": doc["_id"]},
                {"$set": {"status": AlarmStatus.CLEARED.value, "clearedAt": utcnow()}},
            )
    return created


async def get_active(session_id: str) -> list[dict]:
    docs = await mongodb.alarms().find(
        {"sessionId": session_id, "status": AlarmStatus.ACTIVE.value}
    ).sort("createdAt", -1).to_list(length=200)
    return [clean_doc(d) for d in docs]


async def get_history(session_id: str) -> list[dict]:
    docs = await mongodb.alarms().find({"sessionId": session_id}).sort("createdAt", -1).to_list(length=1000)
    return [clean_doc(d) for d in docs]


async def acknowledge(session_id: str, alarm_id: str) -> bool:
    from bson import ObjectId

    try:
        oid = ObjectId(alarm_id)
    except Exception:  # noqa: BLE001
        return False
    result = await mongodb.alarms().update_one(
        {"_id": oid, "sessionId": session_id},
        {"$set": {"status": AlarmStatus.ACKNOWLEDGED.value, "clearedAt": utcnow()}},
    )
    return result.modified_count > 0
