from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FaultCode(Enum):
    """Eindeutige AP4-Fehlercodes für AP5 und AP6.

    Es wird nicht nur ERROR oder EMERGENCY gemeldet. Jeder konkrete Fehler
    besitzt einen stabilen Code. Damit kann AP5 regelbasiert auswerten und AP6
    eine eindeutige Alarmkarte anzeigen.
    """

    ERROR_001_K1_NACHGUSS_TEMP_LOW = "ERROR_001_K1_NACHGUSS_TEMP_LOW"
    ERROR_002_K1_NACHGUSS_TEMP_HIGH = "ERROR_002_K1_NACHGUSS_TEMP_HIGH"
    ERROR_003_V3_CLOSED_IN_NACHGUSS = "ERROR_003_V3_CLOSED_IN_NACHGUSS"
    ERROR_004_FLOW_K1_TO_K2_LOW = "ERROR_004_FLOW_K1_TO_K2_LOW"
    ERROR_005_K2_MASHING_TEMP_LOW = "ERROR_005_K2_MASHING_TEMP_LOW"
    ERROR_006_K2_MASHING_TEMP_HIGH = "ERROR_006_K2_MASHING_TEMP_HIGH"
    ERROR_007_K2_LEVEL_LOW_MASHING = "ERROR_007_K2_LEVEL_LOW_MASHING"
    ERROR_008_V4_CLOSED_TRANSFER_K3 = "ERROR_008_V4_CLOSED_TRANSFER_K3"
    ERROR_009_K3_LEVEL_LOW_LAUTERING = "ERROR_009_K3_LEVEL_LOW_LAUTERING"
    ERROR_010_K2_BOILING_TEMP_LOW = "ERROR_010_K2_BOILING_TEMP_LOW"
    ERROR_011_K2_BOILING_TEMP_HIGH = "ERROR_011_K2_BOILING_TEMP_HIGH"
    ERROR_012_K2_LEVEL_LOW_BOILING = "ERROR_012_K2_LEVEL_LOW_BOILING"
    ERROR_013_COOLING_TEMP_NOT_REACHED = "ERROR_013_COOLING_TEMP_NOT_REACHED"
    ERROR_014_V5_CLOSED_TRANSFER_K4 = "ERROR_014_V5_CLOSED_TRANSFER_K4"
    ERROR_015_PUMP_OFF_TRANSFER_K4 = "ERROR_015_PUMP_OFF_TRANSFER_K4"
    ERROR_016_K4_LEVEL_LOW_TRANSFER = "ERROR_016_K4_LEVEL_LOW_TRANSFER"
    ERROR_017_K4_FERMENT_TEMP_LOW = "ERROR_017_K4_FERMENT_TEMP_LOW"
    ERROR_018_K4_FERMENT_TEMP_HIGH = "ERROR_018_K4_FERMENT_TEMP_HIGH"
    ERROR_019_FORBIDDEN_TRANSITION = "ERROR_019_FORBIDDEN_TRANSITION"
    ERROR_020_AP3_REQUIRED_SIGNAL_MISSING = "ERROR_020_AP3_REQUIRED_SIGNAL_MISSING"
    ERROR_021_DATA_QUALITY_BAD = "ERROR_021_DATA_QUALITY_BAD"

    EMERGENCY_001_ESTOP_ACTIVE = "EMERGENCY_001_ESTOP_ACTIVE"
    EMERGENCY_002_SENSOR_NOT_OK = "EMERGENCY_002_SENSOR_NOT_OK"
    EMERGENCY_003_K1_TEMP_TOO_LOW = "EMERGENCY_003_K1_TEMP_TOO_LOW"
    EMERGENCY_004_K1_TEMP_TOO_HIGH = "EMERGENCY_004_K1_TEMP_TOO_HIGH"
    EMERGENCY_005_K2_TEMP_TOO_LOW = "EMERGENCY_005_K2_TEMP_TOO_LOW"
    EMERGENCY_006_K2_TEMP_TOO_HIGH = "EMERGENCY_006_K2_TEMP_TOO_HIGH"
    EMERGENCY_007_K3_TEMP_TOO_LOW = "EMERGENCY_007_K3_TEMP_TOO_LOW"
    EMERGENCY_008_K3_TEMP_TOO_HIGH = "EMERGENCY_008_K3_TEMP_TOO_HIGH"
    EMERGENCY_009_K4_TEMP_TOO_LOW = "EMERGENCY_009_K4_TEMP_TOO_LOW"
    EMERGENCY_010_K4_TEMP_TOO_HIGH = "EMERGENCY_010_K4_TEMP_TOO_HIGH"
    EMERGENCY_011_K1_LEVEL_NEGATIVE = "EMERGENCY_011_K1_LEVEL_NEGATIVE"
    EMERGENCY_012_K1_LEVEL_TOO_HIGH = "EMERGENCY_012_K1_LEVEL_TOO_HIGH"
    EMERGENCY_013_K2_LEVEL_NEGATIVE = "EMERGENCY_013_K2_LEVEL_NEGATIVE"
    EMERGENCY_014_K2_LEVEL_TOO_HIGH = "EMERGENCY_014_K2_LEVEL_TOO_HIGH"
    EMERGENCY_015_K3_LEVEL_NEGATIVE = "EMERGENCY_015_K3_LEVEL_NEGATIVE"
    EMERGENCY_016_K3_LEVEL_TOO_HIGH = "EMERGENCY_016_K3_LEVEL_TOO_HIGH"
    EMERGENCY_017_K4_LEVEL_NEGATIVE = "EMERGENCY_017_K4_LEVEL_NEGATIVE"
    EMERGENCY_018_K4_LEVEL_TOO_HIGH = "EMERGENCY_018_K4_LEVEL_TOO_HIGH"
    EMERGENCY_019_DATA_STALE = "EMERGENCY_019_DATA_STALE"


@dataclass(frozen=True)
class FaultDescriptor:
    code: FaultCode
    superstate: str
    title: str
    subsystem: str
    state_hint: str
    recommended_action: str


def _d(code: FaultCode, superstate: str, title: str, subsystem: str, state_hint: str, action: str) -> FaultDescriptor:
    return FaultDescriptor(code, superstate, title, subsystem, state_hint, action)


FAULT_CATALOG: dict[FaultCode, FaultDescriptor] = {
    FaultCode.ERROR_001_K1_NACHGUSS_TEMP_LOW: _d(FaultCode.ERROR_001_K1_NACHGUSS_TEMP_LOW, "ERROR", "K1-Nachgusstemperatur zu niedrig", "K1 Nachguss", "NACHGUSS", "K1-Heizung, Sollwert und Sensor prüfen."),
    FaultCode.ERROR_002_K1_NACHGUSS_TEMP_HIGH: _d(FaultCode.ERROR_002_K1_NACHGUSS_TEMP_HIGH, "ERROR", "K1-Nachgusstemperatur zu hoch", "K1 Nachguss", "NACHGUSS", "K1-Heizung abschalten und Sensor plausibilisieren."),
    FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS: _d(FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS, "ERROR", "V3 im Nachguss geschlossen", "Ventil V3", "NACHGUSS", "V3 öffnen oder Rückmeldung prüfen."),
    FaultCode.ERROR_004_FLOW_K1_TO_K2_LOW: _d(FaultCode.ERROR_004_FLOW_K1_TO_K2_LOW, "ERROR", "Durchfluss K1->K2 zu niedrig", "Durchfluss K1->K2", "NACHGUSS", "Durchflussmesser, V3, Leitung und Füllstand prüfen."),
    FaultCode.ERROR_005_K2_MASHING_TEMP_LOW: _d(FaultCode.ERROR_005_K2_MASHING_TEMP_LOW, "ERROR", "K2-Maischtemperatur zu niedrig", "K2 Maischen", "MASHING", "K2-Heizung und Rezeptfenster prüfen."),
    FaultCode.ERROR_006_K2_MASHING_TEMP_HIGH: _d(FaultCode.ERROR_006_K2_MASHING_TEMP_HIGH, "ERROR", "K2-Maischtemperatur zu hoch", "K2 Maischen", "MASHING", "Heizung abschalten und Sensor prüfen."),
    FaultCode.ERROR_007_K2_LEVEL_LOW_MASHING: _d(FaultCode.ERROR_007_K2_LEVEL_LOW_MASHING, "ERROR", "K2-Füllstand für Maischen zu niedrig", "K2 Füllstand", "MASHING", "Nachgussmenge und Füllstandsmessung prüfen."),
    FaultCode.ERROR_008_V4_CLOSED_TRANSFER_K3: _d(FaultCode.ERROR_008_V4_CLOSED_TRANSFER_K3, "ERROR", "V4 beim Transfer nach K3 geschlossen", "Ventil V4", "TRANSFER_TO_K3", "V4 und Transferfreigabe prüfen."),
    FaultCode.ERROR_009_K3_LEVEL_LOW_LAUTERING: _d(FaultCode.ERROR_009_K3_LEVEL_LOW_LAUTERING, "ERROR", "K3-Füllstand für Läutern zu niedrig", "K3 Läutern", "LAUTERING", "Transfer K2->K3 und K3-Füllstand prüfen."),
    FaultCode.ERROR_010_K2_BOILING_TEMP_LOW: _d(FaultCode.ERROR_010_K2_BOILING_TEMP_LOW, "ERROR", "K2-Kochtemperatur zu niedrig", "K2 Kochen", "BOILING", "K2-Heizung und Rezeptfenster prüfen."),
    FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH: _d(FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH, "ERROR", "K2-Kochtemperatur zu hoch", "K2 Kochen", "BOILING", "K2-Heizung abschalten und Sensor prüfen."),
    FaultCode.ERROR_012_K2_LEVEL_LOW_BOILING: _d(FaultCode.ERROR_012_K2_LEVEL_LOW_BOILING, "ERROR", "K2-Füllstand beim Kochen zu niedrig", "K2 Kochen", "BOILING", "Füllstand und Trockenlaufgefahr prüfen."),
    FaultCode.ERROR_013_COOLING_TEMP_NOT_REACHED: _d(FaultCode.ERROR_013_COOLING_TEMP_NOT_REACHED, "ERROR", "Kühltemperatur nicht erreicht", "K2/Kühlen", "COOLING", "Kühlung und Temperatursensor prüfen."),
    FaultCode.ERROR_014_V5_CLOSED_TRANSFER_K4: _d(FaultCode.ERROR_014_V5_CLOSED_TRANSFER_K4, "ERROR", "V5 beim Transfer nach K4 geschlossen", "Ventil V5", "TRANSFER_TO_K4", "V5 und Austrag prüfen."),
    FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4: _d(FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4, "ERROR", "Pumpe beim Transfer nach K4 aus", "Pumpe", "TRANSFER_TO_K4", "Pumpenfreigabe und Rückmeldung prüfen."),
    FaultCode.ERROR_016_K4_LEVEL_LOW_TRANSFER: _d(FaultCode.ERROR_016_K4_LEVEL_LOW_TRANSFER, "ERROR", "K4-Füllstand nach Transfer zu niedrig", "K4 Gärung", "TRANSFER_TO_K4", "Austrag und K4-Füllstand prüfen."),
    FaultCode.ERROR_017_K4_FERMENT_TEMP_LOW: _d(FaultCode.ERROR_017_K4_FERMENT_TEMP_LOW, "ERROR", "K4-Gärtemperatur zu niedrig", "K4 Gärung", "FERMENTING", "Gärtemperatur prüfen."),
    FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH: _d(FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH, "ERROR", "K4-Gärtemperatur zu hoch", "K4 Gärung", "FERMENTING", "Kühlung/Umgebung prüfen."),
    FaultCode.ERROR_019_FORBIDDEN_TRANSITION: _d(FaultCode.ERROR_019_FORBIDDEN_TRANSITION, "ERROR", "Unzulässiger Zustandsübergang", "FSM", "ANY", "Zustandsfolge und Bedienereingriff prüfen."),
    FaultCode.ERROR_020_AP3_REQUIRED_SIGNAL_MISSING: _d(FaultCode.ERROR_020_AP3_REQUIRED_SIGNAL_MISSING, "ERROR", "AP3-Pflichtsignal fehlt", "AP3 Schnittstelle", "ANY", "AP3-Snapshot und MQTT/CSV-Mapping prüfen."),
    FaultCode.ERROR_021_DATA_QUALITY_BAD: _d(FaultCode.ERROR_021_DATA_QUALITY_BAD, "ERROR", "Datenqualität nicht GOOD", "AP3 Schnittstelle", "ANY", "Qualitätsstatus und OPC-UA-Verbindung prüfen."),
    FaultCode.EMERGENCY_001_ESTOP_ACTIVE: _d(FaultCode.EMERGENCY_001_ESTOP_ACTIVE, "EMERGENCY", "Not-Aus aktiv", "Safety", "ANY", "Anlage sichern und Not-Aus quittieren."),
    FaultCode.EMERGENCY_002_SENSOR_NOT_OK: _d(FaultCode.EMERGENCY_002_SENSOR_NOT_OK, "EMERGENCY", "Sensorstatus nicht OK", "Safety", "ANY", "Sensorik prüfen."),
    FaultCode.EMERGENCY_003_K1_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_003_K1_TEMP_TOO_LOW, "EMERGENCY", "K1-Temperatur absolut zu niedrig", "K1", "ANY", "Sensor/Anlage prüfen."),
    FaultCode.EMERGENCY_004_K1_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_004_K1_TEMP_TOO_HIGH, "EMERGENCY", "K1-Temperatur absolut zu hoch", "K1", "ANY", "Heizung abschalten, Anlage sichern."),
    FaultCode.EMERGENCY_005_K2_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_005_K2_TEMP_TOO_LOW, "EMERGENCY", "K2-Temperatur absolut zu niedrig", "K2", "ANY", "Sensor/Anlage prüfen."),
    FaultCode.EMERGENCY_006_K2_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_006_K2_TEMP_TOO_HIGH, "EMERGENCY", "K2-Temperatur absolut zu hoch", "K2", "ANY", "Heizung abschalten, Anlage sichern."),
    FaultCode.EMERGENCY_007_K3_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_007_K3_TEMP_TOO_LOW, "EMERGENCY", "K3-Temperatur absolut zu niedrig", "K3", "ANY", "Sensor prüfen."),
    FaultCode.EMERGENCY_008_K3_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_008_K3_TEMP_TOO_HIGH, "EMERGENCY", "K3-Temperatur absolut zu hoch", "K3", "ANY", "Anlage sichern."),
    FaultCode.EMERGENCY_009_K4_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_009_K4_TEMP_TOO_LOW, "EMERGENCY", "K4-Temperatur absolut zu niedrig", "K4", "ANY", "Sensor prüfen."),
    FaultCode.EMERGENCY_010_K4_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_010_K4_TEMP_TOO_HIGH, "EMERGENCY", "K4-Temperatur absolut zu hoch", "K4", "ANY", "Anlage sichern."),
    FaultCode.EMERGENCY_011_K1_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_011_K1_LEVEL_NEGATIVE, "EMERGENCY", "K1-Füllstand negativ", "K1", "ANY", "Skalierung prüfen."),
    FaultCode.EMERGENCY_012_K1_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_012_K1_LEVEL_TOO_HIGH, "EMERGENCY", "K1-Füllstand zu hoch", "K1", "ANY", "Überfüllung/Skalierung prüfen."),
    FaultCode.EMERGENCY_013_K2_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_013_K2_LEVEL_NEGATIVE, "EMERGENCY", "K2-Füllstand negativ", "K2", "ANY", "Skalierung prüfen."),
    FaultCode.EMERGENCY_014_K2_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_014_K2_LEVEL_TOO_HIGH, "EMERGENCY", "K2-Füllstand zu hoch", "K2", "ANY", "Überfüllung prüfen."),
    FaultCode.EMERGENCY_015_K3_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_015_K3_LEVEL_NEGATIVE, "EMERGENCY", "K3-Füllstand negativ", "K3", "ANY", "Skalierung prüfen."),
    FaultCode.EMERGENCY_016_K3_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_016_K3_LEVEL_TOO_HIGH, "EMERGENCY", "K3-Füllstand zu hoch", "K3", "ANY", "Überfüllung prüfen."),
    FaultCode.EMERGENCY_017_K4_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_017_K4_LEVEL_NEGATIVE, "EMERGENCY", "K4-Füllstand negativ", "K4", "ANY", "Skalierung prüfen."),
    FaultCode.EMERGENCY_018_K4_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_018_K4_LEVEL_TOO_HIGH, "EMERGENCY", "K4-Füllstand zu hoch", "K4", "ANY", "Überfüllung prüfen."),
    FaultCode.EMERGENCY_019_DATA_STALE: _d(FaultCode.EMERGENCY_019_DATA_STALE, "EMERGENCY", "AP3-Daten zu alt", "AP3 Schnittstelle", "ANY", "Datenerfassung/Reconnection prüfen."),
}


def descriptor_for(code: FaultCode) -> FaultDescriptor:
    return FAULT_CATALOG[code]
