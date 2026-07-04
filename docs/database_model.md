# Database Model (MongoDB)

Database: `brewing_digital_twin`. Every runtime document carries a `sessionId`.

## Collections

| Collection | Lifetime | Purpose |
| ---------- | -------- | ------- |
| `sessions` | persistent | one real connection or simulation run |
| `data_points` | static (re-seeded) | OPC-UA variable definitions |
| `simulation_scenarios` | static (re-seeded) | available demo scenarios |
| `snapshots` | runtime | one polling/simulation cycle |
| `measurements` | runtime | individual values per snapshot |
| `fsm_states` | runtime | state transition history |
| `alarms` | runtime | active + historical alarms |
| `system_events` | runtime | technical/system events |

**Runtime collections** (`snapshots, measurements, fsm_states, alarms,
system_events`) are deleted per-session on disconnect / scenario reset
(`mongodb.delete_runtime_data`). Static collections are kept.

## Indexes (`mongodb.init_collections`)

- `snapshots`: `(sessionId, receivedAt)`
- `measurements`: `(sessionId, snapshotId)`, `(sessionId, name, timestamp)`
- `fsm_states`: `(sessionId, createdAt)`
- `alarms`: `(sessionId, status)`
- `system_events`: `(sessionId, createdAt)`
- `sessions`: unique `(sessionId)`

## Example documents

### sessions
```json
{ "sessionId": "session_2026_06_16_215832", "mode": "simulation",
  "scenario": "Low Flow During Lautering", "status": "ACTIVE",
  "startedAt": "2026-06-16T21:58:32Z", "endedAt": null }
```

### snapshots
```json
{ "sessionId": "...", "receivedAt": "...", "source": "OPC-UA",
  "collectorStatus": "OK", "fsmState": "MASHING", "previousFsmState": "IDLE",
  "transitionReason": "start_requested and K1_Temperatur > 50°C",
  "timeInStateSeconds": 120, "aktuellerSchritt": 2, "emergencyStop": false,
  "acknowledge": false, "sensorOk": true, "activeFault": false }
```

### alarms
```json
{ "sessionId": "...", "snapshotId": "...", "ruleId": "R005",
  "code": "LOW_FLOW_DURING_LAUTERING", "severity": "HIGH", "state": "LAUTERING",
  "component": "FLOW_PATH", "variable": "Durchfluss_NachgussMaische",
  "value": 0.1, "threshold": ">= 0.5 l/min",
  "message": "Flow is too low during lautering.", "status": "ACTIVE",
  "createdAt": "...", "clearedAt": null }
```

(`measurements`, `fsm_states`, `system_events`, `data_points`,
`simulation_scenarios` follow section 20 of the MVP description.)
