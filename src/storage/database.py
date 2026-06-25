# src/storage/database.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BrewingDatabase:
    """
    SQLite access layer for the brewing digital twin.

    This class is intentionally simple:
    - no SQLAlchemy
    - no server dependency
    - easy to explain in the presentation
    """

    def __init__(self, db_path: str = "data/brewing_data.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize(self, schema_path: str = "database/schema.sql") -> None:
        with self.connect() as conn:
            schema = Path(schema_path).read_text(encoding="utf-8")
            conn.executescript(schema)
            conn.commit()

    def seed_data_points(self, data_points: Iterable[Dict[str, Any]]) -> None:
        """
        Insert or update the OPC-UA node configuration from Engineer A.
        """

        sql = """
        INSERT INTO data_points (
            name, node_id, data_type, unit, component, category,
            source_block, poll_group, poll_interval_s,
            is_required, is_context, use_in_fsm, use_in_api, use_in_anomaly,
            validation_status, validation_note
        )
        VALUES (
            :name, :node_id, :data_type, :unit, :component, :category,
            :source_block, :poll_group, :poll_interval_s,
            :is_required, :is_context, :use_in_fsm, :use_in_api, :use_in_anomaly,
            :validation_status, :validation_note
        )
        ON CONFLICT(name) DO UPDATE SET
            node_id = excluded.node_id,
            data_type = excluded.data_type,
            unit = excluded.unit,
            component = excluded.component,
            category = excluded.category,
            source_block = excluded.source_block,
            poll_group = excluded.poll_group,
            poll_interval_s = excluded.poll_interval_s,
            is_required = excluded.is_required,
            is_context = excluded.is_context,
            use_in_fsm = excluded.use_in_fsm,
            use_in_api = excluded.use_in_api,
            use_in_anomaly = excluded.use_in_anomaly,
            validation_status = excluded.validation_status,
            validation_note = excluded.validation_note;
        """

        with self.connect() as conn:
            conn.executemany(sql, list(data_points))
            conn.commit()

    def get_data_points(self, poll_group: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            if poll_group:
                rows = conn.execute(
                    "SELECT * FROM data_points WHERE poll_group = ? ORDER BY id",
                    (poll_group,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM data_points ORDER BY id"
                ).fetchall()

        return [dict(row) for row in rows]

    def insert_snapshot(
        self,
        measurements: Dict[str, Dict[str, Any]],
        collector_status: str = "OK",
        source: str = "OPC-UA",
        fsm_state: Optional[str] = None,
    ) -> int:
        """
        Insert one polling cycle.

        measurements format:
        {
            "K2_Temperatur": {
                "value": 68.5,
                "quality": "Good",
                "timestamp": "...",
                "source_timestamp": "...",
                "server_timestamp": "..."
            }
        }
        """

        received_at = utc_now()
        aktueller_schritt = measurements.get("Aktueller_Schritt", {}).get("value")

        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO snapshots (
                    received_at, source, collector_status, aktueller_schritt, fsm_state
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    received_at,
                    source,
                    collector_status,
                    self._safe_int(aktueller_schritt),
                    fsm_state,
                ),
            )

            snapshot_id = cur.lastrowid

            for name, payload in measurements.items():
                dp = conn.execute(
                    "SELECT id, data_type FROM data_points WHERE name = ?",
                    (name,),
                ).fetchone()

                if dp is None:
                    self.insert_system_event(
                        level="WARNING",
                        event_type="UNKNOWN_DATA_POINT",
                        message=f"Unknown data point received: {name}",
                        snapshot_id=snapshot_id,
                    )
                    continue

                value = payload.get("value")
                value_real, value_int, value_bool, value_text = self._split_value(value)

                conn.execute(
                    """
                    INSERT INTO measurements (
                        snapshot_id, data_point_id, timestamp,
                        value_real, value_int, value_bool, value_text,
                        quality, source_timestamp, server_timestamp
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        dp["id"],
                        payload.get("timestamp", received_at),
                        value_real,
                        value_int,
                        value_bool,
                        value_text,
                        payload.get("quality"),
                        payload.get("source_timestamp"),
                        payload.get("server_timestamp"),
                    ),
                )

            conn.commit()

        return int(snapshot_id)

    def get_latest_snapshot(self) -> Dict[str, Any]:
        """
        Return latest values as a flat dictionary.

        This is exactly what Engineer C, D and E need:
        - Engineer C: FSM input
        - Engineer D: anomaly detector input
        - Engineer E: API status response
        """

        with self.connect() as conn:
            snapshot = conn.execute(
                "SELECT * FROM snapshots ORDER BY id DESC LIMIT 1"
            ).fetchone()

            rows = conn.execute(
                """
                SELECT
                    dp.name,
                    dp.unit,
                    dp.component,
                    dp.validation_status,
                    m.timestamp,
                    m.value_real,
                    m.value_int,
                    m.value_bool,
                    m.value_text,
                    m.quality
                FROM measurements m
                JOIN data_points dp ON dp.id = m.data_point_id
                JOIN (
                    SELECT data_point_id, MAX(id) AS latest_measurement_id
                    FROM measurements
                    GROUP BY data_point_id
                ) latest
                ON latest.latest_measurement_id = m.id
                ORDER BY dp.id
                """
            ).fetchall()

            active_alarms = conn.execute(
                "SELECT * FROM alarms WHERE status = 'ACTIVE' ORDER BY created_at DESC"
            ).fetchall()

        result: Dict[str, Any] = {
            "_received_at": snapshot["received_at"] if snapshot else utc_now(),
            "state": snapshot["fsm_state"] if snapshot and snapshot["fsm_state"] else "UNKNOWN",
            "_meta": {},
            "alarms": [dict(row) for row in active_alarms],
        }

        for row in rows:
            value = self._merge_value(row)
            result[row["name"]] = value
            result["_meta"][row["name"]] = {
                "timestamp": row["timestamp"],
                "quality": row["quality"],
                "unit": row["unit"],
                "component": row["component"],
                "validation_status": row["validation_status"],
            }

        return result

    def insert_alarm(self, alarm: Dict[str, Any], snapshot_id: Optional[int] = None) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO alarms (
                    snapshot_id, rule_id, code, severity, state, component,
                    variable, value, threshold, message, status, created_at, cleared_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    alarm.get("rule_id"),
                    alarm.get("code"),
                    alarm.get("severity"),
                    alarm.get("state"),
                    alarm.get("component"),
                    alarm.get("variable"),
                    str(alarm.get("value")),
                    str(alarm.get("threshold")),
                    alarm.get("message"),
                    alarm.get("status", "ACTIVE"),
                    alarm.get("timestamp", utc_now()),
                    alarm.get("cleared_at"),
                ),
            )
            conn.commit()

    def insert_system_event(
        self,
        level: str,
        event_type: str,
        message: str,
        snapshot_id: Optional[int] = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO system_events (
                    snapshot_id, created_at, level, event_type, message
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (snapshot_id, utc_now(), level, event_type, message),
            )
            conn.commit()

    def _split_value(self, value: Any):
        """
        Store Python values into SQLite-compatible columns.

        SQLite has dynamic typing, but separating real/int/bool/text
        makes later queries easier.
        """

        if isinstance(value, bool):
            return None, None, int(value), None

        if isinstance(value, int):
            return None, value, None, None

        if isinstance(value, float):
            return value, None, None, None

        if value is None:
            return None, None, None, None

        return None, None, None, str(value)

    def _merge_value(self, row: sqlite3.Row) -> Any:
        if row["value_bool"] is not None:
            return bool(row["value_bool"])
        if row["value_real"] is not None:
            return row["value_real"]
        if row["value_int"] is not None:
            return row["value_int"]
        return row["value_text"]

    def _safe_int(self, value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None