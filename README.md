# Digital Brewing System

Web-based digital twin for an automated brewing system, organised into work packages **AP2–AP6** under `project/`.

## Structure

```
project/
  ap2/   MQTT publisher + Mosquitto
  ap3/   Data acquisition, MongoDB, sessions, logbook, API routes
  ap4/   Engineer C FSM package (reused as-is)
  ap5/   Anomaly detection + AP4 integration adapters
  ap6/   React frontend
backend/ FastAPI orchestration (main.py only)
tests/   Unit and integration tests
docs/    Architecture, mapping correction, work packages
```

## Approved vessel mapping

| Vessel | Role |
|--------|------|
| K1 | Nachgussbehälter |
| K2 | Maischebehälter |
| K3 | Läuterbehälter |
| K4 | Gärbehälter |

Media flow: **K1 → K2 → K3 → K4**. AP5 rotates MQTT values into AP4's canonical fields (see `docs/mapping_correction.md`).

## Run with Docker

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend (AP6) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Mongo Express | http://localhost:8081 |
| MQTT broker | mqtt://localhost:1883 |

Verify fake vs real publisher:

```bash
docker logs -f brewing_mqtt_publisher
mosquitto_sub -h localhost -p 1883 -t "brauanlage/sps/live" -v
```

## Tests

```bash
python -m pytest tests/ -q
```

## Simulation

Backend simulation mode and the MQTT fake publisher share the same
**ProcessSimulator** (`project/shared/simulation/`). The default demo compresses
the full brew into ~30 minutes. Set `SIMULATION_SPEED_FACTOR=10` for a ~3 minute
debug run.

See `project/shared/simulation/simulation_contract.md`.

## Work packages

See `docs/work_packages.md` and `docs/architecture.md`.
