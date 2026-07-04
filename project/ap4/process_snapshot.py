"""
File: process_snapshot.py
Work Package: AP4
Responsible Engineer: Engineer C
Purpose: AP4 FSM module: process_snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping


def _float(values: Mapping[str, Any], name: str, default: float = 0.0) -> float:
    value = values.get(name, default)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bool(values: Mapping[str, Any], name: str, default: bool = False) -> bool:
    value = values.get(name, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "ja", "yes", "on"}


def _int(values: Mapping[str, Any], name: str, default: int = 0) -> int:
    value = values.get(name, default)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class ProcessSnapshot:
    """Normiertes Prozessabbild aus AP3.

    AP4 verarbeitet ausschließlich kanonische Signale, keine OPC-UA-NodeIds.
    Dadurch sind Simulation, Replay und Live-Betrieb identisch testbar.
    """

    timestamp_s: float = 0.0
    aktueller_schritt: int = 0
    start_requested: bool = False
    acknowledge: bool = False
    reset_requested: bool = False
    emergency_stop: bool = False
    sensor_ok: bool = True

    k3_temperature_c: float = 78.0
    k3_level_l: float = 10.0
    k3_level_min: bool = False
    k3_level_max: bool = False

    k1_temperature_c: float = 65.0
    k1_level_l: float = 0.0
    k1_level_full: bool = False

    k2_temperature_c: float = 20.0
    k2_level_l: float = 0.0
    k2_level_full: bool = False

    k4_temperature_c: float = 20.0
    k4_level_l: float = 0.0

    flow_k3_to_k1_l_min: float = 0.0
    flow_k1_to_k2_l_min: float = 0.0
    flow_k2_to_k4_l_min: float = 0.0

    v3_open: bool = False
    v4_open: bool = False
    v5_open: bool = False
    nv1_closed: bool = True
    nv2_closed: bool = True
    nv3_closed: bool = True

    heater_k1_on_feedback: bool = False
    heater_k2_on_feedback: bool = False
    agitator_on_feedback: bool = False
    pump_on_feedback: bool = False

    missing_value_age_s: float = 0.0

    @classmethod
    def from_opc_values(cls, values: Mapping[str, Any]) -> "ProcessSnapshot":
        aliases = dict(values)
        if "k3_temperatur" in aliases:
            aliases.setdefault("k3_temperature_c", aliases["k3_temperatur"])
        if "k1_temperatur" in aliases:
            aliases.setdefault("k1_temperature_c", aliases["k1_temperatur"])
        if "k2_temperatur" in aliases:
            aliases.setdefault("k2_temperature_c", aliases["k2_temperatur"])
        if "mobiler_sensor_temperatur" in aliases:
            aliases.setdefault("k4_temperature_c", aliases["mobiler_sensor_temperatur"])
        if "durchfluss_nachguss_maische" in aliases:
            aliases.setdefault("flow_k3_to_k1_l_min", aliases["durchfluss_nachguss_maische"])

        return cls(
            timestamp_s=_float(aliases, "timestamp_s"),
            aktueller_schritt=_int(aliases, "aktueller_schritt"),
            start_requested=_bool(aliases, "start_requested"),
            acknowledge=_bool(aliases, "acknowledge"),
            reset_requested=_bool(aliases, "reset_requested"),
            emergency_stop=_bool(aliases, "emergency_stop"),
            sensor_ok=_bool(aliases, "sensor_ok", True),
            k3_temperature_c=_float(aliases, "k3_temperature_c", 78.0),
            k3_level_l=_float(aliases, "k3_level_l", _float(aliases, "k3_fuellstand", 10.0)),
            k3_level_min=_bool(aliases, "k3_level_min", _bool(aliases, "k3_minimaler_fuellstand")),
            k3_level_max=_bool(aliases, "k3_level_max", _bool(aliases, "k3_maximaler_fuellstand")),
            k1_temperature_c=_float(aliases, "k1_temperature_c", 65.0),
            k1_level_l=_float(aliases, "k1_level_l", _float(aliases, "k1_fuellstand", 0.0)),
            k1_level_full=_bool(aliases, "k1_level_full", _bool(aliases, "k1_fuellstand_voll")),
            k2_temperature_c=_float(aliases, "k2_temperature_c", 20.0),
            k2_level_l=_float(aliases, "k2_level_l", _float(aliases, "k2_fuellstand", 0.0)),
            k2_level_full=_bool(aliases, "k2_level_full", _bool(aliases, "k2_fuellstand_voll")),
            k4_temperature_c=_float(aliases, "k4_temperature_c", 20.0),
            k4_level_l=_float(aliases, "k4_level_l", 0.0),
            flow_k3_to_k1_l_min=_float(aliases, "flow_k3_to_k1_l_min"),
            flow_k1_to_k2_l_min=_float(aliases, "flow_k1_to_k2_l_min"),
            flow_k2_to_k4_l_min=_float(aliases, "flow_k2_to_k4_l_min"),
            v3_open=_bool(aliases, "v3_open"),
            v4_open=_bool(aliases, "v4_open"),
            v5_open=_bool(aliases, "v5_open"),
            nv1_closed=_bool(aliases, "nv1_closed", True),
            nv2_closed=_bool(aliases, "nv2_closed", True),
            nv3_closed=_bool(aliases, "nv3_closed", True),
            heater_k1_on_feedback=_bool(aliases, "heater_k1_on_feedback"),
            heater_k2_on_feedback=_bool(aliases, "heater_k2_on_feedback"),
            agitator_on_feedback=_bool(aliases, "agitator_on_feedback"),
            pump_on_feedback=_bool(aliases, "pump_on_feedback"),
            missing_value_age_s=_float(aliases, "missing_value_age_s"),
        )

    def with_updates(self, **changes: Any) -> "ProcessSnapshot":
        return replace(self, **changes)
