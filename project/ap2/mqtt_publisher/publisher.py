"""
File: publisher.py
Work Package: AP2
Responsible Engineer: Engineer A
Purpose: Dockerized MQTT publisher orchestrator (FAKE_PUBLISHER | REAL_SPS).
"""
from __future__ import annotations

import json
import logging
import os
import time

import paho.mqtt.client as mqtt

from fake_publisher import FakePublisher
from real_sps_reader import RealSpsReader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mqtt_publisher")

MODE = os.getenv("PUBLISHER_MODE", "FAKE_PUBLISHER").upper()
BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "brauanlage/sps/live")
OPCUA_URL = os.getenv("OPCUA_SERVER_URL", "opc.tcp://192.168.0.1:4840")
SIM_SCENARIO = os.getenv("SIMULATION_SCENARIO", "NORMAL_PROCESS")
SIM_SPEED = float(os.getenv("SIMULATION_SPEED_FACTOR", "1"))
SIM_TOTAL = float(os.getenv("SIMULATION_TOTAL_DURATION_SECONDS", "1800"))
PUBLISH_INTERVAL = float(os.getenv("SIMULATION_TICK_SECONDS", "1"))


def make_client() -> mqtt.Client:
    client = mqtt.Client()
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.on_connect = lambda c, u, f, rc: logger.info(
        "Connected to MQTT broker %s:%s (rc=%s)", BROKER_HOST, BROKER_PORT, rc)
    client.on_disconnect = lambda c, u, rc: (
        logger.warning("Disconnected from broker (rc=%s); auto-reconnecting", rc) if rc else None)
    return client


def connect_broker(client: mqtt.Client) -> None:
    while True:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)
            client.loop_start()
            return
        except OSError as exc:
            logger.warning("Broker %s:%s not reachable (%s); retry in 3s", BROKER_HOST, BROKER_PORT, exc)
            time.sleep(3)


def publish(client: mqtt.Client, payload: dict) -> None:
    try:
        client.publish(TOPIC, json.dumps(payload), qos=0)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to publish MQTT message")


def run_fake(client: mqtt.Client) -> None:
    logger.info(
        "FAKE_PUBLISHER mode: scenario=%s speed=%sx duration=%ss source=Fake_SPS topic=%s",
        SIM_SCENARIO, SIM_SPEED, SIM_TOTAL, TOPIC,
    )
    src = FakePublisher(scenario=SIM_SCENARIO, total_duration_seconds=SIM_TOTAL, speed_factor=SIM_SPEED)
    while True:
        publish(client, src.next_payload())
        src.advance(PUBLISH_INTERVAL)
        time.sleep(PUBLISH_INTERVAL)


def run_real(client: mqtt.Client) -> None:
    logger.info("REAL_SPS mode: reading %s and publishing real values (source=REAL_SPS) to %s", OPCUA_URL, TOPIC)
    reader = RealSpsReader(OPCUA_URL)
    while True:
        try:
            reader.connect()
            while True:
                publish(client, reader.read_payload())
                time.sleep(PUBLISH_INTERVAL)
        except Exception as exc:  # noqa: BLE001
            logger.warning("SPS connection lost (%s); publishing DISCONNECTED, retry in 3s", exc)
            publish(client, reader.disconnected_payload())
            reader.disconnect()
            time.sleep(3)


def main() -> None:
    client = make_client()
    connect_broker(client)
    try:
        if MODE == "REAL_SPS":
            run_real(client)
        else:
            run_fake(client)
    except KeyboardInterrupt:
        logger.info("Publisher stopped by user")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
