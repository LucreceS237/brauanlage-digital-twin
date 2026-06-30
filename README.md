# AP4 Brauanlage - Version 4 Fault-Coded FSM

Dieses Paket enthält die nachgearbeitete AP4-Implementierung mit eindeutigen Fehlerzuständen.

## Wesentliche Änderung gegenüber Version 3

Version 3 kannte die Superzustände `ERROR` und `EMERGENCY`. Version 4 behält diese Superzustände intern für die Steuerlogik bei, erzeugt aber für jede Anomalie einen eindeutigen `fault_code` und einen eindeutigen Anzeigezustand, z. B. `ERROR_005_K1_MASHING_TEMP_LOW` oder `EMERGENCY_006_K1_TEMP_TOO_HIGH`.

Damit erhalten AP5 und AP6 eine stabile Schnittstelle:

- AP5 nutzt `FsmContext.active_fault_code` zur phasen- und signalgenauen Anomalieerkennung.
- AP6 nutzt `FsmContext.display_state` und `FsmContext.active_fault_title` für Dashboard, Alarmkarten und Historie.

## Start

```bash
python main.py demo
python main.py acceptance
python main.py faults
```
