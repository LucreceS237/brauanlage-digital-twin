# Work Packages (AP2–AP6)

The project is organised into work packages under `project/`. Each package has a
clear owner and a clean interface to its neighbours.

```
MQTT payload
   ↓  (AP2 publisher → Mosquitto)
AP3 mqtt subscribe + payload validation + session/storage
   ↓
AP5 snapshot adapter  (approved K1–K4 mapping)
   ↓
AP4 FSM update  (Engineer C, reused as-is)
   ↓
AP5 alarm adapter + extra anomaly rules
   ↓
AP3 MongoDB storage (snapshots, measurements, fsm_states, alarms, events)
   ↓
AP6 frontend (dashboard, timeline, alarms, logbook)
```

## AP2 — MQTT Publisher & Mosquitto (Engineer D; orig. Engineer B)
`project/ap2/`
- Dockerized MQTT publisher with **FAKE** and **REAL** modes (no silent
  fallback from REAL to FAKE).
- **FAKE** mode uses the shared `ProcessSimulator` (~30 min compressed demo).
- Publishes to `brauanlage/sps/live`; every message includes `source`,
  `publisherMode`, `connectionStatus`, `simulationPhase`, `values`.
- Mosquitto broker configuration.

## AP3 — Data acquisition, DB, session & logbook (Engineer D; orig. Engineer B)
`project/ap3/`
- Subscribe to MQTT, validate payloads, create sessions.
- Store snapshots, measurements, FSM states, alarms, system events (all
  `sessionId`-scoped).
- CSV logbook export before cleanup; runtime-data cleanup on disconnect.
- API: connection, status, logbook, session.

## AP4 — FSM package (Engineer C) — reused as-is
`project/ap4/`
- States: IDLE, PRECHECK, NACHGUSS, MASHING, LAUTERING, BOILING, COOLING,
  TRANSFER_TO_K4, FERMENTING, FINISHED, ERROR, EMERGENCY.
- Owns: transition logic, process monitoring, safety diagnostics, fault catalog.
- Interface consumed by AP5: `ProcessSnapshot` in → `TransitionResult` /
  `FsmContext` out (`BrewStateMachine.update`, `get_context_for_anomaly`).
- **Not rewritten.** The approved mapping is applied around it by AP5 (see
  `mapping_correction.md`).

## AP5 — Anomaly detection & AP4 integration (Engineer D)
`project/ap5/`
- `adapters/mapping.py` — approved K1–K4 mapping (single source of truth).
- `adapters/snapshot_adapter.py` — MQTT values → AP4 `ProcessSnapshot`.
- `adapters/ap4_alarm_adapter.py` — AP4 diagnostics → alarms (approved labels).
- `services/fsm_integration_service.py` — the one clean bridge to AP4 (no
  competing FSM); injects a compressed demo recipe.
- `anomaly_detection/` — EXTRA rules only (MQTT stale, publisher disconnected,
  invalid payload, temp-rise-too-fast, source mismatch) — never duplicating
  AP4 process/safety faults.
- `services/alarm_service.py`, `services/twin_service.py` — alarm lifecycle and
  frontend-ready digital-twin status.

## AP6 — Frontend (Engineer E)
`project/ap6/frontend/`
- Connection page, live dashboard, process timeline, alarm center, simulation
  control, logbook workflow.
- Uses AP4-compatible states and the approved K1–K4 labels; shows `source`
  (REAL_SPS / Fake_SPS) and `publisherMode` (REAL / FAKE).

## Ownership summary

| Engineer | Work packages |
| -------- | ------------- |
| A | Process-variable concept / OPC-UA NodeIds |
| B | *(left)* originally AP2/AP3 |
| C | AP4 FSM |
| D | AP2, AP3, AP5 (+ took over Engineer B's acquisition/storage) |
| E | AP6 frontend |
