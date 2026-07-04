"""
File: process_simulator.py
Work Package: shared
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: Time-driven brewing process simulator for demo, fake SPS, and backend simulation mode.
"""
from __future__ import annotations

import math
from typing import Any

from .payload_builder import build_sps_payload
from .scenarios import Scenario, get_scenario

ROOM_TEMP_C = 20.0
DEFAULT_TOTAL_DURATION_S = 1800.0
DEFAULT_TICK_S = 1.0

# Compressed demo phase boundaries (simulation seconds, before speed factor).
T_PREHEAT_END = 300.0
T_PRECHECK_END = 305.0
T_NACHGUSS_END = 310.0
T_MASHING_END = 660.0
T_LAUTERING_END = 840.0
T_BOILING_END = 1110.0
T_COOLING_END = 1200.0
T_TRANSFER_END = 1230.0
T_FERMENTING_END = 1800.0

PHASE_ORDER = (
    "PRE_HEATING",
    "PRECHECK",
    "NACHGUSS",
    "MASHING",
    "LAUTERING",
    "BOILING",
    "COOLING",
    "TRANSFER_TO_K4",
    "FERMENTING",
    "FINISHED",
)

STEP_BY_PHASE = {
    "PRE_HEATING": 1,
    "PRECHECK": 2,
    "NACHGUSS": 3,
    "MASHING": 4,
    "LAUTERING": 5,
    "BOILING": 6,
    "COOLING": 7,
    "TRANSFER_TO_K4": 8,
    "FERMENTING": 9,
    "FINISHED": 10,
}


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _lerp(t: float, t0: float, t1: float, v0: float, v1: float) -> float:
    if t <= t0:
        return v0
    if t >= t1:
        return v1
    frac = (t - t0) / max(t1 - t0, 1e-9)
    return v0 + (v1 - v0) * frac


def _smoothstep(t: float, t0: float, t1: float, v0: float, v1: float) -> float:
    if t <= t0:
        return v0
    if t >= t1:
        return v1
    x = (t - t0) / max(t1 - t0, 1e-9)
    x = x * x * (3.0 - 2.0 * x)
    return v0 + (v1 - v0) * x


def _phase_at(t: float) -> str:
    if t < T_PREHEAT_END:
        return "PRE_HEATING"
    if t < T_PRECHECK_END:
        return "PRECHECK"
    if t < T_NACHGUSS_END:
        return "NACHGUSS"
    if t < T_MASHING_END:
        return "MASHING"
    if t < T_LAUTERING_END:
        return "LAUTERING"
    if t < T_BOILING_END:
        return "BOILING"
    if t < T_COOLING_END:
        return "COOLING"
    if t < T_TRANSFER_END:
        return "TRANSFER_TO_K4"
    if t < T_FERMENTING_END:
        return "FERMENTING"
    return "FINISHED"


def _tiny_noise(scale: float, tick: int) -> float:
    """Deterministic micro-ripple so charts look alive without random jumps."""
    return scale * math.sin(tick * 0.17)


class ProcessSimulator:
    """
    Time-driven brewing process simulator producing MQTT-compatible payloads.

    Values evolve smoothly over the compressed ~30 minute demo timeline.
    """

    def __init__(
        self,
        scenario: str = "NORMAL_PROCESS",
        total_duration_seconds: float = DEFAULT_TOTAL_DURATION_S,
        tick_seconds: float = DEFAULT_TICK_S,
        speed_factor: float = 1.0,
    ) -> None:
        self.scenario: Scenario = get_scenario(scenario)
        self.total_duration_seconds = total_duration_seconds
        self.tick_seconds = tick_seconds
        self.speed_factor = max(speed_factor, 0.01)
        self._fault: str | None = self.scenario.fault
        self._elapsed = 0.0
        self._tick_count = 0
        self._finished = False

    @property
    def scenario_name(self) -> str:
        return self.scenario.name

    @property
    def current_phase(self) -> str:
        return _phase_at(self._elapsed)

    @property
    def elapsed_simulation_seconds(self) -> float:
        return self._elapsed

    def is_finished(self) -> bool:
        return self._finished

    def reset(self) -> None:
        self._elapsed = 0.0
        self._tick_count = 0
        self._finished = False
        self._fault = self.scenario.fault

    def acknowledge(self) -> None:
        """Clear injected fault after operator acknowledge (demo recovery)."""
        self._fault = None

    def advance(self, dt_s: float) -> None:
        if self._finished:
            return
        self._elapsed += dt_s * self.speed_factor
        self._tick_count += 1
        if self._elapsed >= self.total_duration_seconds:
            self._elapsed = self.total_duration_seconds
            self._finished = True

    def next_values(self, fsm_state: str | None = None, time_in_state: float | None = None) -> dict[str, Any]:
        """Produce one values dict; advances time by tick_seconds (backend path)."""
        del fsm_state, time_in_state
        self.advance(self.tick_seconds)
        return self._build_values()

    def next_payload(
        self,
        *,
        source: str = "Fake_SPS",
        publisher_mode: str = "FAKE",
        connection_status: str = "CONNECTED",
        sps_endpoint: str = "",
    ) -> dict[str, Any]:
        """Produce a full MQTT payload; does not advance time (call advance() separately)."""
        values = self._build_values()
        return build_sps_payload(
            values,
            source=source,
            publisher_mode=publisher_mode,
            connection_status=connection_status,
            simulation_phase=self.current_phase,
            sps_endpoint=sps_endpoint,
        )

    def _build_values(self) -> dict[str, Any]:
        t = self._elapsed
        phase = _phase_at(t)
        tick = self._tick_count
        step = STEP_BY_PHASE[phase]

        k1 = _smoothstep(t, 0.0, T_PREHEAT_END, ROOM_TEMP_C, 75.0) + _tiny_noise(0.15, tick)
        k2 = ROOM_TEMP_C + _tiny_noise(0.1, tick)
        k3 = ROOM_TEMP_C + _tiny_noise(0.1, tick)
        k4 = ROOM_TEMP_C + _tiny_noise(0.08, tick)
        flow = 0.0
        k2_level = 0.0
        k3_level = 8.0

        start_requested = t >= T_PREHEAT_END - 10.0
        mash_finished = t >= T_MASHING_END
        lautering_finished = t >= T_LAUTERING_END
        boiling_finished = t >= T_BOILING_END
        cooled_down = t >= T_COOLING_END
        fermentation_finished = t >= T_FERMENTING_END

        if phase == "PRECHECK":
            k1 = 72.0 + _tiny_noise(0.1, tick)
            start_requested = True
            k2_level = 4.0

        elif phase == "NACHGUSS":
            k1 = 74.0 + _tiny_noise(0.1, tick)
            flow = 0.7 + _tiny_noise(0.02, tick)
            k2_level = 6.0

        elif phase == "MASHING":
            k1 = 74.0 + _tiny_noise(0.1, tick)
            k2 = _smoothstep(t, T_NACHGUSS_END, T_MASHING_END, ROOM_TEMP_C + 5.0, 65.0) + _tiny_noise(0.2, tick)
            k2_level = 20.0 + _tiny_noise(0.05, tick)
            k3 = _lerp(t, T_NACHGUSS_END, T_MASHING_END, ROOM_TEMP_C, 35.0) + _tiny_noise(0.1, tick)
            flow = 0.1 + abs(_tiny_noise(0.02, tick))

        elif phase == "LAUTERING":
            k1 = 70.0 + _tiny_noise(0.1, tick)
            k2 = 64.0 + _tiny_noise(0.15, tick)
            k2_level = _lerp(t, T_MASHING_END, T_LAUTERING_END, 20.0, 12.0)
            k3 = 40.0 + _tiny_noise(0.1, tick)
            k3_level = _smoothstep(t, T_MASHING_END, T_LAUTERING_END, 10.0, 22.0)
            flow = 0.75 + _tiny_noise(0.03, tick)

        elif phase == "BOILING":
            k1 = 68.0 + _tiny_noise(0.1, tick)
            k2 = 63.0 + _tiny_noise(0.1, tick)
            k3 = _smoothstep(t, T_LAUTERING_END, T_BOILING_END, 45.0, 100.0) + _tiny_noise(0.15, tick)
            k3_level = 18.0 + _tiny_noise(0.05, tick)
            flow = 0.15 + abs(_tiny_noise(0.02, tick))

        elif phase == "COOLING":
            k1 = 55.0 + _tiny_noise(0.1, tick)
            k2 = 50.0 + _tiny_noise(0.1, tick)
            k3 = _smoothstep(t, T_BOILING_END, T_COOLING_END, 100.0, 22.0) + _tiny_noise(0.1, tick)
            k3_level = 16.0
            flow = 0.0

        elif phase == "TRANSFER_TO_K4":
            k3 = 24.0 + _tiny_noise(0.1, tick)
            k4 = _smoothstep(t, T_COOLING_END, T_TRANSFER_END, 22.0, 18.0) + _tiny_noise(0.08, tick)
            k3_level = 14.0
            flow = 0.6 + _tiny_noise(0.02, tick)

        elif phase == "FERMENTING":
            k1 = 45.0 + _tiny_noise(0.08, tick)
            k2 = 35.0 + _tiny_noise(0.08, tick)
            k3 = 22.0 + _tiny_noise(0.08, tick)
            k4 = 18.0 + _tiny_noise(0.12, tick)
            k3_level = 12.0
            flow = 0.0

        elif phase == "FINISHED":
            k1 = 40.0
            k2 = 30.0
            k3 = 20.0
            k4 = 18.0
            k2_level = 10.0
            k3_level = 10.0
            flow = 0.0
            start_requested = False

        values: dict[str, Any] = {
            "Aktueller_Schritt": step,
            "K1_Temperatur": round(_clamp(k1, 0.0, 130.0), 2),
            "K1_Füllstand_OK": True,
            "K2_Temperatur": round(_clamp(k2, 0.0, 130.0), 2),
            "K2_Füllstand": round(max(k2_level, 0.0), 2),
            "K3_Temperatur": round(_clamp(k3, 0.0, 130.0), 2),
            "K3_Füllstand": round(max(k3_level, 0.0), 2),
            "K3_MinimalerFüllstand": 5.0,
            "K3_MaximalerFüllstand": 30.0,
            "MobilerSensor_Temperatur": round(_clamp(k4, 0.0, 130.0), 2),
            "Durchfluss_NachgussMaische": round(max(flow, 0.0), 3),
            "emergency_stop": False,
            "sensor_ok": True,
            "acknowledge": False,
            "start_requested": start_requested,
            "mash_finished": mash_finished,
            "lautering_finished": lautering_finished,
            "boiling_finished": boiling_finished,
            "cooled_down": cooled_down,
            "fermentation_finished": fermentation_finished,
        }

        meta = self._inject_fault(values, phase)
        values.update(meta)
        return values

    def _inject_fault(self, values: dict[str, Any], phase: str) -> dict[str, Any]:
        fault = self._fault
        meta: dict[str, Any] = {}
        if fault is None:
            return meta

        if fault == "temp_high" and phase == "BOILING":
            values["K3_Temperatur"] = 118.0

        elif fault == "low_flow" and phase == "LAUTERING":
            values["Durchfluss_NachgussMaische"] = 0.15

        elif fault == "sensor_fail" and phase in ("MASHING", "LAUTERING"):
            values["sensor_ok"] = False
            values["K2_Temperatur"] = -999.0

        elif fault == "stale" and phase in ("MASHING", "LAUTERING", "BOILING"):
            meta["_stale"] = True
            meta["_collectorStatus"] = "STALE"

        elif fault == "cooling_fail" and phase == "COOLING":
            values["K3_Temperatur"] = 72.0
            values["cooled_down"] = False

        elif fault == "ferment_temp" and phase == "FERMENTING":
            values["MobilerSensor_Temperatur"] = 27.0

        elif fault == "emergency" and phase not in ("PRE_HEATING", "FINISHED"):
            if self._elapsed >= T_MASHING_END:
                values["emergency_stop"] = True

        elif fault == "absolute_limit" and phase == "BOILING":
            values["K3_Temperatur"] = 130.0

        return meta
