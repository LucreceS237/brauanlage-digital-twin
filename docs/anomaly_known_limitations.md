# Bekannte Einschränkungen der Anomalieerkennung
## Zweck
Dieses Dokument beschreibt die bekannten Einschränkungen, Annahmen und offenen Fragestellungen der Anomalieerkennung für den digitalen Zwilling der Labor-Brauanlage.

Ziel ist es, die Grenzen der aktuellen Implementierung transparent zu dokumentieren und gleichzeitig Erweiterungsmöglichkeiten für zukünftige Versionen aufzuzeigen.

Die in anomaly_rules_v0.1.md definierten Regeln beschränken sich bewusst auf Anomalien, die mit den aktuell validierten OPC-UA-Prozessvariablen sowie den verfügbaren Zuständen des Zustandsautomaten (FSM) zuverlässig diagnostiziert werden können.

---

## 1. Annahmen
Die aktuelle Version der Anomalieerkennung basiert auf folgenden Annahmen:

- Die von der SPS bereitgestellten Prozesswerte sind grundsätzlich korrekt und aktuell.
- Die im OPC-UA-Modell definierten Prozessvariablen entsprechen den tatsächlichen Anlagenzuständen.
- Die Zustände des Zustandsautomaten (IDLE, MASHING, LAUTERING, BOILING, COOLING, FERMENTING, FINISHED, EMERGENCY, ERROR) werden korrekt erkannt.
- Die Sollwerte und Grenzwerte aus der SPS bzw. dem Rezept repräsentieren den gewünschten Anlagenbetrieb.
- Durchfluss-, Temperatur- und Füllstandswerte liegen bereits in Engineering Units vor und müssen nicht zusätzlich skaliert werden.

---

## 2. Nicht diagnostizierbare Anomalien

### ND001 – Trockenheizen eines Behälters

#### Beschreibung

Ein Heizelement oder Tauchsieder ist aktiv, obwohl sich kein Medium im Behälter befindet.

#### Begründung

Der aktuelle Datenbestand enthält keine validierten OPC-UA-Variablen für die tatsächlichen Zustände der Heizelemente.

#### Benötigte Erweiterung
- Heizungsstatus K1
- Heizungsstatus K2
- Status der Tauchsieder K3
---

### ND002 – Betrieb des Rührwerks ohne Medium
#### Beschreibung

Das Rührwerk läuft, obwohl der Behälter leer ist.

#### Begründung

Der Zustand des Rührwerks wird aktuell nicht als verifizierter Datenpunkt bereitgestellt.

#### Benötigte Erweiterung
- Rückmeldung Rührwerk EIN/AUS
---

### ND003 – Mechanischer Ventilfehler
#### Beschreibung

Ein Ventil erhält einen Schaltbefehl, bewegt sich jedoch mechanisch nicht.
#### Begründung

Aktuell stehen lediglich die SPS-Ausgangssignale zur Verfügung.
Es existiert keine physische Stellungsrückmeldung des Ventils.

#### Benötigte Erweiterung
- Ventilstellung IST offen
- Ventilstellung IST geschlossen
---


### ND004 – Notventil ausgelöst
Beschreibung

Ein Sicherheits- bzw. Notventil wurde manuell oder automatisch ausgelöst.

#### Begründung

Für die Notventile NV1–NV3 liegen derzeit keine validierten OPC-UA-Datenpunkte vor.
---

### ND005 – Ursache eines Pumpenausfalls
#### Beschreibung

Die Pumpe wird aktiviert, jedoch wird kein Durchfluss erkannt.

#### Aktueller Diagnoseumfang

Die Anomalie

„Pumpe aktiv, aber kein Durchfluss“ kann erkannt werden. Die eigentliche Ursache kann jedoch nicht eindeutig bestimmt werden.

Mögliche Ursachen:
- Defekte Pumpe
- Geschlossenes Ventil
- Verstopfte Leitung
- Durchflusssensorfehler
---
## 3. Datenqualitätsrisiken
### DQ001 – Unplausible Füllstandswerte K3

Während der Analyse wurden einzelne Füllstandswerte identifiziert, deren Größenordnung nicht mit einer Labor-Brauanlage vereinbar erscheint.

Vor einer produktiven Nutzung müssen diese Werte validiert werden.

Risiko:
- Falsche Überfüllungsalarme
- Falsche Leerlaufalarme
---
### DQ002 – Skalierung von Rohwerten
Mehrere Rohwerte (IO-Link / Analogwerte) besitzen aktuell keine vollständig dokumentierte Skalierung.

Beispiele:
- Roh-Temperaturwerte
- Roh-Füllstandswerte

Vor der Nutzung für die Anomalieerkennung muss die Umrechnung in Engineering Units bestätigt werden.
---
### DQ003 – Fehlende Sensorvalidierung
Die aktuelle Version prüft lediglich die bereitgestellten Prozesswerte.
Ein Vergleich zwischen:
- Rohwert
- SPS-Prozesswert
ist derzeit noch nicht implementiert.
---
