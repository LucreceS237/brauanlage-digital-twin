# API Contract

Base URL: `http://localhost:8000`. Interactive docs at `/docs`.

## Connection
| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/api/connect` | Start real SPS or simulation; creates a session. Body: `{mode, opcuaEndpoint?, scenario?}` |
| GET | `/api/connection-status` | Current connection status |
| POST | `/api/disconnect/request` | Warn before disconnect (no deletion) |
| POST | `/api/disconnect/confirm` | Delete runtime data, end session, disconnect |
| DELETE | `/api/session/current/runtime-data` | Explicit runtime cleanup |

## Simulation
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/simulation/scenarios` | List scenarios |
| POST | `/api/simulation/start` | Start a scenario. Body: `{scenario}` |
| POST | `/api/simulation/scenario` | Switch scenario (new session). Body: `{scenario}` |
| POST | `/api/simulation/stop/request` | Warn before stop |
| POST | `/api/simulation/stop/confirm` | Stop + delete runtime data |
| POST | `/api/simulation/reset/request` | Warn before reset |
| POST | `/api/simulation/reset/confirm` | Delete previous data + start scenario. Body: `{scenario}` |

## Digital twin status
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/status` | Aggregated dashboard payload |
| GET | `/api/snapshot/latest` | Latest snapshot |
| GET | `/api/measurements/latest` | Latest values (name→value) |
| GET | `/api/measurements/history?name=&limit=` | Trend history for one variable |

## FSM
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/fsm/current` | FR-04 FSM result |
| GET | `/api/fsm/transitions` | Transition history |
| POST | `/api/fsm/acknowledge` | Acknowledge ERROR/EMERGENCY |

## Alarms
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/alarms/active` | Active alarms |
| GET | `/api/alarms/history` | All alarms |
| POST | `/api/alarms/{id}/acknowledge` | Acknowledge one alarm |

## Logbook
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/logbook/preview` | Columns + first rows |
| GET | `/api/logbook/export/csv` | Download full CSV logbook |

## Disconnect order (FR-09/FR-11)
1. user requests disconnect → 2. app warns → 3. offers CSV → 4. user confirms →
5. (optional) export → 6. delete runtime data → 7. disconnect source.
