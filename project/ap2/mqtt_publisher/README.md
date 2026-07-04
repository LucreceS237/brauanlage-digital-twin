# MQTT SPS Publisher (AP2)

Dockerized service that feeds the digital twin's **real-SPS data path**:

```
SPS / PLC → mqtt_publisher → Mosquitto → backend → MongoDB → frontend
```

## FSM-driven fake mode

`FAKE_PUBLISHER` uses the shared **`ProcessSimulator`** (`project/shared/simulation/`).
Values follow a coherent compressed brewing timeline (~30 minutes by default), not
random jumps.

For demonstration purposes, the simulator compresses the brewing process into
approximately 30 minutes. This does not represent real industrial brewing
durations. It allows the complete process flow to be observed during a project
presentation.

## Modes (`PUBLISHER_MODE`)

| Mode | `source` | `publisherMode` | Data |
| ---- | -------- | --------------- | ---- |
| `FAKE_PUBLISHER` (default) | `Fake_SPS` | `FAKE` | ProcessSimulator |
| `REAL_SPS` | `REAL_SPS` | `REAL` | OPC-UA live read |

REAL mode **never** falls back to fake data. SPS outage → `connectionStatus: DISCONNECTED`.

## Payload

Published once per second to `brauanlage/sps/live`:

```json
{
  "timestamp": "2026-07-01T12:00:00Z",
  "source": "Fake_SPS",
  "publisherMode": "FAKE",
  "connectionStatus": "CONNECTED",
  "simulationPhase": "MASHING",
  "values": { "...": "..." }
}
```

## Environment variables

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `PUBLISHER_MODE` | `FAKE_PUBLISHER` | `FAKE_PUBLISHER` or `REAL_SPS` |
| `SIMULATION_SCENARIO` | `NORMAL_PROCESS` | Fault scenario key |
| `SIMULATION_TOTAL_DURATION_SECONDS` | `1800` | Full demo length (~30 min) |
| `SIMULATION_TICK_SECONDS` | `1` | Publish interval |
| `SIMULATION_SPEED_FACTOR` | `1` | `10` = 30 min in ~3 min |
| `MQTT_BROKER_HOST` | `mosquitto` | Broker host |
| `MQTT_TOPIC` | `brauanlage/sps/live` | Topic |
| `OPCUA_SERVER_URL` | `opc.tcp://192.168.0.1:4840` | REAL_SPS only |

## Verify fake vs real

```bash
docker logs -f brewing_mqtt_publisher
mosquitto_sub -h localhost -p 1883 -t "brauanlage/sps/live" -v
```

Look for `source` and `publisherMode` in each message.

## Files

- `publisher.py` — orchestrator
- `fake_publisher.py` — FAKE path wrapper
- `real_sps_reader.py` — REAL OPC-UA path
- `data_points.py` — NodeIds (Engineer A)
- `process_simulator.py`, `scenarios.py`, `payload_builder.py` — re-exports
