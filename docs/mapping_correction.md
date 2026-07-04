# Anlage Mapping Correction

## Approved Anlage mapping

After reviewing the Anlage documentation, the approved physical mapping is:

| Vessel | Role |
| ------ | ---- |
| **K1** | Nachgussbehälter (hot liquor / sparge water) |
| **K2** | Maischebehälter (mash) |
| **K3** | Läuterbehälter (lauter / boil) |
| **K4** | Gärbehälter (fermentation) |

Correct process/media flow:

```
K1 (Nachguss) → K2 (Maische) → K3 (Läuter/Boil) → K4 (Gärung)
```

Phase → primary vessel:

| Phase | Vessel |
| ----- | ------ |
| PRECHECK / NACHGUSS | K1 |
| MASHING | K2 |
| LAUTERING | K3 |
| BOILING | K3 |
| COOLING | K3 |
| TRANSFER_TO_K4 / FERMENTING | K4 |

## Why an adapter layer (not a rewrite of AP4)

The AP4 FSM package predates this correction. Its `ProcessSnapshot` fields
(`k1_*`, `k2_*`, `k3_*`, `k4_*`) are bound to a process **role** by AP4's own
transition logic (`ap4/fsm.py`, `ap4/process_monitor.py`), and AP4 originally
labelled the tanks with a different physical assignment:

| AP4 field | AP4 role (fixed in AP4 logic) | AP4's original label |
| --------- | ----------------------------- | -------------------- |
| `k3_*` | Nachguss source (PRECHECK/NACHGUSS) | "Nachguss K3" |
| `k1_*` | Mash vessel (MASHING) | "Maische K1" |
| `k2_*` | Lauter/Boil (LAUTERING/BOILING) | "Läuter/Koch K2" |
| `k4_*` | Fermentation (FERMENTING) | "Gär K4" |

To respect the approved mapping **without destabilising AP4**, AP5 adds a
correction/adapter layer (`project/ap5/adapters/`). Each approved physical
sensor is routed to the AP4 field whose **role** matches that sensor's vessel —
a rotation, not a 1:1 rename:

| Approved sensor (MQTT) | Vessel role | → AP4 canonical field |
| ---------------------- | ----------- | --------------------- |
| `K1_Temperatur` | Nachguss | `k3_temperature_c` |
| `K2_Temperatur` | Mash | `k1_temperature_c` |
| `K3_Temperatur` | Lauter/Boil | `k2_temperature_c` |
| `MobilerSensor_Temperatur` | Fermentation | `k4_temperature_c` |
| `K2_Füllstand` | Mash level | `k1_level_l` |
| `K3_Füllstand` | Lauter level | `k2_level_l` |
| `Durchfluss_NachgussMaische` | Nachguss→Mash flow | `flow_k3_to_k1_l_min` |

### Meaning of AP4 canonical fields after correction

```
k3_temperature_c = K1 Nachguss temperature
k1_temperature_c = K2 Mashing temperature
k2_temperature_c = K3 Lautering/Boiling temperature
k4_temperature_c = K4 Fermentation temperature
```

This is documented in code in `project/ap5/adapters/mapping.py` and enforced by
`project/ap5/adapters/snapshot_adapter.py`. Alarms produced from AP4 diagnostics
are re-labelled back to the approved vessel (`ap4_alarm_adapter.py`), e.g. an
AP4 `k1_temperature_c` fault is shown as **K2 Maischebehälter**.

## Actuator-feedback derivation

The standard SPS/MQTT payload carries process values but not valve/pump feedback
or the internal transfer flows AP4 needs to advance. `snapshot_adapter.py`
derives a plausible actuator picture from the PLC step `Aktueller_Schritt`
(isolated in AP5, never inside AP4). The measured temperatures/levels/flow still
gate every transition and still raise AP4 faults.

## Tests

- `tests/test_snapshot_adapter.py` — asserts the rotation above.
- `tests/test_ap4_integration.py` — AP4 driven only through AP5 walks the real
  normal sequence IDLE→…→BOILING; emergency stop takes priority.
- `tests/test_alarm_adapter.py` — AP4 diagnostics map to alarms with the approved
  vessel labels and correct severity.

> Written as a mapping correction after reviewed Anlage documentation — no
> individual is at fault; AP4 remains the reference FSM and is reused as-is.
