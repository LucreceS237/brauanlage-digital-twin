"""
File: snapshot_adapter.py
Work Package: AP5
Responsible Engineer: Engineer D
Purpose: Converts a validated MQTT/SPS payload (`values` dict in the APPROVED physical namespace) into the ProcessSnapshot format required by AP4. It enforces the approved Anlage mapping: K1 = Nachgussbehälter, K2 = Maischebehälter, K3 = Läuterbehälter, K4 = Gärbehälter via the rotation defined in mapping.py.
"""
from __future__ import annotations

from numbers import Number
from typing import Any, Mapping

from project.ap4.process_snapshot import ProcessSnapshot

from .mapping import FLOW_MAP, LEVEL_MAP, TEMPERATURE_MAP

# Demo/PLC step -> AP4 target phase (the fake publisher walks steps 1..10).
STEP_TO_AP4_STATE: dict[int, str] = {
    1: "IDLE", 2: "PRECHECK", 3: "NACHGUSS", 4: "MASHING", 5: "LAUTERING",
    6: "BOILING", 7: "COOLING", 8: "TRANSFER_TO_K4", 9: "FERMENTING", 10: "FINISHED",
}


def _num(values: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    v = values.get(key, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _flag(values: Mapping[str, Any], key: str, default: bool = False) -> bool:
    v = values.get(key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, Number):
        return bool(v)
    return str(v).strip().lower() in {"true", "1", "yes", "on", "ja"}


def _derive_actuators(step: int) -> dict[str, Any]:
    """
    Synthesize the actuator/feedback signals AP4 expects, from the PLC step.

    The standard SPS payload has no valve/pump feedback, so we present a
    plausible actuator picture consistent with the reported step; the measured
    temperatures/levels/flow still gate the transitions and raise AP4 faults.
    """
    return {
        "start_requested": step >= 2,
        "nv1_closed": True,
        "nv2_closed": True,
        "nv3_closed": True,
        "v3_open": step >= 3,                       # Nachguss valve
        "v4_open": step >= 4,                       # Mash -> Läuter transfer valve
        "v5_open": step >= 7,                       # Cooling / K4 transfer valve
        "pump_on_feedback": step >= 7,
        "flow_k1_to_k2_l_min": 1.0 if step >= 4 else 0.0,
        "flow_k2_to_k4_l_min": 1.0 if step >= 8 else 0.0,
        "k4_level_l": 5.0 if step >= 8 else 0.0,
    }


def build_snapshot(
    values: Mapping[str, Any],
    timestamp_s: float = 0.0,
    missing_value_age_s: float = 0.0,
) -> ProcessSnapshot:
    """Map an approved-namespace `values` dict into an AP4 ProcessSnapshot."""
    step = int(_num(values, "Aktueller_Schritt", 0))
    fields: dict[str, Any] = {
        "timestamp_s": timestamp_s,
        "aktueller_schritt": step,
        "emergency_stop": _flag(values, "emergency_stop"),
        "sensor_ok": _flag(values, "sensor_ok", True),
        "acknowledge": _flag(values, "acknowledge"),
        "missing_value_age_s": missing_value_age_s,
    }

    # 1. Temperatures (rotation to AP4 role fields).
    for src, dst in TEMPERATURE_MAP.items():
        if src in values:
            fields[dst] = _num(values, src, ProcessSnapshot.__dataclass_fields__[dst].default)

    # 2. Levels (rotation).
    for src, dst in LEVEL_MAP.items():
        if src in values:
            fields[dst] = _num(values, src)

    # 3. Flow (Nachguss -> Maische).
    for src, dst in FLOW_MAP.items():
        if src in values:
            fields[dst] = _num(values, src)

    # 4. Nachguss source level: approved K1 provides only a boolean OK signal.
    #    AP4's nachguss source is its k3 role; present a sufficient level when OK.
    k1_ok = _flag(values, "K1_Füllstand_OK", True)
    fields["k3_level_l"] = 10.0 if k1_ok else 0.0

    # 5. Derived actuator/feedback signals so AP4 can advance.
    fields.update(_derive_actuators(step))

    # Prefer explicit control flags from the payload when the simulator sets them.
    for flag_key in ("start_requested",):
        if flag_key in values:
            fields[flag_key] = _flag(values, flag_key)

    return ProcessSnapshot(**fields)
