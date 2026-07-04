"""
File: mongodb.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Owns the single MongoDB connection (Motor async client) for the whole backend and exposes typed collection accessors. Also creates the runtime collections and indexes after a connection/simulation start, and provides a helper to wipe all runtime data for a given session (used on disconnect / scenario reset).
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from project.ap3.config import settings
from project.ap3.database.models import (
    COLLECTION_ALARMS,
    COLLECTION_DATA_POINTS,
    COLLECTION_FSM_STATES,
    COLLECTION_MEASUREMENTS,
    COLLECTION_SESSIONS,
    COLLECTION_SIMULATION_SCENARIOS,
    COLLECTION_SNAPSHOTS,
    COLLECTION_SYSTEM_EVENTS,
    RUNTIME_COLLECTIONS,
)

# Module-level singletons set during connect().
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect() -> None:
    """Open the MongoDB connection. Called once on FastAPI startup."""
    global _client, _db
    if _client is not None:
        return
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db_name]


async def disconnect() -> None:
    """Close the MongoDB connection. Called on FastAPI shutdown."""
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    """Return the active database handle (raises if not connected yet)."""
    if _db is None:
        raise RuntimeError("MongoDB is not connected. Call connect() first.")
    return _db


# --- Collection accessors (thin wrappers for readability) -------------------

def sessions():
    return get_db()[COLLECTION_SESSIONS]


def data_points():
    return get_db()[COLLECTION_DATA_POINTS]


def snapshots():
    return get_db()[COLLECTION_SNAPSHOTS]


def measurements():
    return get_db()[COLLECTION_MEASUREMENTS]


def fsm_states():
    return get_db()[COLLECTION_FSM_STATES]


def alarms():
    return get_db()[COLLECTION_ALARMS]


def system_events():
    return get_db()[COLLECTION_SYSTEM_EVENTS]


def simulation_scenarios():
    return get_db()[COLLECTION_SIMULATION_SCENARIOS]


# --- Initialization & cleanup ----------------------------------------------

async def init_collections() -> None:
    """
    FR-02: ensure the runtime collections exist and have helpful indexes.

    MongoDB creates collections lazily, but we create indexes eagerly so that
    queries by sessionId and time stay fast even with many snapshots.
    """
    db = get_db()
    await db[COLLECTION_SNAPSHOTS].create_index([("sessionId", 1), ("receivedAt", 1)])
    await db[COLLECTION_MEASUREMENTS].create_index([("sessionId", 1), ("snapshotId", 1)])
    await db[COLLECTION_MEASUREMENTS].create_index([("sessionId", 1), ("name", 1), ("timestamp", 1)])
    await db[COLLECTION_FSM_STATES].create_index([("sessionId", 1), ("createdAt", 1)])
    await db[COLLECTION_ALARMS].create_index([("sessionId", 1), ("status", 1)])
    await db[COLLECTION_SYSTEM_EVENTS].create_index([("sessionId", 1), ("createdAt", 1)])
    await db[COLLECTION_SESSIONS].create_index([("sessionId", 1)], unique=True)


async def delete_runtime_data(session_id: str) -> dict[str, int]:
    """
    FR-09 / FR-10: delete every runtime document belonging to one session.

    Static data (data_points, simulation_scenarios) is intentionally NOT
    touched here so it can be reused / re-seeded across runs.

    Returns a map of collection -> number of deleted documents (for the event
    log and the API response).
    """
    db = get_db()
    deleted: dict[str, int] = {}
    for name in RUNTIME_COLLECTIONS:
        result = await db[name].delete_many({"sessionId": session_id})
        deleted[name] = result.deleted_count
    return deleted
