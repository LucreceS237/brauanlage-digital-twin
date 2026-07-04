"""
File: mqtt_client.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Subscribes to brauanlage/sps/live and keeps the latest VALID MQTT payload. Invalid payloads are queued for the collector to log as system events.
"""
from __future__ import annotations

import json
import logging
import socket
import threading
import time
from collections import deque
from typing import Optional

import paho.mqtt.client as mqtt

from project.ap3.mqtt.payload_validator import validate_payload

logger = logging.getLogger(__name__)


class MqttClient:
    def __init__(self, host: str, port: int, topic: str) -> None:
        self.host = host
        self.port = port
        self.topic = topic
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)
        self._lock = threading.Lock()
        self._latest_payload: Optional[dict] = None
        self._latest_monotonic: float = 0.0
        self._first_valid = threading.Event()
        self.invalid_events: deque = deque(maxlen=100)
        self.valid_count = 0
        self.invalid_count = 0
        self.connected = False

    def connect(self) -> None:
        self._client.connect(self.host, self.port, keepalive=30)
        self._client.loop_start()

    def disconnect(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:  # noqa: BLE001
            logger.warning("Error disconnecting MQTT client", exc_info=True)
        self.connected = False

    def broker_available(self, timeout: float = 2.0) -> bool:
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except OSError:
            return False

    async def wait_for_first_valid(self, timeout: float) -> bool:
        import asyncio

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._first_valid.is_set():
                return True
            await asyncio.sleep(0.1)
        return self._first_valid.is_set()

    def latest(self) -> tuple[Optional[dict], float]:
        with self._lock:
            if self._latest_payload is None:
                return None, float("inf")
            age = time.monotonic() - self._latest_monotonic
            return dict(self._latest_payload), age

    def drain_invalid(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        while self.invalid_events:
            out.append(self.invalid_events.popleft())
        return out

    def _on_connect(self, client, userdata, flags, rc):  # noqa: ANN001
        self.connected = rc == 0
        if rc == 0:
            client.subscribe(self.topic, qos=0)
            logger.info("MQTT connected; subscribed to %s", self.topic)

    def _on_disconnect(self, client, userdata, rc):  # noqa: ANN001
        self.connected = False

    def _on_message(self, client, userdata, msg):  # noqa: ANN001
        try:
            raw = json.loads(msg.payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            self.invalid_count += 1
            self.invalid_events.append(("JSON_DECODE_ERROR", str(exc)))
            return
        ok, reason = validate_payload(raw)
        if not ok:
            self.invalid_count += 1
            self.invalid_events.append(("INVALID_PAYLOAD", reason or "invalid"))
            return
        with self._lock:
            self._latest_payload = raw
            self._latest_monotonic = time.monotonic()
        self.valid_count += 1
        self._first_valid.set()
