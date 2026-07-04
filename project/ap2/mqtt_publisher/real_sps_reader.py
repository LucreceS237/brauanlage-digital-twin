"""
File: real_sps_reader.py
Work Package: AP2
Responsible Engineer: Engineer A
Purpose: REAL publisher source. Reads live values from the SPS over OPC-UA (asyncua) and wraps them in the MQTT payload envelope with source="REAL_SPS", publisherMode="REAL". If the SPS is unreachable it reports a DISCONNECTED payload instead of inventing values (no silent fallback to fake data).
"""
from __future__ import annotations

import logging

from data_points import NODE_IDS, build_payload

logger = logging.getLogger("mqtt_publisher.real")


class RealSpsReader:
    """Reads the SPS via OPC-UA and produces REAL payloads."""

    def __init__(self, opcua_url: str) -> None:
        self.opcua_url = opcua_url
        self._client = None
        self._nodes: dict = {}

    def connect(self) -> None:
        """Open the OPC-UA connection and resolve nodes. Raises on failure."""
        from asyncua.sync import Client  # lazy import; FAKE mode needs no SPS

        self._client = Client(url=self.opcua_url)
        self._client.connect()
        self._nodes = {name: self._client.get_node(nid) for name, nid in NODE_IDS.items()}
        logger.info("Connected to SPS at %s", self.opcua_url)

    def disconnect(self) -> None:
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:  # noqa: BLE001
                pass
            self._client = None
            self._nodes = {}

    def read_payload(self) -> dict:
        """Read all nodes and build a REAL payload. Raises if not connected."""
        if self._client is None:
            raise ConnectionError("SPS not connected")
        values = {}
        for name, node in self._nodes.items():
            try:
                values[name] = node.read_value()
            except Exception:  # noqa: BLE001 - tolerate individual bad reads
                logger.debug("Failed reading %s", name, exc_info=True)
        return build_payload(
            values, source="REAL_SPS", publisher_mode="REAL",
            connection_status="CONNECTED", sps_endpoint=self.opcua_url,
        )

    def disconnected_payload(self) -> dict:
        """A REAL-mode payload that honestly reports the SPS is down."""
        return build_payload(
            {}, source="REAL_SPS", publisher_mode="REAL",
            connection_status="DISCONNECTED", sps_endpoint=self.opcua_url,
        )
