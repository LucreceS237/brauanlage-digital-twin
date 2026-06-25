# Anomaly Rules v0.1

## Digitaler Zwilling der Labor-Brauanlage
Projekt: 
Modul: Automatisierungstechnik und industrielle Kommunikationssysteme
Studiengang: Master Systems Eningeering
Verantwortlich: Emmanuel - Anomalieerkennung & Validierung

# 1. Ziel des Dokuments
Dieses Dokument definiert die regelbasierten Anomalieerkennung für den digitalen Zwilling der Labor-Brauanlage.

Die Anomalieerkennung dient dazu:
- Abweichungen von VNormalbetrieb zu erkennen
- sicherheitskritische Zustände frühzeitig zu identifizieren
- Alarmmeldungen mit kontextinformationne bereitzustellen
- die Grundlage für visualisierun und ApI-Integration bereitzustellen
- den Brauprozess intelligent zu interpretieren

Die Dokument beschreibt:
 - bekannte Sensoren und Aktoren
 - Prozesszusammenhänge
 - Kategorien von Anomalien
 - erste Regeldefinitionen
 - offene Punkte und Annahmen
 - Anforderungen an andere Systemmodule

# 2. Systemkontext
## 2.1 Übersicht der Brauanlage
Die Labor-Brauanlage besteht aus vier Hauptbehältern: 
| Behälter | Funktion |
|---|---|
| K3 | Nachgussbehälter |
| K1 | Maishebehälter |
| K2 | Läuterbehälter |
| K4 | Gärbehälter |

Der Medienfluss erfolgt aktuell in folgender Reihenfolge:
``` 
K3 → K1 → K2 → K4
```
Die Übertragung zwischen den Behältern erfolgt über Prozessventile und eine Pumpe.

## 2.2 Bekannte Sensoren
| Sensor | Beschreibung |
| T | Temperatur |
| L | Füllstand |
| DF | Durchfluss |

Zusätzlich existieren Rohwerte aus IO-Link-/Analog-Sensorik

## 2.3 Bekannte Aktoren

| Aktor | Beschreibung |
| Tauchsieder | Heizung K3 |
| Kochfeld 1 | Hiezung K1 |
| Kochfeld 2 | Heizung K2 |
| Rührwerk | K1 |
| Pumpe | Austrag Richtung K4 |

## 2.4 Bekannte Prozessventile
| Ventil | Verbindung |
| V3 | K3 → K1 |
| V4 | K1 → K2 |
| V5 | K2 → K4 |

## 2.5 Sicherheitsventile
| Ventil | Beschreibung |
| NV1 | Sicherheits-/Absperrventil zwischen K3 und K1 |
| Nv2 | Sicherheits-/Absperrventil zwischen K1 und K2 |
| NV3 | Sicherheits-/Absperrventil Austrag |

> **TODO:** Die genaue technishce Bedeutung und Integration der Scicherheitsventile muss noch geklärt werden

# 3. Bekannte OPC-UA-Datenpunkte
Basierend auf der aktuellen Knotenliste sind folgende Variablen für die Anomalieerkennung relevant:

## 3.1 Temperaturdaten
 - k1_temperatur
 - k2_temperatur
 - k3_temperatur
 - mobiler_sensor_temperatur
 - k1_roh_temperatur
 - k2_roh_temperatur
 - k3_roh_temperatur
 - k4_roh_temperatur

## 3.2 Sollwerte und Grenzwerte

- k1_temperatur_aktiver_sollwert
- k2_temperatur_aktiver_sollwert
- k3_temperatur_sollwert
- k1_temperatur_sollwert_obere_grenze
- k1_temperatur_sollwert_untere_grenze
- k2_temperatur_sollwert_obere_grenze
- k2_temperatur_sollwert_untere_grenze
- k3_temperatur_sollwert_obere_grenze
- k3_temperatur_sollwert_untere_grenze
- k4_sollkuehltemperatur

---

## 3.3 Füllstandsdaten

- k1_fuellstand_voll
- k2_fuellstand
- k2_fuellstand_voll
- k3_fuellstand
- k3_minimaler_fuellstand
- k3_maximaler_fuellstand
- k3_soll_fuellstand
- k2_soll_fuellstand_nach_vorgang1
- k1_roh_fuellstand
- k2_roh_fuellstand
- k3_roh_fuellstand

---

## 3.4 Noch fehlende kritische Variablen

> **TODO:** Die folgenden Variablen müssen noch zugeordnet sein(mit Samuel und Hamid):

- v3_status
- v4_status
- v5_status
- pump_status
- heater_status_k1
- heater_status_k2
- heater_status_k3
- ruehrwerk_status
- durchflusswert_df

# 4. Prozessphasen (TODO)

 Eine genaue FSM-Definition muss mit Jovian.

Aktuell wird von folgenden Hauptzuständen ausgegangen:

| Zustand | Beschreibung |
|---|---|
| MAISCHEN | Verarbeitung in K1 |
| LAEUTERN | Transfer/Trennung Richtung K2 |
| KOCHEN | Temperaturerhöhung/Kochen |
| KUEHLEN | Temperaturabsenkung |
| GAEREN | Prozess in K4 |

---

# 5. Kategorien der Anomalieerkennung

## 5.1 Temperatur-Anomalien

Abweichungen von Sollwerten oder Grenzbereichen.

Beispiele:

- Übertemperatur
- Untertemperatur
- Temperatur steigt trotz aktiver Heizung nicht
- Temperaturanstieg zu schnell

---

## 5.2 Füllstand-Anomalien

Abweichungen im Behälterfüllstand.

Beispiele:

- Overflow
- Minimalfüllstand unterschritten
- Behälter leer trotz aktivem Heizbetrieb

---

## 5.3 Durchfluss-Anomalien

Probleme im Medienfluss.

Beispiele:

- Pumpe aktiv aber kein Durchfluss
- Durchfluss trotz geschlossener Ventile
- Medienfluss in falscher Richtung

---

## 5.4 Sensor-Anomalien

Inkonsistenzen zwischen Rohwerten und Prozesswerten.

Beispiele:

- Rohwert stark abweichend
- Unplausible Sensorwerte
- Fehlende Daten

---

## 5.5 Prozesslogik-Anomalien

Physikalisch oder logisch unmögliche Zustände.

Beispiele:

- K2-Füllstand steigt bei geschlossenem V4
- Temperaturänderung ohne aktive Heizung
- Medienfluss ohne offene Ventile

---

# 6. Severity-Level

## 6.1 Definition

| Severity | Bedeutung |
|---|---|
| LOW | Unkritische Abweichung |
| MEDIUM | Prozessabweichung |
| HIGH | Kritischer Prozessfehler |
| CRITICAL | Sicherheitskritischer Zustand |

---

## 6.2 Vorläufige Farbcodierung

| Severity | Farbe |
|---|---|
| LOW | Gelb |
| MEDIUM | Orange |
| HIGH | Rot |
| CRITICAL | Blinkend Rot |

Muss mit Engineer E abgestimmt werden.

---

# 7. Regelkatalog v0.1

## 7.1 Temperatur-Regeln

| ID | Regel | Severity | Status |
|---|---|---|---|
| R001 | K1 Temperatur > obere Grenze | HIGH | Entwurf |
| R002 | K1 Temperatur < untere Grenze | MEDIUM | Entwurf |
| R003 | K2 Temperatur > obere Grenze | HIGH | Entwurf |
| R004 | K3 Temperatur > obere Grenze | HIGH | Entwurf |
| R005 | K4 Temperatur > Sollkühltemperatur + Toleranz | HIGH | Entwurf |

---

## 7.2 Füllstand-Regeln

| ID | Regel | Severity | Status |
|---|---|---|---|
| R010 | K3 Füllstand < Minimalwert | HIGH | Entwurf |
| R011 | K3 Füllstand > Maximalwert | HIGH | Entwurf |
| R012 | K2 Füllstand > Sollfüllstand | MEDIUM | Entwurf |
| R013 | Behälter leer trotz aktivem Heizbetrieb | CRITICAL | Entwurf |

---

## 7.3 Durchfluss-Regeln

| ID | Regel | Severity | Status |
|---|---|---|---|
| R020 | Pumpe aktiv aber DF = 0 | CRITICAL | Platzhalter |
| R021 | Durchfluss vorhanden trotz geschlossener Ventile | HIGH | Platzhalter |
| R022 | V4 offen aber K2 Füllstand steigt nicht | HIGH | Platzhalter |

Diese Regeln benötigen noch Ventil- und Pumpenzustände.

---

## 7.4 Sensor-Regeln

| ID | Regel | Severity | Status |
|---|---|---|---|
| R030 | Rohwert Temperatur stark abweichend vom Prozesswert | MEDIUM | Entwurf |
| R031 | Fehlender Temperaturwert | MEDIUM | Entwurf |
| R032 | Unplausibler Füllstandswert | HIGH | Entwurf |

---

## 7.5 Prozesslogik-Regeln

| ID | Regel | Severity | Status |
|---|---|---|---|
| R040 | K2 steigt bei geschlossenem V4 | HIGH | Platzhalter |
| R041 | Temperatur steigt ohne aktive Heizung | MEDIUM | Platzhalter |
| R042 | Medienfluss ohne offene Ventile | HIGH | Platzhalter |

---

# 8. Diagnostizierbare Anomalien 

| ID   | Anomalie                              | Diagnosebedingung                                                                                          | Severity                           | Warum diagnostizierbar?                                        |
| ---- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------- |
| A001 | K1 Temperatur zu hoch                 | `K1_Temperatur > K1_Temperatur_SollwertObereGrenze`                                                        | HIGH                               | K1-Temperatur und Grenzwert sind Pflicht-/Kontextdatenpunkte   |
| A002 | K1 Temperatur zu niedrig              | `K1_Temperatur < K1_Temperatur_SollwertUntereGrenze`                                                       | MEDIUM                             | direkt messbar                                                 |
| A003 | K2 Temperatur zu hoch                 | `K2_Temperatur > K2_Temperatur_SollwertObereGrenze`                                                        | HIGH                               | K2 ist Maischebehälter, Temperatur ist plausibel validiert     |
| A004 | K2 Temperatur zu niedrig              | `K2_Temperatur < K2_Temperatur_SollwertUntereGrenze`                                                       | MEDIUM                             | direkt messbar                                                 |
| A005 | K3 Temperatur zu hoch                 | `K3_Temperatur > K3_Temperatur_SollwertObereGrenze`                                                        | HIGH                               | K3 Temperatur ist Pflicht und plausibel                        |
| A006 | K3 Temperatur zu niedrig              | `K3_Temperatur < K3_Temperatur_SollwertUntereGrenze`                                                       | MEDIUM                             | direkt messbar                                                 |
| A007 | K3 Füllstand über Maximum             | `K3_Füllstand > K3_MaximalerFüllstand`                                                                     | HIGH, aber mit Validierungswarnung | K3_Füllstand ist Pflicht, aber aktuell zu prüfen               |
| A008 | K3 Füllstand unter Minimum            | `K3_Füllstand < K3_MinimalerFüllstand`                                                                     | HIGH, aber mit Validierungswarnung | nur verwenden, wenn K3_Füllstand plausibilisiert wurde         |
| A009 | Durchfluss zu niedrig beim Läutern    | Zustand `LAUTERING` und `Durchfluss_NachgussMaische < 0.5 l/min`                                           | HIGH                               | FSM nutzt `flow_rate ≥ 0.5` für `lautering_finished`           |
| A010 | Unerwarteter Durchfluss im Stillstand | Zustand `IDLE` oder `FINISHED` und `Durchfluss_NachgussMaische > 0.5 l/min`                                | MEDIUM/HIGH                        | Zustand + Durchfluss reichen zur Diagnose                      |
| A011 | Kühlziel nicht erreicht               | Zustand `COOLING` und `K3_Temperatur > 25 °C` nach definierter Zeit                                        | MEDIUM                             | FSM definiert `cooled_down` als K3 ≤ 25 °C                     |
| A012 | Gärtemperatur zu hoch                 | Zustand `FERMENTING` und `MobilerSensor_Temperatur > 18 °C + Toleranz`                                     | MEDIUM                             | K4 wird über mobilen Temperatursensor abgebildet               |
| A013 | Gärtemperatur zu niedrig              | Zustand `FERMENTING` und `MobilerSensor_Temperatur < 18 °C - Toleranz`                                     | MEDIUM                             | direkt diagnostizierbar                                        |
| A014 | Sensorwert unplausibel                | Temperaturwert fehlt, `None`, NaN oder außerhalb technischer Plausibilität, z. B. `< 0 °C` oder `> 110 °C` | HIGH                               | schützt FSM und API vor falscher Logik                         |
| A015 | K3_Füllstand unplausibel              | K3_Füllstand extrem groß/negativ oder außerhalb plausibler Anlagenkapazität                                | HIGH                               | Engineer A markiert K3_Füllstand ausdrücklich als Prüfkandidat |


# 9. Scope and Applicability

Die in diesem Dokument definierten Anomalie-Regeln beschränken sich auf Zustände, die anhand der derzeit validierten Prozessvariablen, FSM-Zustände und verfügbaren Stellgliedinformationen zuverlässig diagnostiziert werden können.
Um den Regelkatalog übersichtlich und umsetzungsorientiert zu halten, werden Annahmen, diagnostische Einschränkungen, offene technische Fragen und zukünftige Erweiterungen separat behandelt.

See:

👉 [Anomaly Assumptions & Limitations](./anomaly_known_limitations.md)

# 10. Vorläufiges Alarmformat

Das einheitliche Alarmformat ist im separaten Dokument [Alarm-Schema der Anomalieerkennung](./alarm_schema.md)
---