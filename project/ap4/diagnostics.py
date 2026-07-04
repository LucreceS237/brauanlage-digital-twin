"""
File: diagnostics.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: diagnostics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fault_catalog import FaultCode, descriptor_for


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    EMERGENCY = "emergency"


@dataclass(frozen=True)
class Diagnostic:
    """Ein konkreter, eindeutiger AP4-Fehlernachweis.

    `code` enthält nicht mehr nur eine generische Ursache, sondern einen eindeutigen
    Fehlerzustand wie `ERROR_005_K1_MASHING_TEMP_LOW`. AP5 und AP6 dürfen diesen
    Code als stabile Schnittstelle verwenden.
    """

    severity: Severity
    code: FaultCode
    message: str
    signal: str | None = None
    value: float | bool | str | None = None
    limit: float | str | None = None

    @property
    def code_text(self) -> str:
        return self.code.value

    @property
    def descriptor_title(self) -> str:
        return descriptor_for(self.code).title

    @property
    def display_state(self) -> str:
        return self.code.value

    def terminal_line(self) -> str:
        details = []
        if self.signal:
            details.append(f"signal={self.signal}")
        if self.value is not None:
            details.append(f"value={self.value}")
        if self.limit is not None:
            details.append(f"limit={self.limit}")
        suffix = " | " + ", ".join(details) if details else ""
        return f"[{self.severity.value.upper()}] {self.code.value}: {self.message}{suffix}"


def make_diagnostic(
    severity: Severity,
    code: FaultCode,
    signal: str | None = None,
    value: float | bool | str | None = None,
    limit: float | str | None = None,
    message: str | None = None,
) -> Diagnostic:
    desc = descriptor_for(code)
    return Diagnostic(
        severity=severity,
        code=code,
        message=message or desc.title,
        signal=signal,
        value=value,
        limit=limit,
    )
