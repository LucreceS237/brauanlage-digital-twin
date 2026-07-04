"""
File: test_process_simulator.py
Work Package: tests
Responsible Engineer: Engineer D
Purpose: Tests for the shared FSM-driven ProcessSimulator.
"""
from __future__ import annotations

from project.shared.simulation import ProcessSimulator
from project.shared.simulation.process_simulator import PHASE_ORDER, T_PREHEAT_END
from project.ap3.mqtt.payload_validator import validate_payload


def _advance_to_phase(sim: ProcessSimulator, target: str, max_steps: int = 2500) -> None:
    for _ in range(max_steps):
        if sim.current_phase == target:
            return
        sim.advance(1.0)
        if sim.is_finished():
            break
    assert sim.current_phase == target, f"expected phase {target}, got {sim.current_phase}"


def test_normal_scenario_visits_phases_in_order():
    sim = ProcessSimulator(scenario="NORMAL_PROCESS", speed_factor=50.0)
    seen: list[str] = []
    for _ in range(200):
        phase = sim.current_phase
        if not seen or seen[-1] != phase:
            seen.append(phase)
        sim.advance(1.0)
        if sim.is_finished():
            if seen[-1] != "FINISHED":
                seen.append("FINISHED")
            break
    for expected in ("PRE_HEATING", "MASHING", "LAUTERING", "BOILING", "COOLING", "FERMENTING", "FINISHED"):
        assert expected in seen, seen


def test_preheating_raises_k1_above_50():
    sim = ProcessSimulator(speed_factor=1.0)
    sim.advance(T_PREHEAT_END - 1)
    values = sim._build_values()  # noqa: SLF001
    assert values["K1_Temperatur"] > 50.0
    assert values["K1_Füllstand_OK"] is True


def test_mashing_raises_k2_toward_65():
    sim = ProcessSimulator(speed_factor=1.0)
    _advance_to_phase(sim, "MASHING")
    sim.advance(330.0)
    values = sim._build_values()  # noqa: SLF001
    assert 60.0 <= values["K2_Temperatur"] <= 68.0


def test_lautering_flow_at_least_half_l_min_normal():
    sim = ProcessSimulator(scenario="NORMAL_PROCESS")
    _advance_to_phase(sim, "LAUTERING")
    values = sim._build_values()  # noqa: SLF001
    assert values["Durchfluss_NachgussMaische"] >= 0.5


def test_boiling_raises_k3_toward_100():
    sim = ProcessSimulator()
    _advance_to_phase(sim, "BOILING")
    sim.advance(200.0)
    values = sim._build_values()  # noqa: SLF001
    assert values["K3_Temperatur"] >= 90.0


def test_cooling_decreases_k3_to_25_or_below():
    sim = ProcessSimulator()
    _advance_to_phase(sim, "COOLING")
    sim.advance(90.0)
    values = sim._build_values()  # noqa: SLF001
    assert values["K3_Temperatur"] <= 25.0
    assert values["cooled_down"] is True


def test_fermentation_mobiler_sensor_in_window():
    sim = ProcessSimulator()
    _advance_to_phase(sim, "FERMENTING")
    sim.advance(120.0)
    values = sim._build_values()  # noqa: SLF001
    assert 16.0 <= values["MobilerSensor_Temperatur"] <= 22.0


def test_normal_scenario_no_fault_flags():
    sim = ProcessSimulator(scenario="NORMAL_PROCESS")
    _advance_to_phase(sim, "MASHING")
    values = sim._build_values()  # noqa: SLF001
    assert values["emergency_stop"] is False
    assert values["sensor_ok"] is True


def test_low_flow_scenario_during_lautering():
    sim = ProcessSimulator(scenario="LOW_FLOW_DURING_LAUTERING")
    _advance_to_phase(sim, "LAUTERING")
    values = sim._build_values()  # noqa: SLF001
    assert values["Durchfluss_NachgussMaische"] < 0.5


def test_emergency_stop_scenario():
    sim = ProcessSimulator(scenario="EMERGENCY_STOP")
    _advance_to_phase(sim, "MASHING")
    sim.advance(400.0)
    values = sim._build_values()  # noqa: SLF001
    assert values["emergency_stop"] is True


def test_fake_payload_source_and_mode():
    sim = ProcessSimulator()
    payload = sim.next_payload(source="Fake_SPS", publisher_mode="FAKE")
    assert payload["source"] == "Fake_SPS"
    assert payload["publisherMode"] == "FAKE"
    assert payload["simulationPhase"] in PHASE_ORDER


def test_simulation_payload_source_and_mode():
    sim = ProcessSimulator()
    sim.advance(1.0)
    values = sim.next_values()
    from project.shared.simulation.payload_builder import build_sps_payload

    payload = build_sps_payload(
        {k: v for k, v in values.items() if not str(k).startswith("_")},
        source="SIMULATION",
        publisher_mode="SIMULATION",
        connection_status="SIMULATION",
        simulation_phase=sim.current_phase,
    )
    assert payload["source"] == "SIMULATION"
    assert payload["publisherMode"] == "SIMULATION"


def test_fake_payload_passes_validator():
    sim = ProcessSimulator()
    for _ in range(20):
        payload = sim.next_payload(source="Fake_SPS", publisher_mode="FAKE")
        ok, reason = validate_payload(payload)
        assert ok, reason
        sim.advance(1.0)


def test_real_mode_does_not_use_simulator_values():
    """REAL path uses RealSpsReader, not ProcessSimulator — sanity import check."""
    from project.ap2.mqtt_publisher.real_sps_reader import RealSpsReader

    reader = RealSpsReader("opc.tcp://127.0.0.1:4840")
    assert not hasattr(reader, "next_payload")
