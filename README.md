# AP4 FSM Version 5 - ProcessSnapshot Simulation

Dieses Paket enthält eine nachgearbeitete AP4-FSM für die Brauanlage mit der verbindlichen Equipment-Zuordnung:

- K1 = Nachgussbehälter
- K2 = Maische-/Kochbehälter
- K3 = Läuterbehälter
- K4 = Gärbehälter
- Einziger gemessener Durchfluss im Snapshot: `durchfluss_k1_k2` bzw. `durchfluss_k1_k2_l_min`

## Startbefehle

```bash
cd AP4_FSM_V5_ProcessSnapshot
python main.py acceptance
python main.py faults
python main.py csv --csv data/AP4_ProcessSnapshots_Normalzyklus_V5.csv
```

## Wichtige Dateien

- `ap4/process_snapshot.py`: AP3 -> AP4 Laufzeitschnittstelle
- `ap4/fsm.py`: Zustandsautomat
- `ap4/process_monitor.py`: Prozess-ERROR-Codes
- `ap4/safety.py`: EMERGENCY-Codes
- `ap4/ap4_interfaces.py`: AP4 -> AP5 und AP4 -> AP6 Schnittstellen
- `ap4/simulation_runner.py`: Live-/Replay-Simulation aus CSV
- `data/AP4_ProcessSnapshots_Normalzyklus_V5.csv`: vollständiger Normalzyklus
- `data/AP4_ProcessSnapshots_Fehlerfaelle_V5.csv`: Fehlerfälle
- `data/AP4_ProcessSnapshots_Testdaten_V5.sqlite`: SQL-Datenbank

## AP5 Nutzung

```python
from ap4.ap4_interfaces import build_ap5_payload
context = fsm.get_context_for_anomaly()
payload = build_ap5_payload(context)
```

## AP6 Nutzung

```python
from ap4.ap4_interfaces import build_ap6_dashboard_payload
context = fsm.get_context_for_anomaly()
payload = build_ap6_dashboard_payload(context)
```
