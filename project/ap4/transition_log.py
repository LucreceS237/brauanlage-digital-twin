"""
File: transition_log.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: transition_log.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .fsm_contract import TransitionRecord


class TransitionLogger:
    """Persistiert Transitionen mit eindeutigen Fehlercodes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write_csv(self, records: Iterable[TransitionRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, delimiter=";")
            writer.writerow(["counter", "old_state", "new_state", "display_state", "reason_code", "active_fault_code", "message", "time_in_old_state_s"])
            for record in records:
                writer.writerow([record.counter, record.old_state.name, record.new_state.name, record.display_state, record.reason_code, record.active_fault_code or "", record.message, f"{record.time_in_old_state_s:.2f}"])
