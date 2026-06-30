from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FaultCode(Enum):
    """Eindeutige AP4-Fehlercodes für AP5 und AP6.

    Namensschema:
    - ERROR_XXX_*: Prozess- oder Plausibilitätsfehler, Anlage wird kontrolliert angehalten.
    - EMERGENCY_XXX_*: Sicherheitsrelevante Ereignisse mit höchster Priorität.
    """

    ERROR_001_K3_NACHGUSS_TEMP_LOW = "ERROR_001_K3_NACHGUSS_TEMP_LOW"
    ERROR_002_K3_NACHGUSS_TEMP_HIGH = "ERROR_002_K3_NACHGUSS_TEMP_HIGH"
    ERROR_003_V3_CLOSED_IN_NACHGUSS = "ERROR_003_V3_CLOSED_IN_NACHGUSS"
    ERROR_004_FLOW_K3_TO_K1_LOW = "ERROR_004_FLOW_K3_TO_K1_LOW"
    ERROR_005_K1_MASHING_TEMP_LOW = "ERROR_005_K1_MASHING_TEMP_LOW"
    ERROR_006_K1_MASHING_TEMP_HIGH = "ERROR_006_K1_MASHING_TEMP_HIGH"
    ERROR_007_K1_LEVEL_LOW_MASHING = "ERROR_007_K1_LEVEL_LOW_MASHING"
    ERROR_008_V4_CLOSED_IN_LAUTERING = "ERROR_008_V4_CLOSED_IN_LAUTERING"
    ERROR_009_FLOW_K1_TO_K2_LOW = "ERROR_009_FLOW_K1_TO_K2_LOW"
    ERROR_010_K2_BOILING_TEMP_LOW = "ERROR_010_K2_BOILING_TEMP_LOW"
    ERROR_011_K2_BOILING_TEMP_HIGH = "ERROR_011_K2_BOILING_TEMP_HIGH"
    ERROR_012_K2_LEVEL_LOW_BOILING = "ERROR_012_K2_LEVEL_LOW_BOILING"
    ERROR_013_COOLING_TEMP_IMPLAUSIBLE = "ERROR_013_COOLING_TEMP_IMPLAUSIBLE"
    ERROR_014_V5_CLOSED_TRANSFER_K4 = "ERROR_014_V5_CLOSED_TRANSFER_K4"
    ERROR_015_PUMP_OFF_TRANSFER_K4 = "ERROR_015_PUMP_OFF_TRANSFER_K4"
    ERROR_016_FLOW_K2_TO_K4_LOW = "ERROR_016_FLOW_K2_TO_K4_LOW"
    ERROR_017_K4_FERMENT_TEMP_LOW = "ERROR_017_K4_FERMENT_TEMP_LOW"
    ERROR_018_K4_FERMENT_TEMP_HIGH = "ERROR_018_K4_FERMENT_TEMP_HIGH"
    ERROR_019_FORBIDDEN_TRANSITION = "ERROR_019_FORBIDDEN_TRANSITION"
    ERROR_020_AP3_REQUIRED_SIGNAL_MISSING = "ERROR_020_AP3_REQUIRED_SIGNAL_MISSING"

    EMERGENCY_001_ESTOP_ACTIVE = "EMERGENCY_001_ESTOP_ACTIVE"
    EMERGENCY_002_SENSOR_NOT_OK = "EMERGENCY_002_SENSOR_NOT_OK"
    EMERGENCY_003_K3_TEMP_TOO_LOW = "EMERGENCY_003_K3_TEMP_TOO_LOW"
    EMERGENCY_004_K3_TEMP_TOO_HIGH = "EMERGENCY_004_K3_TEMP_TOO_HIGH"
    EMERGENCY_005_K1_TEMP_TOO_LOW = "EMERGENCY_005_K1_TEMP_TOO_LOW"
    EMERGENCY_006_K1_TEMP_TOO_HIGH = "EMERGENCY_006_K1_TEMP_TOO_HIGH"
    EMERGENCY_007_K2_TEMP_TOO_LOW = "EMERGENCY_007_K2_TEMP_TOO_LOW"
    EMERGENCY_008_K2_TEMP_TOO_HIGH = "EMERGENCY_008_K2_TEMP_TOO_HIGH"
    EMERGENCY_009_K4_TEMP_TOO_LOW = "EMERGENCY_009_K4_TEMP_TOO_LOW"
    EMERGENCY_010_K4_TEMP_TOO_HIGH = "EMERGENCY_010_K4_TEMP_TOO_HIGH"
    EMERGENCY_011_K3_LEVEL_NEGATIVE = "EMERGENCY_011_K3_LEVEL_NEGATIVE"
    EMERGENCY_012_K3_LEVEL_TOO_HIGH = "EMERGENCY_012_K3_LEVEL_TOO_HIGH"
    EMERGENCY_013_K1_LEVEL_NEGATIVE = "EMERGENCY_013_K1_LEVEL_NEGATIVE"
    EMERGENCY_014_K1_LEVEL_TOO_HIGH = "EMERGENCY_014_K1_LEVEL_TOO_HIGH"
    EMERGENCY_015_K2_LEVEL_NEGATIVE = "EMERGENCY_015_K2_LEVEL_NEGATIVE"
    EMERGENCY_016_K2_LEVEL_TOO_HIGH = "EMERGENCY_016_K2_LEVEL_TOO_HIGH"
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
    ap5_usage: str
    ap6_usage: str
    recommended_action: str


def _d(code: FaultCode, superstate: str, title: str, subsystem: str, state_hint: str, action: str) -> FaultDescriptor:
    return FaultDescriptor(
        code=code,
        superstate=superstate,
        title=title,
        subsystem=subsystem,
        state_hint=state_hint,
        ap5_usage="Regel- und Ursachenklassifikation über active_fault_code, signal, value und limit.",
        ap6_usage="Dashboard-Anzeige als eindeutige Alarmkarte mit Code, Titel, Signal, Wert und Handlungsempfehlung.",
        recommended_action=action,
    )


FAULT_CATALOG: dict[FaultCode, FaultDescriptor] = {
    FaultCode.ERROR_001_K3_NACHGUSS_TEMP_LOW: _d(FaultCode.ERROR_001_K3_NACHGUSS_TEMP_LOW, "ERROR", "K3 Nachgusstemperatur zu niedrig", "K3/Nachguss", "NACHGUSS", "K3-Heizung, Sensor und Rezeptwert prüfen."),
    FaultCode.ERROR_002_K3_NACHGUSS_TEMP_HIGH: _d(FaultCode.ERROR_002_K3_NACHGUSS_TEMP_HIGH, "ERROR", "K3 Nachgusstemperatur zu hoch", "K3/Nachguss", "NACHGUSS", "K3-Heizung abschalten, Abkühlung abwarten, Sensor plausibilisieren."),
    FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS: _d(FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS, "ERROR", "V3 im Nachguss geschlossen", "Ventil V3", "NACHGUSS", "Ventilstellung V3 und Rückmeldung prüfen."),
    FaultCode.ERROR_004_FLOW_K3_TO_K1_LOW: _d(FaultCode.ERROR_004_FLOW_K3_TO_K1_LOW, "ERROR", "Durchfluss K3 nach K1 zu niedrig", "Durchfluss K3->K1", "NACHGUSS", "V3, Leitung, DF-Sensor und Behälterfüllstand prüfen."),
    FaultCode.ERROR_005_K1_MASHING_TEMP_LOW: _d(FaultCode.ERROR_005_K1_MASHING_TEMP_LOW, "ERROR", "K1 Maischtemperatur zu niedrig", "K1/Maischen", "MASHING", "Kochfeld 1, Temperaturfühler und Rezeptfenster prüfen."),
    FaultCode.ERROR_006_K1_MASHING_TEMP_HIGH: _d(FaultCode.ERROR_006_K1_MASHING_TEMP_HIGH, "ERROR", "K1 Maischtemperatur zu hoch", "K1/Maischen", "MASHING", "Kochfeld 1 abschalten und Temperaturmessung validieren."),
    FaultCode.ERROR_007_K1_LEVEL_LOW_MASHING: _d(FaultCode.ERROR_007_K1_LEVEL_LOW_MASHING, "ERROR", "K1-Füllstand für Maischen zu niedrig", "K1/Füllstand", "MASHING", "Nachgussmenge und Füllstandssensor K1 prüfen."),
    FaultCode.ERROR_008_V4_CLOSED_IN_LAUTERING: _d(FaultCode.ERROR_008_V4_CLOSED_IN_LAUTERING, "ERROR", "V4 beim Läutern geschlossen", "Ventil V4", "LAUTERING", "Ventilstellung V4 und Rückmeldung prüfen."),
    FaultCode.ERROR_009_FLOW_K1_TO_K2_LOW: _d(FaultCode.ERROR_009_FLOW_K1_TO_K2_LOW, "ERROR", "Durchfluss K1 nach K2 zu niedrig", "Durchfluss K1->K2", "LAUTERING", "V4, Leitung und Durchflussmessung prüfen."),
    FaultCode.ERROR_010_K2_BOILING_TEMP_LOW: _d(FaultCode.ERROR_010_K2_BOILING_TEMP_LOW, "ERROR", "K2 Kochtemperatur zu niedrig", "K2/Kochen", "BOILING", "Kochfeld 2 und Temperaturfühler K2 prüfen."),
    FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH: _d(FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH, "ERROR", "K2 Kochtemperatur zu hoch", "K2/Kochen", "BOILING", "Kochfeld 2 abschalten und Temperatur validieren."),
    FaultCode.ERROR_012_K2_LEVEL_LOW_BOILING: _d(FaultCode.ERROR_012_K2_LEVEL_LOW_BOILING, "ERROR", "K2-Füllstand für Kochen zu niedrig", "K2/Füllstand", "BOILING", "Transfer K1->K2 und Sensor K2 prüfen."),
    FaultCode.ERROR_013_COOLING_TEMP_IMPLAUSIBLE: _d(FaultCode.ERROR_013_COOLING_TEMP_IMPLAUSIBLE, "ERROR", "Kühlphase mit unplausibel hoher Temperatur", "Kühlung", "COOLING", "Kühlung, Sensorwert und Phasenwechsel prüfen."),
    FaultCode.ERROR_014_V5_CLOSED_TRANSFER_K4: _d(FaultCode.ERROR_014_V5_CLOSED_TRANSFER_K4, "ERROR", "V5 beim Austrag geschlossen", "Ventil V5", "TRANSFER_TO_K4", "Ventilstellung V5 und Rückmeldung prüfen."),
    FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4: _d(FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4, "ERROR", "Pumpe beim Austrag ausgeschaltet", "Pumpe", "TRANSFER_TO_K4", "Pumpenrückmeldung, Motorschutz und Ansteuerung prüfen."),
    FaultCode.ERROR_016_FLOW_K2_TO_K4_LOW: _d(FaultCode.ERROR_016_FLOW_K2_TO_K4_LOW, "ERROR", "Durchfluss K2 nach K4 zu niedrig", "Durchfluss K2->K4", "TRANSFER_TO_K4", "Pumpe, V5, Leitung und DF-Sensor prüfen."),
    FaultCode.ERROR_017_K4_FERMENT_TEMP_LOW: _d(FaultCode.ERROR_017_K4_FERMENT_TEMP_LOW, "ERROR", "K4 Gärtemperatur zu niedrig", "K4/Gären", "FERMENTING", "Umgebung, mobiler Sensor und Gärbedingungen prüfen."),
    FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH: _d(FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH, "ERROR", "K4 Gärtemperatur zu hoch", "K4/Gären", "FERMENTING", "Kühl-/Umgebungsbedingungen prüfen."),
    FaultCode.ERROR_019_FORBIDDEN_TRANSITION: _d(FaultCode.ERROR_019_FORBIDDEN_TRANSITION, "ERROR", "Verbotener Zustandsübergang", "FSM/Sequenz", "GLOBAL", "Softwarelogik, Bedienbefehl oder SPS-Schritt prüfen."),
    FaultCode.ERROR_020_AP3_REQUIRED_SIGNAL_MISSING: _d(FaultCode.ERROR_020_AP3_REQUIRED_SIGNAL_MISSING, "ERROR", "Pflichtsignal aus AP3 fehlt", "AP3/AP4-Schnittstelle", "GLOBAL", "OPC-UA-Mapping, Knotenliste und Collector prüfen."),
    FaultCode.EMERGENCY_001_ESTOP_ACTIVE: _d(FaultCode.EMERGENCY_001_ESTOP_ACTIVE, "EMERGENCY", "Not-Aus aktiv", "Safety", "GLOBAL", "Not-Aus Ursache beseitigen und anschließend quittieren."),
    FaultCode.EMERGENCY_002_SENSOR_NOT_OK: _d(FaultCode.EMERGENCY_002_SENSOR_NOT_OK, "EMERGENCY", "Sensorstatus nicht OK", "Safety", "GLOBAL", "Sensorversorgung, IO-Link/Analogsignal und Diagnose prüfen."),
    FaultCode.EMERGENCY_003_K3_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_003_K3_TEMP_TOO_LOW, "EMERGENCY", "K3 Temperatur unter absoluter Grenze", "K3/Safety", "GLOBAL", "Sensorfehler oder unplausible Messung prüfen."),
    FaultCode.EMERGENCY_004_K3_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_004_K3_TEMP_TOO_HIGH, "EMERGENCY", "K3 Temperatur über absoluter Grenze", "K3/Safety", "GLOBAL", "Heizung abschalten und Sicherheitsprüfung durchführen."),
    FaultCode.EMERGENCY_005_K1_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_005_K1_TEMP_TOO_LOW, "EMERGENCY", "K1 Temperatur unter absoluter Grenze", "K1/Safety", "GLOBAL", "Sensorfehler oder unplausible Messung prüfen."),
    FaultCode.EMERGENCY_006_K1_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_006_K1_TEMP_TOO_HIGH, "EMERGENCY", "K1 Temperatur über absoluter Grenze", "K1/Safety", "GLOBAL", "Kochfeld 1 abschalten und Safety-Review durchführen."),
    FaultCode.EMERGENCY_007_K2_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_007_K2_TEMP_TOO_LOW, "EMERGENCY", "K2 Temperatur unter absoluter Grenze", "K2/Safety", "GLOBAL", "Sensorfehler oder unplausible Messung prüfen."),
    FaultCode.EMERGENCY_008_K2_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_008_K2_TEMP_TOO_HIGH, "EMERGENCY", "K2 Temperatur über absoluter Grenze", "K2/Safety", "GLOBAL", "Kochfeld 2 abschalten und Safety-Review durchführen."),
    FaultCode.EMERGENCY_009_K4_TEMP_TOO_LOW: _d(FaultCode.EMERGENCY_009_K4_TEMP_TOO_LOW, "EMERGENCY", "K4 Temperatur unter absoluter Grenze", "K4/Safety", "GLOBAL", "Mobilsensor prüfen."),
    FaultCode.EMERGENCY_010_K4_TEMP_TOO_HIGH: _d(FaultCode.EMERGENCY_010_K4_TEMP_TOO_HIGH, "EMERGENCY", "K4 Temperatur über absoluter Grenze", "K4/Safety", "GLOBAL", "Gärbehälterumgebung und Mobilsensor prüfen."),
    FaultCode.EMERGENCY_011_K3_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_011_K3_LEVEL_NEGATIVE, "EMERGENCY", "K3 Füllstand negativ", "K3/Safety", "GLOBAL", "Füllstandsmessung K3 prüfen."),
    FaultCode.EMERGENCY_012_K3_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_012_K3_LEVEL_TOO_HIGH, "EMERGENCY", "K3 Füllstand über Schutzgrenze", "K3/Safety", "GLOBAL", "Überfüllung und Sensor K3 prüfen."),
    FaultCode.EMERGENCY_013_K1_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_013_K1_LEVEL_NEGATIVE, "EMERGENCY", "K1 Füllstand negativ", "K1/Safety", "GLOBAL", "Füllstandsmessung K1 prüfen."),
    FaultCode.EMERGENCY_014_K1_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_014_K1_LEVEL_TOO_HIGH, "EMERGENCY", "K1 Füllstand über Schutzgrenze", "K1/Safety", "GLOBAL", "Überfüllung und Sensor K1 prüfen."),
    FaultCode.EMERGENCY_015_K2_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_015_K2_LEVEL_NEGATIVE, "EMERGENCY", "K2 Füllstand negativ", "K2/Safety", "GLOBAL", "Füllstandsmessung K2 prüfen."),
    FaultCode.EMERGENCY_016_K2_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_016_K2_LEVEL_TOO_HIGH, "EMERGENCY", "K2 Füllstand über Schutzgrenze", "K2/Safety", "GLOBAL", "Überfüllung und Sensor K2 prüfen."),
    FaultCode.EMERGENCY_017_K4_LEVEL_NEGATIVE: _d(FaultCode.EMERGENCY_017_K4_LEVEL_NEGATIVE, "EMERGENCY", "K4 Füllstand negativ", "K4/Safety", "GLOBAL", "Füllstandsmessung K4 prüfen."),
    FaultCode.EMERGENCY_018_K4_LEVEL_TOO_HIGH: _d(FaultCode.EMERGENCY_018_K4_LEVEL_TOO_HIGH, "EMERGENCY", "K4 Füllstand über Schutzgrenze", "K4/Safety", "GLOBAL", "Überfüllung und Sensor K4 prüfen."),
    FaultCode.EMERGENCY_019_DATA_STALE: _d(FaultCode.EMERGENCY_019_DATA_STALE, "EMERGENCY", "Messwerte zu alt", "AP3/AP4-Safety", "GLOBAL", "Collector, Netzwerk und Timestamp prüfen."),
}


def descriptor_for(code: FaultCode | str) -> FaultDescriptor:
    if isinstance(code, str):
        code = FaultCode(code)
    return FAULT_CATALOG[code]


def codes_by_superstate(superstate: str) -> list[FaultCode]:
    return [code for code, desc in FAULT_CATALOG.items() if desc.superstate == superstate]
