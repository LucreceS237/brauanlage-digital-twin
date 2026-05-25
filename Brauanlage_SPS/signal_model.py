from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class NodePriority(Enum):
    NORMAL = "normal"
    TOP_PFLICHT = "top_pflicht"          # hellgelb markiert im Top-Blatt
    PARAMETER_LIMIT = "parameter_limit"  # blassgelb markierte Soll-/Grenzwerte
    NEEDS_REVIEW = "needs_review"        # orange markiert: Messwert prüfen
    RELEVANCE_MARKED = "relevance_marked"  # grün/thematisch markierte Relevanzzelle


@dataclass(frozen=True)
class NodeDefinition:
    original_no: int | None
    node_id: str
    namespace: str | None
    node_path: str | None
    browse_name: str | None
    display_name: str | None
    area: str | None
    component: str | None
    quantity: str | None
    datatype: str | None
    category: str | None
    unit: str | None
    polling_mode: str | None
    polling_interval_s: float | None
    mandatory_status: str | None
    validation_status: str | None
    project_access: str | None
    use_collector: bool
    use_fsm: bool
    use_anomaly: bool
    use_api: bool
    api_name: str
    description: str | None
    comment: str | None
    priority: NodePriority = NodePriority.NORMAL


@dataclass(frozen=True)
class SignalValue:
    api_name: str
    value: Any
    quality_good: bool = True
    age_s: float = 0.0