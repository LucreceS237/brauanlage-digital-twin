# scripts/opcua_collector.py
# -*- coding: utf-8 -*-

"""
OPC-UA collector for the brewing digital twin.

This script:
1. connects to the Siemens S7-1500 OPC-UA server
2. reads validated data points from Engineer A
3. stores values in SQLite
4. keeps the database usable for Engineer C, D and E

Run:
    python scripts/opcua_collector.py
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from asyncua import Client
from dotenv import load_dotenv

from src.storage.database import BrewingDatabase
from src.storage.data_points import DATA_POINTS


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_enabled(value: str | None) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y"}


class OpcUaCollector:
    """
    Reads SPS values from OPC-UA and writes them into SQLite.

    The collector intentionally does not perform FSM or anomaly logic.
    It only collects trustworthy, timestamped data.
    """

    def __init__(self) -> None:
        load_dotenv()

        self.opcua_url = os.getenv(
            "OPCUA_SERVER_URL",
            "opc.tcp://192.168.0.1:4840",
        )

        self.db_path = os.getenv(
            "DATABASE_PATH",
            "data/brewing_data.db",
        )

        self.dynamic_interval = float(
            os.getenv("DYNAMIC_POLL_INTERVAL_SECONDS", "1")
        )

        self.context_interval = float(
            os.getenv("CONTEXT_POLL_INTERVAL_SECONDS", "60")
        )

        self.enable_optional = is_enabled(
            os.getenv("ENABLE_OPTIONAL_ACTUATORS", "false")
        )

        self.db = BrewingDatabase(self.db_path)

        self.dynamic_points = [
            dp for dp in DATA_POINTS
            if dp["poll_group"] == "dynamic"
        ]

        self.context_points = [
            dp for dp in DATA_POINTS
            if dp["poll_group"] == "context"
        ]

        self.optional_points = [
            dp for dp in DATA_POINTS
            if dp["poll_group"] == "optional"
        ]

        if self.enable_optional:
            self.dynamic_points += self.optional_points

        # Context values are read slowly, but cached so that
        # Engineer D always has access to last known limits.
        self.context_cache: Dict[str, Dict[str, Any]] = {}

    async def run_forever(self) -> None:
        """
        Run collector with reconnect loop.

        If the SPS connection fails, the script waits and reconnects.
        """

        backoff_seconds = 2

        while True:
            try:
                print(f"Connecting to OPC-UA server: {self.opcua_url}")

                async with Client(url=self.opcua_url) as client:
                    print("Connected to OPC-UA server.")

                    self.db.insert_system_event(
                        level="INFO",
                        event_type="OPCUA_CONNECTED",
                        message=f"Connected to {self.opcua_url}",
                    )

                    backoff_seconds = 2
                    await self._poll_loop(client)

            except Exception as exc:
                message = f"OPC-UA connection error: {exc}"
                print(message)

                self.db.insert_system_event(
                    level="ERROR",
                    event_type="OPCUA_CONNECTION_ERROR",
                    message=message,
                )

                print(f"Reconnect in {backoff_seconds} seconds...")
                await asyncio.sleep(backoff_seconds)

                backoff_seconds = min(backoff_seconds * 2, 30)

    async def _poll_loop(self, client: Client) -> None:
        """
        Main polling loop.

        Dynamic values:
            read every 1 second.

        Context values:
            read at startup and then every 60 seconds.
        """

        last_context_read = 0.0

        while True:
            loop_time = asyncio.get_event_loop().time()

            measurements: Dict[str, Dict[str, Any]] = {}

            # Read context values at startup and then periodically.
            if loop_time - last_context_read >= self.context_interval or not self.context_cache:
                context_measurements = await self._read_points(client, self.context_points)
                self.context_cache.update(context_measurements)
                last_context_read = loop_time

            # Read fast-changing SPS values.
            dynamic_measurements = await self._read_points(client, self.dynamic_points)

            # Store dynamic values for this snapshot.
            measurements.update(dynamic_measurements)

            # Also include cached context values in the database periodically.
            # This ensures that temperature limits are available for API/debugging.
            measurements.update(self.context_cache)

            snapshot_id = self.db.insert_snapshot(
                measurements=measurements,
                collector_status="OK",
                source="OPC-UA",
            )

            print(
                f"[{utc_now()}] Snapshot {snapshot_id} stored "
                f"with {len(measurements)} values."
            )

            await asyncio.sleep(self.dynamic_interval)

    async def _read_points(
        self,
        client: Client,
        points: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Read a list of OPC-UA nodes.

        Returns:
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

        result: Dict[str, Dict[str, Any]] = {}

        for dp in points:
            name = dp["name"]
            node_id = dp["node_id"]

            try:
                node = client.get_node(node_id)
                data_value = await node.read_data_value()

                value = data_value.Value.Value
                quality = str(data_value.StatusCode)

                source_timestamp = (
                    data_value.SourceTimestamp.isoformat()
                    if data_value.SourceTimestamp
                    else None
                )

                server_timestamp = (
                    data_value.ServerTimestamp.isoformat()
                    if data_value.ServerTimestamp
                    else None
                )

                result[name] = {
                    "value": value,
                    "quality": quality,
                    "timestamp": utc_now(),
                    "source_timestamp": source_timestamp,
                    "server_timestamp": server_timestamp,
                }

            except Exception as exc:
                error_message = f"Failed reading {name}: {exc}"
                print(error_message)

                self.db.insert_system_event(
                    level="ERROR",
                    event_type="NODE_READ_ERROR",
                    message=error_message,
                )

        return result


async def main() -> None:
    db = BrewingDatabase("data/brewing_data.db")
    db.initialize("database/schema.sql")
    db.seed_data_points(DATA_POINTS)

    collector = OpcUaCollector()
    await collector.run_forever()


if __name__ == "__main__":
    asyncio.run(main())