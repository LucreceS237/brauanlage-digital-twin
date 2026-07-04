"""
File: payload_builder.py
Work Package: shared
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Build MQTT-compatible SPS payloads with a consistent envelope.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_sps_payload(
    values: dict[str, Any],
    *,
    source: str,
    publisher_mode: str,
    connection_status: str,
    simulation_phase: str,
    sps_endpoint: str = "",
) -> dict[str, Any]:
    """Wrap process values into the standard brauanlage/sps/live payload."""
    return {
        "timestamp": now_iso(),
        "source": source,
        "publisherMode": publisher_mode,
        "connectionStatus": connection_status,
        "simulationPhase": simulation_phase,
        "spsEndpoint": sps_endpoint,
        "values": values,
    }
