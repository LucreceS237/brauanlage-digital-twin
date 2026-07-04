# Architecture

## Layers

```
SPS / PLC (read-only, OPC-UA)
    ↓
MQTT SPS Publisher                       project/ap2/mqtt_publisher   (FAKE_PUBLISHER | REAL_SPS)
    ↓  publish brauanlage/sps/live (1 msg/s)
Mosquitto MQTT Broker                    project/ap2/mosquitto
    ↓  subscribe
AP3 MQTT Subscriber                      project/ap3/mqtt   (validate + session)
    ↓                                     — OR internal Simulator (simulation mode)
MongoDB (Motor async)                    project/ap3/database
    ↓
AP5 snapshot adapter → AP4 FSM           project/ap5/adapters, project/ap4
    ↓
AP5 anomaly detection + alarm adapter    project/ap5/anomaly_detection
    ↓
Backend API (FastAPI)                    project/ap3/api  (orchestrated by backend/app/main.py)
    ↓  REST (JSON)
Frontend Web App (React + Vite)          project/ap6/frontend
    ↓
Dashboard / Alarm Visualization          AP6 pages
```

## Runtime flow (collector loop)

The AP3 `collector_service` runs one background asyncio task while a session is
active. Each cycle (default 1 s):

1. **Acquire** values from the simulator or the latest validated MQTT payload
   (see `project/ap3/mqtt/payload_validator.py`).
2. **Adapt** — AP5 `snapshot_adapter` maps MQTT vessel keys to AP4 `ProcessSnapshot`
   fields (approved K1–K4 rotation; see `docs/mapping_correction.md`).
3. **FSM evaluate** — AP4 FSM via AP5 `fsm_integration_service`.
4. **Anomaly detect** — AP4 diagnostics plus AP5 extra rules (stale MQTT, publisher
   disconnect, invalid payload, etc.).
5. **Persist** — snapshot + measurements; FSM transition record on state change;
   alarms reconciled; system events (all session-scoped in MongoDB).
6. **Cache** the latest twin state in memory for fast `/api/status` reads.

## Responsibilities

- **AP2**: MQTT publisher (fake or real SPS) and Mosquitto broker config.
- **AP3**: MQTT subscribe, validation, MongoDB storage, sessions, logbook export,
  cleanup, REST API routes.
- **AP4**: Brewing process FSM (Engineer C package, reused as-is).
- **AP5**: Snapshot mapping, FSM integration, alarm adapter, supplementary anomaly rules.
- **AP6**: Connection workflow, dashboard, timeline, alarms, simulation UI, logbook.
- **backend/app/main.py**: FastAPI app assembly only (imports AP3 + AP5).

The frontend **never** connects to the SPS directly; SPS access is read-only via AP2.

## Containers (docker-compose)

`frontend` (3000) · `backend` (8000) · `mongodb` (27017) · `mosquitto` (1883) ·
`mqtt_publisher` · `mongo-express` (8081). The backend waits for MongoDB health
before starting. Inside the compose network, `backend` and `mqtt_publisher`
reach the broker via host `mosquitto` (never `localhost`).

See also `docs/work_packages.md` and `docs/mapping_correction.md`.
