"""
File: collector_service.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Runtime orchestration loop: acquire (MQTT or simulation) -> AP5 FSM (AP4) -> AP5 alarms -> AP3 storage
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from project.ap3.config import settings
from project.ap3.database import mongodb
from project.ap3.database.models import ConnectionMode, EventLevel, utcnow
from project.ap3.mqtt.mqtt_client import MqttClient
from project.ap3.services import session_service, storage_service
from project.ap3.simulation.simulator import ProcessSimulator
from project.ap3.utils.serialization import clean_doc
from project.ap5.anomaly_detection.detector import Ap5Detector
from project.ap5.services import alarm_service
from project.ap5.services.fsm_integration_service import FsmIntegrationService

logger = logging.getLogger(__name__)


class SpsConnectionError(Exception):
    """Raised when the real-SPS (MQTT) connection cannot be established."""


def normalize_values(values: dict[str, Any]) -> dict[str, Any]:
    out = dict(values)
    if "aktueller_schritt" in out and "Aktueller_Schritt" not in out:
        out["Aktueller_Schritt"] = out.pop("aktueller_schritt")
    return out


class RuntimeState:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.active = False
        self.mode: Optional[str] = None
        self.session: Optional[dict] = None
        self.simulator: Optional[ProcessSimulator] = None
        self.mqtt: Optional[MqttClient] = None
        self.fsm: Optional[FsmIntegrationService] = None
        self.detector: Optional[Ap5Detector] = None
        self.task: Optional[asyncio.Task] = None
        self.pending_acknowledge = False
        self.latest_snapshot: Optional[dict] = None
        self.latest_measurements: list[dict] = []
        self.latest_fsm: Optional[dict] = None
        self.latest_payload: Optional[dict] = None
        self.endpoint: Optional[str] = None
        self.connection_status = "DISCONNECTED"
        self.publisher_mode: Optional[str] = None
        self.source: Optional[str] = None

    @property
    def session_id(self) -> Optional[str]:
        return self.session["sessionId"] if self.session else None


runtime = RuntimeState()


async def start(mode: ConnectionMode, scenario: str | None, endpoint: str | None) -> dict:
    if runtime.active:
        await stop(delete_runtime=False)

    await mongodb.init_collections()
    session = await session_service.create_session(
        mode=mode.value, scenario=scenario if mode == ConnectionMode.SIMULATION else None
    )
    runtime.session = session
    runtime.mode = mode.value
    runtime.fsm = FsmIntegrationService(demo_mode=True)
    runtime.detector = Ap5Detector(expected_mode="REAL" if mode == ConnectionMode.REAL else "SIMULATION")
    runtime.pending_acknowledge = False
    runtime.publisher_mode = "SIMULATION" if mode == ConnectionMode.SIMULATION else None
    runtime.source = "SIMULATION" if mode == ConnectionMode.SIMULATION else None

    if mode == ConnectionMode.SIMULATION:
        runtime.simulator = ProcessSimulator(
            scenario=scenario or settings.simulation_scenario,
            total_duration_seconds=settings.simulation_total_duration_seconds,
            tick_seconds=settings.simulation_tick_seconds,
            speed_factor=settings.simulation_speed_factor,
        )
        runtime.connection_status = "SIMULATION"
        await session_service.log_event(session["sessionId"], "SIMULATION_STARTED",
                                        f"Simulation mode started successfully (scenario: {scenario}).")
    else:
        runtime.endpoint = f"mqtt://{settings.mqtt_broker_host}:{settings.mqtt_broker_port}/{settings.mqtt_topic}"
        client = MqttClient(settings.mqtt_broker_host, settings.mqtt_broker_port, settings.mqtt_topic)
        runtime.mqtt = client
        if not client.broker_available():
            await _fail_start(session["sessionId"], "Connection failed – MQTT broker is not reachable.")
        try:
            client.connect()
        except Exception as exc:  # noqa: BLE001
            await _fail_start(session["sessionId"], f"Connection failed – cannot connect to MQTT broker ({exc}).")
        if not await client.wait_for_first_valid(settings.sps_message_timeout_seconds):
            await _fail_start(session["sessionId"],
                              "Connection failed – no valid SPS data received from MQTT publisher.")
        payload, _ = client.latest()
        runtime.publisher_mode = payload.get("publisherMode") if payload else "REAL"
        runtime.source = payload.get("source") if payload else "REAL_SPS"
        runtime.connection_status = "CONNECTED"
        await session_service.log_event(session["sessionId"], "SPS_CONNECTED",
                                        "Connection successful – live SPS data received via MQTT.")

    runtime.active = True
    runtime.task = asyncio.create_task(_loop())
    return session


async def _fail_start(session_id: str, message: str) -> None:
    await session_service.log_event(session_id, "SPS_CONNECT_FAILED", message, level=EventLevel.ERROR)
    if runtime.mqtt is not None:
        runtime.mqtt.disconnect()
    await session_service.end_session(session_id)
    await mongodb.sessions().delete_one({"sessionId": session_id})
    runtime.reset()
    raise SpsConnectionError(message)


async def stop(delete_runtime: bool = True) -> dict[str, int]:
    deleted: dict[str, int] = {}
    runtime.active = False
    if runtime.task is not None:
        runtime.task.cancel()
        try:
            await runtime.task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass
        runtime.task = None
    session_id = runtime.session_id
    if runtime.mqtt is not None:
        runtime.mqtt.disconnect()
    if session_id is not None:
        if delete_runtime:
            deleted = await session_service.cleanup_runtime(session_id)
        await session_service.end_session(session_id)
    runtime.reset()
    return deleted


def request_acknowledge() -> None:
    runtime.pending_acknowledge = True
    if runtime.simulator is not None:
        runtime.simulator.acknowledge()


async def _loop() -> None:
    interval = settings.collector_interval_seconds
    while runtime.active:
        try:
            await _cycle()
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Collector cycle failed")
        await asyncio.sleep(interval)


async def _cycle() -> None:
    fsm_svc = runtime.fsm
    detector = runtime.detector
    session_id = runtime.session_id
    if fsm_svc is None or detector is None or session_id is None:
        return

    payload, values, missing_age = await _acquire(session_id)
    if values is None:
        return

    if runtime.pending_acknowledge:
        values = dict(values)
        values["acknowledge"] = True
        runtime.pending_acknowledge = False

    fsm_update = fsm_svc.update(values, dt_s=settings.collector_interval_seconds,
                                missing_value_age_s=missing_age)
    extra_alarms = detector.evaluate(payload or {"values": values, "source": runtime.source or "SIMULATION"},
                                     fsm_update.state)
    all_alarms = list(fsm_update.alarms) + extra_alarms

    snapshot_id, measurements, snapshot_doc = await storage_service.store_snapshot(
        session_id,
        source=runtime.source or (payload or {}).get("source", "SIMULATION"),
        publisher_mode=runtime.publisher_mode or (payload or {}).get("publisherMode", "SIMULATION"),
        connection_status=runtime.connection_status,
        collector_status="STALE" if missing_age > settings.sps_message_timeout_seconds else "OK",
        fsm_state=fsm_update.state,
        display_state=fsm_update.display_state,
        previous_state=fsm_update.previous_state,
        transition_reason=fsm_update.reason_code,
        time_in_state_s=fsm_update.time_in_state_s,
        values=values,
        emergency_stop=bool(values.get("emergency_stop", False)),
        acknowledge=bool(values.get("acknowledge", False)),
        sensor_ok=bool(values.get("sensor_ok", True)),
        active_fault=fsm_update.active_fault_code is not None,
    )

    if fsm_update.changed:
        await storage_service.store_fsm_transition(
            session_id, snapshot_id,
            current_state=fsm_update.state,
            display_state=fsm_update.display_state,
            previous_state=fsm_update.previous_state,
            transition_reason=fsm_update.reason_code,
        )
        await session_service.log_event(
            session_id, "FSM_TRANSITION",
            f"{fsm_update.previous_state} -> {fsm_update.display_state}: {fsm_update.reason_code}",
        )

    created = await alarm_service.sync_alarms(session_id, snapshot_id, all_alarms)
    for alarm in created:
        await session_service.log_event(session_id, "ALARM_RAISED",
                                        f"[{alarm['severity']}] {alarm['code']}: {alarm['message']}",
                                        level=EventLevel.WARNING)

    runtime.latest_payload = payload
    runtime.latest_snapshot = clean_doc({**snapshot_doc, "_id": snapshot_id})
    runtime.latest_measurements = [clean_doc(m) for m in measurements]
    runtime.latest_fsm = {
        "current_state": fsm_update.state,
        "display_state": fsm_update.display_state,
        "previous_state": fsm_update.previous_state,
        "transition_reason": fsm_update.reason_code,
        "time_in_state": round(fsm_update.time_in_state_s, 2),
        "active_fault_code": fsm_update.active_fault_code,
        "acknowledge_required": fsm_update.state in {"ERROR", "EMERGENCY"},
    }


async def _acquire(session_id: str) -> tuple[Optional[dict], Optional[dict], float]:
    if runtime.simulator is not None and runtime.fsm is not None:
        ctx = runtime.simulator.next_values(runtime.fsm.current_state,
                                            runtime.fsm.machine.time_in_state_s)
        missing_age = 999.0 if ctx.get("_stale") else 0.0
        values = normalize_values({k: v for k, v in ctx.items() if not str(k).startswith("_")})
        payload = {
            "source": "SIMULATION",
            "publisherMode": "SIMULATION",
            "connectionStatus": "SIMULATION",
            "simulationPhase": runtime.simulator.current_phase,
            "values": values,
        }
        return payload, values, missing_age

    client = runtime.mqtt
    assert client is not None
    for event_type, reason in client.drain_invalid():
        await session_service.log_event(session_id, "SPS_INVALID_PAYLOAD",
                                        f"Discarded invalid MQTT payload ({event_type}): {reason}",
                                        level=EventLevel.WARNING)
        if runtime.detector is not None:
            runtime.detector.evaluate({"values": {}}, runtime.fsm.current_state if runtime.fsm else "IDLE",
                                      invalid_payload=True, invalid_reason=reason)

    payload, age = client.latest()
    if payload is None:
        runtime.connection_status = "CONNECTING"
        return None, None, float("inf")

    runtime.publisher_mode = payload.get("publisherMode")
    runtime.source = payload.get("source")
    if age > settings.sps_message_timeout_seconds:
        runtime.connection_status = "STALE"
    elif str(payload.get("connectionStatus", "")).upper() == "DISCONNECTED":
        runtime.connection_status = "DISCONNECTED"
    else:
        runtime.connection_status = "CONNECTED"

    values = normalize_values(dict(payload.get("values", {})))
    return payload, values, age
