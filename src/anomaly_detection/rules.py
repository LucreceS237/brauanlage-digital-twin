"""
===========================================================
ANOMALY DETECTION RULES
===========================================================

This module contains all anomaly detection logic for the
Digital Twin of the Brewing System.

Concept
-------
The anomaly detector evaluates SPS process snapshots in
real time.

Each rule can use:

1. Current snapshot
2. Historical measurements
3. FSM process state

Rule Categories
---------------
R001 Data Quality
R002 Sensor Plausibility
R003 Temperature Limits
R004 Temperature Trends
R005 Flow Anomalies
R006 State-Based Process Anomalies

Design Principles
-----------------
- No alarm on a single noisy measurement.
- Use persistence windows whenever possible.
- Use FSM state as context.
- Separate data quality alarms from process alarms.

"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from math import isnan
from typing import Any, Dict, List, Optional
from .alarm import Alarm, Severity, create_alarm, utc_now

def is_invalid_number(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, (int, float)):
        return True
    if isinstance(value, float) and isnan(value):
        return True
    return False

def check_data_stale(
    snapshot: Dict[str, Any],
    max_age_seconds: float = 3.0,
) -> List[Alarm]:
    alarms: List[Alarm] = []
    state = snapshot.get("state", "UNKNOWN")

    received_at = snapshot.get("_received_at")

    if received_at is None:
        return [
            create_alarm(
                rule_id="R001",
                code="SNAPSHOT_TIMESTAMP_MISSING",
                severity=Severity.HIGH,
                state=state,
                component="SYSTEM",
                variable="_received_at",
                value=None,
                threshold="required timestamp",
                message="The snapshot has no reception timestamp.",
            )
        ]

    if isinstance(received_at, str):
        received_at = datetime.fromisoformat(received_at)

    meta = snapshot.get("_meta", {})

    # If no metadata is available, we do not create alarms in v0.1.
    # Later, this can be changed once Engineer B guarantees timestamps
    # for every data point.
    if not meta:
        return []

    for variable, info in meta.items():
        timestamp = info.get("timestamp")

        if timestamp is None:
            alarms.append(
                create_alarm(
                    rule_id="R001",
                    code="DATA_TIMESTAMP_MISSING",
                    severity=Severity.HIGH,
                    state=state,
                    component="SYSTEM",
                    variable=variable,
                    value=None,
                    threshold="timestamp required",
                    message=f"Timestamp missing for {variable}.",
                )
            )
            continue

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        age = (received_at - timestamp).total_seconds()

        if age > max_age_seconds:
            alarms.append(
                create_alarm(
                    rule_id="R001",
                    code="DATA_STALE",
                    severity=Severity.HIGH,
                    state=state,
                    component="SYSTEM",
                    variable=variable,
                    value=round(age, 3),
                    threshold=max_age_seconds,
                    message=f"{variable} is stale: {age:.1f}s old.",
                )
            )

    return alarms

def check_sensor_value_invalid(snapshot: Dict[str, Any]) -> List[Alarm]:
    """
    Rule R002: SENSOR_VALUE_INVALID

    This rule checks whether temperature values are physically plausible.

    It uses the validated OPC-UA process variable names from Engineer A.
    """

    alarms: List[Alarm] = []
    state = snapshot.get("state", "UNKNOWN")

    temperature_limits = {
        "K1_Temperatur": ("K1", 0.0, 110.0),
        "K2_Temperatur": ("K2", 0.0, 110.0),
        "K3_Temperatur": ("K3", 0.0, 110.0),
        "MobilerSensor_Temperatur": ("K4", 0.0, 60.0),
    }

    for variable, (component, min_value, max_value) in temperature_limits.items():
        value = snapshot.get(variable)

        if is_invalid_number(value) or value < min_value or value > max_value:
            alarms.append(
                create_alarm(
                    rule_id="R002",
                    code="SENSOR_VALUE_INVALID",
                    severity=Severity.HIGH,
                    state=state,
                    component=component,
                    variable=variable,
                    value=value,
                    threshold=f"{min_value} <= value <= {max_value}",
                    message=f"{variable} is invalid or physically implausible.",
                )
            )

    return alarms

def check_temperature_limits(snapshot: Dict[str, Any]) -> List[Alarm]:
    alarms: List[Alarm] = []
    state = snapshot.get("state", "UNKNOWN")
    
    rules = [
        ("K1", "K1_Temperatur", "K1_Temperatur_SollwertUntereGrenze", "K1_Temperatur_SollwertObereGrenze"),
        ("K2", "K2_Temperatur", "K2_Temperatur_SollwertUntereGrenze", "K2_Temperatur_SollwertObereGrenze"),
        ("K3", "K3_Temperatur", "K3_Temperatur_SollwertUntereGrenze", "K3_Temperatur_SollwertObereGrenze"),
    ]

    for component, temp_key, lower_key, upper_key in rules:
        value = snapshot.get(temp_key)
        lower = snapshot.get(lower_key)
        upper = snapshot.get(upper_key)

        if is_invalid_number(value):
            continue

        if lower is not None and value < lower:
            alarms.append(
                Alarm(
                    timestamp=utc_now(),
                    rule_id="R003",
                    code="TEMP_TOO_LOW",
                    severity=Severity.MEDIUM,
                    state=state,
                    component=component,
                    variable=temp_key,
                    value=value,
                    threshold=lower,
                    message=f"{temp_key} is below lower allowed limit.",
                )
            )

        if upper is not None and value > upper:
            alarms.append(
                Alarm(
                    timestamp=utc_now(),
                    rule_id="R003",
                    code="TEMP_TOO_HIGH",
                    severity=Severity.HIGH,
                    state=state,
                    component=component,
                    variable=temp_key,
                    value=value,
                    threshold=upper,
                    message=f"{temp_key} exceeds upper allowed limit.",
                )
            )
    return alarms

def check_temperature_rise_too_fast(
    history: List[Dict[str, Any]],
    variable: str,
    component: str,
    state: str,
    max_rise_c_per_min: float = 5.0,
    window_seconds: int = 60,
) -> List[Alarm]:
    if len(history) < 2:
        return []

    latest = history[-1]
    latest_time = latest.get("_received_at")
    latest_value = latest.get(variable)

    if isinstance(latest_time, str):
        latest_time = datetime.fromisoformat(latest_time)

    if is_invalid_number(latest_value):
        return []

    reference = None

    for item in reversed(history):
        t = item.get("_received_at")
        if isinstance(t, str):
            t = datetime.fromisoformat(t)

        if (latest_time - t).total_seconds() >= window_seconds:
            reference = item
            break

    if reference is None:
        return []

    old_value = reference.get(variable)
    old_time = reference.get("_received_at")

    if isinstance(old_time, str):
        old_time = datetime.fromisoformat(old_time)

    if is_invalid_number(old_value):
        return []

    delta_t_seconds = (latest_time - old_time).total_seconds()
    if delta_t_seconds <= 0:
        return []

    rate_c_per_min = (latest_value - old_value) / delta_t_seconds * 60.0

    if rate_c_per_min > max_rise_c_per_min:
        return [
            Alarm(
                timestamp=utc_now(),
                rule_id="R004",
                code="TEMP_RISE_TOO_FAST",
                severity=Severity.HIGH,
                state=state,
                component=component,
                variable=variable,
                value=round(rate_c_per_min, 3),
                threshold=max_rise_c_per_min,
                message=f"{variable} rises too fast over {window_seconds}s window.",
            )
        ]

    return []

def check_low_flow_during_lautering(
    snapshot: Dict[str, Any],
    min_flow_l_min: float = 0.5,
) -> List[Alarm]:
    state = snapshot.get("state", "UNKNOWN")
    flow = snapshot.get("Durchfluss_NachgussMaische")

    if state != "LAUTERING":
        return []

    if is_invalid_number(flow):
        return []

    if flow < min_flow_l_min:
        return [
            Alarm(
                timestamp=utc_now(),
                rule_id="R005",
                code="LOW_FLOW_DURING_LAUTERING",
                severity=Severity.HIGH,
                state=state,
                component="FLOW_PATH",
                variable="Durchfluss_NachgussMaische",
                value=flow,
                threshold=min_flow_l_min,
                message="Flow is too low during lautering.",
            )
        ]

    return []

def check_unexpected_flow_in_idle(
    snapshot: Dict[str, Any],
    flow_threshold_l_min: float = 0.5,
) -> List[Alarm]:
    state = snapshot.get("state", "UNKNOWN")
    flow = snapshot.get("Durchfluss_NachgussMaische")

    if state not in ["IDLE", "FINISHED"]:
        return []

    if is_invalid_number(flow):
        return []

    if flow > flow_threshold_l_min:
        return [
            Alarm(
                timestamp=utc_now(),
                rule_id="R006",
                code="UNEXPECTED_FLOW_IN_IDLE",
                severity=Severity.MEDIUM,
                state=state,
                component="FLOW_PATH",
                variable="Durchfluss_NachgussMaische",
                value=flow,
                threshold=flow_threshold_l_min,
                message="Flow detected although the process should be inactive.",
            )
        ]

    return []

def evaluate_rules(
    snapshot: Dict[str, Any],
    history: Optional[List[Dict[str, Any]]] = None,
) -> List[Alarm]:
    """
    Main entry point for anomaly rule evaluation.

    snapshot:
        Current digital-twin process snapshot from SPS/OPC-UA collector.

    history:
        Time-ordered list of previous snapshots, including the current snapshot.
        Required for trend-based rules such as temperature rise too fast.
    """
    history = history or [snapshot]
    state = snapshot.get("state", "UNKNOWN")

    alarms: List[Alarm] = []

    alarms.extend(check_data_stale(snapshot))
    alarms.extend(check_sensor_value_invalid(snapshot))
    alarms.extend(check_temperature_limits(snapshot))

    for component, variable in [
        ("K1", "K1_Temperatur"),
        ("K2", "K2_Temperatur"),
        ("K3", "K3_Temperatur"),
    ]:
        alarms.extend(
            check_temperature_rise_too_fast(
                history=history,
                variable=variable,
                component=component,
                state=state,
            )
        )

    alarms.extend(check_low_flow_during_lautering(snapshot))
    alarms.extend(check_unexpected_flow_in_idle(snapshot))

    return alarms