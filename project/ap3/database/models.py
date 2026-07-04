"""
File: models.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Defines the MongoDB collection names and Pydantic models / enums that describe the documents stored at runtime. These models are also reused by the API layer for response shaping and validation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# --- Collection name constants ---------------------------------------------

COLLECTION_SESSIONS = "sessions"
COLLECTION_DATA_POINTS = "data_points"
COLLECTION_SNAPSHOTS = "snapshots"
COLLECTION_MEASUREMENTS = "measurements"
COLLECTION_FSM_STATES = "fsm_states"
COLLECTION_ALARMS = "alarms"
COLLECTION_SYSTEM_EVENTS = "system_events"
COLLECTION_SIMULATION_SCENARIOS = "simulation_scenarios"

# Runtime collections are wiped per-session on disconnect / reset.
RUNTIME_COLLECTIONS = [
    COLLECTION_SNAPSHOTS,
    COLLECTION_MEASUREMENTS,
    COLLECTION_FSM_STATES,
    COLLECTION_ALARMS,
    COLLECTION_SYSTEM_EVENTS,
]


# --- Enums ------------------------------------------------------------------

class ConnectionMode(str, Enum):
    REAL = "real"
    SIMULATION = "simulation"


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class AlarmSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlarmStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLEARED = "CLEARED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


class EventLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def utcnow() -> datetime:
    """Single source of truth for timestamps (timezone-aware UTC)."""
    return datetime.now(timezone.utc)


# --- API request models -----------------------------------------------------

class ConnectRequest(BaseModel):
    mode: ConnectionMode = ConnectionMode.SIMULATION
    opcuaEndpoint: Optional[str] = None
    scenario: Optional[str] = None


class SimulationStartRequest(BaseModel):
    scenario: str = "Normal process"


class ScenarioSelectRequest(BaseModel):
    scenario: str


# --- API response helpers ---------------------------------------------------

class SessionModel(BaseModel):
    sessionId: str
    mode: str
    scenario: Optional[str] = None
    status: str = SessionStatus.ACTIVE.value
    startedAt: datetime = Field(default_factory=utcnow)
    endedAt: Optional[datetime] = None


class SystemEvent(BaseModel):
    sessionId: str
    level: str = EventLevel.INFO.value
    eventType: str
    message: str
    createdAt: datetime = Field(default_factory=utcnow)
    details: Optional[dict[str, Any]] = None
