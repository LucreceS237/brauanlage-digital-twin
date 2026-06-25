from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    EMERGENCY = "emergency"


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str