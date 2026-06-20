# Alarm-Schema der Anomalieerkennung

## Zweck des Dokuments

Dieses Dokument definiert das einheitliche Alarmformat der Anomalieerkennung für den digitalen Zwilling der Labor-Brauanlage.

Das Alarm-Schema beschreibt, wie erkannte Anomalien strukturiert dargestellt, gespeichert, getestet und über die REST-API weitergegeben werden.

Es dient als Schnittstelle zwischen:

- Anomalieerkennung
- Zustandsautomat
- Datenerfassung
- REST-API
- Live-Anzeige
- Testmodulen

---

# 1. Grundprinzip

Jede erkannte Anomalie wird als strukturierter Alarm dargestellt.

Ein Alarm beschreibt:

- wann die Anomalie erkannt wurde
- welche Regel ausgelöst wurde
- in welchem Prozesszustand sie auftrat
- welche Komponente betroffen ist
- welcher Messwert problematisch war
- welcher Grenzwert verletzt wurde
- wie kritisch die Anomalie ist
- welche Meldung angezeigt werden soll

---

# 2. Alarmobjekt

## 2.1 JSON-Struktur

```json
{
  "timestamp": "2026-06-15T10:15:30",
  "rule_id": "A003",
  "code": "K2_TEMP_HIGH",
  "severity": "HIGH",
  "state": "MASHING",
  "component": "K2",
  "variable": "K2_Temperatur",
  "value": 82.5,
  "threshold": 78.0,
  "unit": "°C",
  "message": "Die Temperatur im Maischebehälter K2 liegt oberhalb der zulässigen oberen Grenze.",
  "diagnostic_status": "DIAGNOSABLE"
}
```
# 3. Feldbeschreibung
| Feld                | Typ                              | Pflicht | Beschreibung                                                                          |
| ------------------- | -------------------------------- | ------- | ------------------------------------------------------------------------------------- |
| `timestamp`         | String / ISO 8601                | Ja      | Zeitpunkt der Alarmerkennung                                                          |
| `rule_id`           | String                           | Ja      | Eindeutige ID der Regel, z. B. `A003`                                                 |
| `code`              | String                           | Ja      | Technischer Kurzcode des Alarms                                                       |
| `severity`          | String                           | Ja      | Kritikalität des Alarms                                                               |
| `state`             | String                           | Ja      | Aktueller FSM-Zustand                                                                 |
| `component`         | String                           | Ja      | Betroffene Anlagenkomponente                                                          |
| `variable`          | String                           | Ja      | Betroffener OPC-UA-Datenpunkt bzw. Prozesswert                                        |
| `value`             | Number / Boolean / String / Null | Ja      | Gemessener Wert                                                                       |
| `threshold`         | Number / String / Null           | Nein    | Verletzter Grenzwert oder erwarteter Bereich                                          |
| `unit`              | String / Null                    | Nein    | Einheit des Messwerts                                                                 |
| `message`           | String                           | Ja      | Menschlich lesbare Alarmbeschreibung                                                  |
| `diagnostic_status` | String                           | Ja      | Gibt an, ob die Anomalie direkt, indirekt oder nur eingeschränkt diagnostizierbar ist |
---
# 4. Severity-Level
Die Severity beschreibt die Kritikalität eines Alarms.

| Severity   | Bedeutung                                             | Beispiel                               |
| ---------- | ----------------------------------------------------- | -------------------------------------- |
| `INFO`     | Reine Information, keine unmittelbare Störung         | Zustand gewechselt                     |
| `LOW`      | Leichte Abweichung, Beobachtung notwendig             | Temperatur leicht außerhalb Sollwert   |
| `MEDIUM`   | Prozessabweichung mit möglichem Einfluss auf Qualität | Gärtemperatur außerhalb Zielbereich    |
| `HIGH`     | Kritische Prozessabweichung                           | Temperatur deutlich über oberer Grenze |
| `CRITICAL` | Potenzielles Sicherheits- oder Anlagenrisiko          | Pumpe aktiv, aber kein Durchfluss      |

# 5. Diagnostic Status
Nicht jede Anomalie ist mit der gleichen Sicherheit diagnostizierbar.
| Status            | Bedeutung                                                                                |
| ----------------- | ---------------------------------------------------------------------------------------- |
| `DIAGNOSABLE`     | Die Anomalie kann mit den vorhandenen Datenpunkten direkt erkannt werden                 |
| `INDIRECT`        | Die Anomalie kann nur indirekt aus Symptomen abgeleitet werden                           |
| `LIMITED`         | Die Diagnose ist möglich, aber wegen Datenqualität oder fehlender Sensorik eingeschränkt |
| `NOT_DIAGNOSABLE` | Die Anomalie ist mit den aktuellen Datenpunkten nicht zuverlässig erkennbar              |

# 6. Komponentenbezeichnungen
Für die Alarmmeldungen werden folgende Komponentenbezeichnungen verwendet:
| Komponente  | Bedeutung                          |
| ----------- | ---------------------------------- |
| `K1`        | Nachgussbehälter                   |
| `K2`        | Maischebehälter                    |
| `K3`        | Läuterbehälter                     |
| `K4`        | Gär-/Reservebehälter               |
| `FLOW_PATH` | Durchflussstrecke Nachguss/Maische |
| `PUMP`      | Pumpe                              |
| `VALVE`     | Ventile allgemein                  |
| `FSM`       | Zustandsautomat                    |
| `SENSOR`    | Sensorik / Datenqualität           |
| `SYSTEM`    | Allgemeiner Systemzustand          |

# 7. Erlaubte FSM-Zustände
Das Feld state verwendet die Zustände des Zustandsautomaten:
```
IDLE
MASHING
LAUTERING
BOILING
COOLING
FERMENTING
FINISHED
EMERGENCY
ERROR
UNKNOWN
```
