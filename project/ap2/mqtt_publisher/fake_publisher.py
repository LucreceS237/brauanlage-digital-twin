"""
File: fake_publisher.py
Work Package: AP2
Responsible Engineer: Engineer A
Purpose: FAKE publisher source using the shared FSM-driven ProcessSimulator.
"""
from __future__ import annotations

import os

from project.shared.simulation import ProcessSimulator


class FakePublisher:
    """Generates FAKE SPS payloads once per tick."""

    def __init__(
        self,
        scenario: str | None = None,
        total_duration_seconds: float | None = None,
        speed_factor: float | None = None,
    ) -> None:
        self._sim = ProcessSimulator(
            scenario=scenario or os.getenv("SIMULATION_SCENARIO", "NORMAL_PROCESS"),
            total_duration_seconds=float(
                total_duration_seconds
                if total_duration_seconds is not None
                else os.getenv("SIMULATION_TOTAL_DURATION_SECONDS", "1800")
            ),
            tick_seconds=float(os.getenv("SIMULATION_TICK_SECONDS", "1")),
            speed_factor=float(
                speed_factor if speed_factor is not None else os.getenv("SIMULATION_SPEED_FACTOR", "1")
            ),
        )

    def next_payload(self) -> dict:
        return self._sim.next_payload(
            source="Fake_SPS",
            publisher_mode="FAKE",
            connection_status="CONNECTED",
            sps_endpoint="",
        )

    def advance(self, dt_s: float) -> None:
        self._sim.advance(dt_s)
