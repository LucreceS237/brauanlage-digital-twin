# Anomaly Rules v0.1

## 1. Ziel
Dieses Dokument beschreibt die erste Version der regelbasierten Anomalieerkennung für den digitalen Zwilling der Brauanlage.

## 2. Grundprinzip
Die Anomalieerkennung arbeitet zyklisch auf Echtzeit-Snapshots aus der SPS. Jeder Snapshot enthält Zeitstempel, aktuellen FSM-Zustand, Prozesswerte und optional Signalqualität.

## 3. Realtime Evaluation
- Prozesswerte werden ca. alle 1 s gelesen.
- Grenzwerte werden beim Start oder alle 30–60 s gelesen.
- Regeln lösen nicht bei Einzelwerten aus, sondern nach definierter Persistenzdauer.
- Nach Zustandswechseln gilt eine Grace Period.
- Alarme werden erst zurückgesetzt, wenn die Rücksetzbedingung erfüllt ist.

## 4. Severity
LOW = Hinweis  
MEDIUM = Prozessabweichung  
HIGH = kritische Prozessabweichung  
CRITICAL = potenzielles Sicherheits- oder Anlagenrisiko  

## 5. Regeln

### R001 – DATA_STALE
Datenpunkt ist älter als erlaubtes Maximum.

### R002 – SENSOR_VALUE_INVALID
Wert ist None, NaN oder außerhalb physikalischer Plausibilität.

### R003 – TEMP_OUT_OF_RANGE
Temperatur liegt außerhalb unterer/oberer Sollwertgrenzen.

### R004 – TEMP_RISE_TOO_FAST
Temperaturgradient überschreitet erlaubten Grenzwert über ein 60-s-Fenster.

### R005 – LOW_FLOW_DURING_LAUTERING
Im Zustand LAUTERING liegt der Durchfluss unter 0.5 l/min.
zeitfenster
### R006 – UNEXPECTED_FLOW_IN_IDLE
Im Zustand IDLE oder FINISHED existiert Durchfluss.