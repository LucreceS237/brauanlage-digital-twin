from __future__ import annotations

from dataclasses import dataclass

from .fault_catalog import FaultCode
from .fsm import BrewStateMachine
from .process_snapshot import ProcessSnapshot
from .recipe import BrewRecipe
from .states import BrewState


@dataclass(frozen=True)
class ScenarioStep:
    test_id: str
    description: str
    snapshot: ProcessSnapshot
    dt_s: float
    expected_state: BrewState
    expected_display_state: str


@dataclass(frozen=True)
class ScenarioResult:
    test_id: str
    passed: bool
    expected_display_state: str
    actual_display_state: str
    reason_code: str


def build_fast_recipe() -> BrewRecipe:
    return BrewRecipe(nachguss_min_duration_s=2, mashing_duration_s=2, lautering_duration_s=2, boiling_duration_s=2, transfer_to_k4_duration_s=2, fermentation_duration_s=2)


def build_acceptance_steps() -> list[ScenarioStep]:
    base = ProcessSnapshot()
    return [
        ScenarioStep("T01", "Starttaste setzt IDLE -> PRECHECK", base.with_updates(start_requested=True), 1, BrewState.PRECHECK, "PRECHECK"),
        ScenarioStep("T02", "Precheck erfüllt -> NACHGUSS", base.with_updates(start_requested=True), 1, BrewState.NACHGUSS, "NACHGUSS"),
        ScenarioStep("T03", "Nachguss ausreichend -> MASHING", base.with_updates(v3_open=True, flow_k3_to_k1_l_min=1.0, k1_level_l=4.0), 3, BrewState.MASHING, "MASHING"),
        ScenarioStep("T04", "Maischen abgeschlossen -> LAUTERING", base.with_updates(k1_level_l=4.0, k1_temperature_c=66.0, v4_open=True, flow_k1_to_k2_l_min=1.0), 3, BrewState.LAUTERING, "LAUTERING"),
        ScenarioStep("T05", "Läutern abgeschlossen -> BOILING", base.with_updates(v4_open=True, flow_k1_to_k2_l_min=1.0, k2_level_l=4.0), 3, BrewState.BOILING, "BOILING"),
        ScenarioStep("T06", "Kochen abgeschlossen -> COOLING", base.with_updates(k2_level_l=4.0, k2_temperature_c=100.0), 3, BrewState.COOLING, "COOLING"),
        ScenarioStep("T07", "Kühlziel mit V5/Pumpe -> TRANSFER_TO_K4", base.with_updates(k2_temperature_c=24.0, v5_open=True, pump_on_feedback=True), 1, BrewState.TRANSFER_TO_K4, "TRANSFER_TO_K4"),
        ScenarioStep("T08", "Austrag vollständig -> FERMENTING", base.with_updates(v5_open=True, pump_on_feedback=True, flow_k2_to_k4_l_min=1.0, k4_level_l=3.0), 3, BrewState.FERMENTING, "FERMENTING"),
        ScenarioStep("T09", "Gärdauer erfüllt -> FINISHED", base.with_updates(k4_level_l=3.0, k4_temperature_c=18.0), 3, BrewState.FINISHED, "FINISHED"),
    ]


def run_acceptance_suite() -> list[ScenarioResult]:
    fsm = BrewStateMachine(recipe=build_fast_recipe())
    results: list[ScenarioResult] = []
    print("AP4 Terminal-Abnahme Version 4")
    print("=" * 80)
    for step in build_acceptance_steps():
        result = fsm.update(step.snapshot, dt_s=step.dt_s)
        passed = result.state == step.expected_state and result.display_state == step.expected_display_state
        results.append(ScenarioResult(step.test_id, passed, step.expected_display_state, result.display_state, result.reason_code))
        print(f"\n{step.test_id} - {step.description}")
        for line in result.terminal_lines():
            print(line)
        print("Status:", "BESTANDEN" if passed else "NICHT BESTANDEN")
    run_fault_catalog_suite()
    return results


def run_fault_catalog_suite() -> None:
    print("\nAP4 Fehlercode-Abnahme Version 4")
    print("=" * 80)
    tests = [
        ("F01", BrewState.NACHGUSS, ProcessSnapshot(v3_open=True, flow_k3_to_k1_l_min=1.0, k3_temperature_c=50.0), FaultCode.ERROR_001_K3_NACHGUSS_TEMP_LOW.value),
        ("F02", BrewState.NACHGUSS, ProcessSnapshot(v3_open=False, flow_k3_to_k1_l_min=1.0), FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS.value),
        ("F03", BrewState.MASHING, ProcessSnapshot(k1_temperature_c=40.0, k1_level_l=4.0), FaultCode.ERROR_005_K1_MASHING_TEMP_LOW.value),
        ("F04", BrewState.BOILING, ProcessSnapshot(k2_temperature_c=110.0, k2_level_l=4.0), FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH.value),
        ("F05", BrewState.TRANSFER_TO_K4, ProcessSnapshot(v5_open=True, pump_on_feedback=False, flow_k2_to_k4_l_min=1.0), FaultCode.ERROR_015_PUMP_OFF_TRANSFER_K4.value),
        ("F06", BrewState.FERMENTING, ProcessSnapshot(k4_temperature_c=30.0, k4_level_l=4.0), FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH.value),
        ("F07", BrewState.BOILING, ProcessSnapshot(emergency_stop=True), FaultCode.EMERGENCY_001_ESTOP_ACTIVE.value),
        ("F08", BrewState.MASHING, ProcessSnapshot(k1_temperature_c=130.0, k1_level_l=4.0), FaultCode.EMERGENCY_006_K1_TEMP_TOO_HIGH.value),
    ]
    passed = 0
    for test_id, initial_state, snapshot, expected_display in tests:
        fsm = BrewStateMachine(recipe=build_fast_recipe())
        fsm.state = initial_state
        result = fsm.update(snapshot, dt_s=1)
        ok = result.display_state == expected_display
        passed += int(ok)
        print(f"\n{test_id} erwartet: {expected_display}")
        for line in result.terminal_lines():
            print(line)
        context = fsm.get_context_for_anomaly()
        print(f"AP5/AP6 active_fault_code={context.active_fault_code}, display_state={context.display_state}")
        print("Status:", "BESTANDEN" if ok else "NICHT BESTANDEN")
    print(f"\nFehlercode-Abnahme: {passed}/{len(tests)} bestanden")


if __name__ == "__main__":
    run_acceptance_suite()
