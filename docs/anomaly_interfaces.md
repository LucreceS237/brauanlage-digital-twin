# Schnittstellen der Anomalieerkennung

## Zweck des Dokuments

Dieses Dokument definiert die technischen und fachlichen Schnittstellen der Anomalieerkennung für den digitalen Zwilling der Labor-Brauanlage.

Es beschreibt:

- welche Eingabedaten die Anomalieerkennung benötigt,
- welche Ausgabedaten sie liefert,
- welche Module beteiligt sind,
- welche Annahmen für die Integration gelten,
- und welche offenen Punkte noch mit den anderen Arbeitspaketen abgestimmt werden müssen.

Die Datei dient als Übergabedokument zwischen:

- Datenerfassung
- Zustandsautomat
- Anomalieerkennung
- REST-API
- Testmodulen

---

# 1. Rolle der Anomalieerkennung im System

Die Anomalieerkennung verarbeitet zyklisch den aktuellen Prozesszustand und die aktuell verfügbaren Prozessdaten.

Grundprinzip:

```text
Prozessdaten + FSM-Zustand + Grenzwerte
→ Regelprüfung
→ Liste erkannter Alarme
```
Die Anomalieerkennung steuert die Anlage nicht aktiv. Sie arbeitet ausschließlich lesend und bewertet die bereitgestellten Daten.

# 2. Eingabeschnittstelle
## 2.1 ERwartetes Eingabeobjekt
Die Anomalieerkennung erwartet pro Zyklus ein strukturiertes Eingabeobjekt.

Vorgeschlagener Name: 
```Python
ProcessSnapshot
```
Beispiel als JSON: 
```JSON
{
  "timestamp": "2026-06-15T10:15:30",
  "state": "MASHING",
  "aktueller_schritt": 3,

  "k1_temperatur": 68.5,
  "k1_temperatur_sollwert_obere_grenze": 78.0,
  "k1_temperatur_sollwert_untere_grenze": 50.0,
  "k1_fuellstand_voll": true,

  "k2_temperatur": 65.2,
  "k2_temperatur_sollwert_obere_grenze": 78.0,
  "k2_temperatur_sollwert_untere_grenze": 50.0,
  "k2_fuellstand": 12.5,
  "k2_fuellstand_voll": false,

  "k3_temperatur": 24.8,
  "k3_temperatur_sollwert_obere_grenze": 100.0,
  "k3_temperatur_sollwert_untere_grenze": 20.0,
  "k3_fuellstand": 8.0,
  "k3_minimaler_fuellstand": 2.0,
  "k3_maximaler_fuellstand": 20.0,

  "mobiler_sensor_temperatur": 18.5,
  "durchfluss_nachguss_maische": 0.7,

  "pumpe": null,
  "ventil_3": null,
  "ventil_4_1": null,
  "ventil_4_2": null,
  "ventil_5_1": null,
  "ventil_5_2": null
}
```
---
# 3. Pflichtfelder
Die folgenden Folder werden für die minimale Version der Anomalieerkennung benötigt.
| Feld                                   | Typ               | Einheit | Herkunft              | Verwendung                        |
| -------------------------------------- | ----------------- | ------- | --------------------- | --------------------------------- |
| `timestamp`                            | String / ISO 8601 | -       | Datenerfassung        | Zeitliche Einordnung              |
| `state`                                | String            | -       | FSM                   | Zustandsabhängige Regeln          |
| `aktueller_schritt`                    | Integer           | -       | SPS / OPC-UA          | Abgleich mit FSM                  |
| `k1_temperatur`                        | Float             | °C      | OPC-UA DB1            | Temperaturregel K1                |
| `k1_temperatur_sollwert_obere_grenze`  | Float             | °C      | OPC-UA Parametrierung | obere Temperaturgrenze K1         |
| `k1_temperatur_sollwert_untere_grenze` | Float             | °C      | OPC-UA Parametrierung | untere Temperaturgrenze K1        |
| `k1_fuellstand_voll`                   | Boolean           | -       | OPC-UA DB1            | Plausibilitätsprüfung             |
| `k2_temperatur`                        | Float             | °C      | OPC-UA DB1            | Temperaturregel K2                |
| `k2_temperatur_sollwert_obere_grenze`  | Float             | °C      | OPC-UA Parametrierung | obere Temperaturgrenze K2         |
| `k2_temperatur_sollwert_untere_grenze` | Float             | °C      | OPC-UA Parametrierung | untere Temperaturgrenze K2        |
| `k2_fuellstand`                        | Float             | Liter   | OPC-UA DB1            | Füllstandsregel K2                |
| `k2_fuellstand_voll`                   | Boolean           | -       | OPC-UA DB1            | Plausibilitätsprüfung             |
| `k3_temperatur`                        | Float             | °C      | OPC-UA DB1            | Temperaturregel K3                |
| `k3_temperatur_sollwert_obere_grenze`  | Float             | °C      | OPC-UA Parametrierung | obere Temperaturgrenze K3         |
| `k3_temperatur_sollwert_untere_grenze` | Float             | °C      | OPC-UA Parametrierung | untere Temperaturgrenze K3        |
| `k3_fuellstand`                        | Float             | Liter   | OPC-UA DB1            | Füllstandsregel K3, eingeschränkt |
| `k3_minimaler_fuellstand`              | Float             | Liter   | OPC-UA Parametrierung | Mindestfüllstand K3               |
| `k3_maximaler_fuellstand`              | Float             | Liter   | OPC-UA Parametrierung | Maximalfüllstand K3               |
| `mobiler_sensor_temperatur`            | Float             | °C      | OPC-UA DB1            | Gär-/Reservebereich K4            |
| `durchfluss_nachguss_maische`          | Float             | l/min   | OPC-UA DB1            | Durchflussregel                   |

# 4. Ausgabeschnittstele
Die Anomalieerkennung liefert eine Liste von Alarmobjekten.
Siehe mal das einheitliche Alarmformat [Alarm-Schema der Anomalieerkennung](./alarm_schema.md)