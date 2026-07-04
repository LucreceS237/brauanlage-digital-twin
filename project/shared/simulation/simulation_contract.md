# Process simulator contract (shared by AP2 fake MQTT and AP3 simulation mode)

For demonstration purposes, the simulator compresses the brewing process into
approximately **30 minutes**. This does not represent real industrial brewing
durations. It allows the complete process flow to be observed during a project
presentation.

## Module location

`project/shared/simulation/` — imported by:

- `project/ap2/mqtt_publisher/` (FAKE publisher)
- `project/ap3/simulation/` (backend simulation mode)
- `project/ap5/simulation/` (re-exports for documentation)

## Physical mapping (approved)

| MQTT field | Vessel | Role |
|------------|--------|------|
| K1_Temperatur | Nachguss | Pre-heating / hot liquor |
| K2_Temperatur | Maische | Mashing |
| K3_Temperatur | Läuter | Lautering, boiling, cooling |
| MobilerSensor_Temperatur | Gär (K4) | Fermentation |

Flow: **K1 → K2 → K3 → K4**

## Compressed timeline (default 1800 s)

| Phase | Duration | Primary signals |
|-------|----------|-----------------|
| PRE_HEATING | 5 min | K1_Temperatur 20→75 °C |
| PRECHECK / NACHGUSS | ~10 s | start, flow |
| MASHING | 6 min | K2_Temperatur → 65 °C |
| LAUTERING | 3 min | flow ≥ 0.5 l/min, K3_Füllstand |
| BOILING | 4.5 min | K3_Temperatur → 100 °C |
| COOLING | 1.5 min | K3_Temperatur → ≤ 25 °C |
| TRANSFER_TO_K4 | 30 s | transfer flow |
| FERMENTING | 10 min | MobilerSensor ~ 18 °C (16–22) |
| FINISHED | stable | process complete |

## Configuration

| Variable | Default | Used by |
|----------|---------|---------|
| `SIMULATION_TOTAL_DURATION_SECONDS` | 1800 | backend + publisher |
| `SIMULATION_TICK_SECONDS` | 1 | backend + publisher |
| `SIMULATION_SPEED_FACTOR` | 1 | 10 = 30 min demo in ~3 min |
| `SIMULATION_SCENARIO` | NORMAL_PROCESS | publisher fake mode |

## Payload envelope

```json
{
  "timestamp": "...",
  "source": "Fake_SPS | SIMULATION | REAL_SPS",
  "publisherMode": "FAKE | SIMULATION | REAL",
  "connectionStatus": "CONNECTED | SIMULATION | DISCONNECTED",
  "simulationPhase": "MASHING",
  "values": { "...": "..." }
}
```

## Scenarios

`NORMAL_PROCESS`, `TEMPERATURE_TOO_HIGH`, `LOW_FLOW_DURING_LAUTERING`,
`SENSOR_FAILURE`, `STALE_DATA`, `COOLING_FAILURE`,
`FERMENTATION_TEMP_OUT_OF_RANGE`, `EMERGENCY_STOP`, `ABSOLUTE_LIMIT_EXCEEDED`

Faults inject after the normal timeline reaches the target phase.

## API

```python
sim = ProcessSimulator(scenario="NORMAL_PROCESS", total_duration_seconds=1800, speed_factor=1.0)
payload = sim.next_payload(source="Fake_SPS", publisher_mode="FAKE")  # MQTT path
sim.advance(1.0)
values = sim.next_values()  # backend path (advances internally)
```
