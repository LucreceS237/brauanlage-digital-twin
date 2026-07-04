"""
File: mapping.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Single source of truth for the APPROVED physical Anlage mapping and the translation from MQTT/SPS payload fields into the canonical fields that the AP4 FSM (Engineer C) consumes.
"""
from __future__ import annotations

# Approved physical vessel roles (for labels/documentation and the frontend).
APPROVED_VESSELS: dict[str, str] = {
    "K1": "Nachgussbehälter",
    "K2": "Maischebehälter",
    "K3": "Läuterbehälter",
    "K4": "Gärbehälter",
}

# Which approved vessel each brewing phase primarily uses.
PHASE_PRIMARY_VESSEL: dict[str, str] = {
    "IDLE": "-",
    "PRECHECK": "K1",
    "NACHGUSS": "K1",
    "MASHING": "K2",
    "LAUTERING": "K3",
    "BOILING": "K3",
    "COOLING": "K3",
    "TRANSFER_TO_K4": "K4",
    "FERMENTING": "K4",
    "FINISHED": "-",
    "ERROR": "-",
    "EMERGENCY": "-",
}

# Approved MQTT temperature field  ->  AP4 canonical field (the rotation).
TEMPERATURE_MAP: dict[str, str] = {
    "K1_Temperatur": "k3_temperature_c",            # Nachguss  -> AP4 nachguss role
    "K2_Temperatur": "k1_temperature_c",            # Maische   -> AP4 mash role
    "K3_Temperatur": "k2_temperature_c",            # Läuter    -> AP4 lauter/boil role
    "MobilerSensor_Temperatur": "k4_temperature_c",  # Gär       -> AP4 ferment role
}

# Approved MQTT level field  ->  AP4 canonical level field (same rotation).
LEVEL_MAP: dict[str, str] = {
    "K2_Füllstand": "k1_level_l",  # Maische level -> AP4 mash level
    "K3_Füllstand": "k2_level_l",  # Läuter level  -> AP4 lauter/boil level
}

# The single measured flow (Nachguss -> Maische) is AP4's k3->k1 (nachguss) flow.
FLOW_MAP: dict[str, str] = {
    "Durchfluss_NachgussMaische": "flow_k3_to_k1_l_min",
}

# Human-readable meaning of each AP4 canonical field AFTER correction.
AP4_FIELD_MEANING: dict[str, str] = {
    "k3_temperature_c": "K1 Nachguss temperature (°C)",
    "k1_temperature_c": "K2 Mashing temperature (°C)",
    "k2_temperature_c": "K3 Lautering/Boiling temperature (°C)",
    "k4_temperature_c": "K4 Fermentation temperature (°C)",
    "flow_k3_to_k1_l_min": "Durchfluss Nachguss->Maische (L/min)",
}
