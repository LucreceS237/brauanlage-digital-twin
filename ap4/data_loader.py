from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterator

from .process_snapshot import ProcessSnapshot


def load_snapshots_from_csv(path: str | Path) -> list[ProcessSnapshot]:
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [ProcessSnapshot.from_dict(row) for row in reader]


def iter_snapshots_from_sqlite(path: str | Path, table: str = "process_snapshots") -> Iterator[ProcessSnapshot]:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        for row in con.execute(f"SELECT * FROM {table} ORDER BY timestamp"):
            yield ProcessSnapshot.from_dict(dict(row))
    finally:
        con.close()