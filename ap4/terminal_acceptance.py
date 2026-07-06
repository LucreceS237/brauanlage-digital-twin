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


def build_fast_recipe() -> BrewRecipe:
    return BrewRecipe(
        nachguss_min_duration_s=2,
        mashing_duration_s=2,
        transfer_to_k3_duration_s=2,
        lautering_duration_s=2,
        boiling_duration_s=2,
        transfer_to_k4_duration_s=2,
        fermentation_duration_s=2,
    )


def build_acceptance_steps() -> list[ScenarioStep]:
    base = ProcessSnapshot(timestamp="2026-07-01T12:00:00", data_quality="GOOD")
    return [
        ScenarioStep("T01", "Start -> PRECHECK", base.with_updates(start_requested=True), 1, BrewState.PRECHECK, "PRECHECK"),
        ScenarioStep("T02", "Precheck K1 OK -> NACHGUSS", base.with_updates(start_requested=True, k1_temperature_c=78, k1_level_l=20), 1, BrewState.NACHGUSS, "NACHGUSS"),
        ScenarioStep("T03", "K1->K2 Nachguss fertig -> MASHING", base.with_updates(v3_open=True, durchfluss_k1_k2_l_min=1.2, k2_level_l=18, k2_temperature_c=65), 3, BrewState.MASHING, "MASHING"),
        ScenarioStep("T04", "Maischen in K2 fertig -> TRANSFER_TO_K3", base.with_updates(k2_level_l=18, k2_temperature_c=65), 3, BrewState.TRANSFER_TO_K3, "TRANSFER_TO_K3"),
        ScenarioStep("T05", "Transfer K2->K3 fertig -> LAUTERING", base.with_updates(v4_open=True, k3_level_l=16), 3, BrewState.LAUTERING, "LAUTERING"),
        ScenarioStep("T06", "Läutern in K3 fertig -> BOILING", base.with_updates(k3_level_l=16, k2_level_l=18, k2_temperature_c=99), 3, BrewState.BOILING, "BOILING"),
        ScenarioStep("T07", "Kochen in K2 fertig -> COOLING", base.with_updates(k2_level_l=18, k2_temperature_c=99), 3, BrewState.COOLING, "COOLING"),
        ScenarioStep("T08", "Kühlziel erreicht -> TRANSFER_TO_K4", base.with_updates(k2_temperature_c=24), 1, BrewState.TRANSFER_TO_K4, "TRANSFER_TO_K4"),
        ScenarioStep("T09", "Transfer K4 fertig -> FERMENTING", base.with_updates(v5_open=True, pump_on=True, k4_level_l=16, k4_temperature_c=18), 3, BrewState.FERMENTING, "FERMENTING"),
        ScenarioStep("T10", "Gärung fertig -> FINISHED", base.with_updates(k4_level_l=16, k4_temperature_c=18), 3, BrewState.FINISHED, "FINISHED"),
    ]


def run_acceptance_suite() -> None:
    fsm = BrewStateMachine(recipe=build_fast_recipe())
    print("AP4 Terminal-Abnahme Version 5")
    print("=" * 80)
    passed = 0
    steps = build_acceptance_steps()
    for step in steps:
        result = fsm.update(step.snapshot, step.dt_s)
        ok = result.state == step.expected_state and result.display_state == step.expected_display_state
        passed += int(ok)
        print(f"\n{step.test_id} - {step.description}")
        for line in result.terminal_lines():
            print(line)
        print("Status:", "BESTANDEN" if ok else "NICHT BESTANDEN")
    print(f"\nNormalpfad: {passed}/{len(steps)} bestanden")
    run_fault_catalog_suite()


def run_fault_catalog_suite() -> None:
    print("\nAP4 Fehlercode-Abnahme Version 5")
    print("=" * 80)
    tests = [
        ("F01", BrewState.NACHGUSS, ProcessSnapshot(k1_temperature_c=50, v3_open=True, durchfluss_k1_k2_l_min=1.2), FaultCode.ERROR_001_K1_NACHGUSS_TEMP_LOW.value),
        ("F02", BrewState.NACHGUSS, ProcessSnapshot(k1_temperature_c=78, v3_open=False, durchfluss_k1_k2_l_min=1.2), FaultCode.ERROR_003_V3_CLOSED_IN_NACHGUSS.value),
        ("F03", BrewState.NACHGUSS, ProcessSnapshot(k1_temperature_c=78, v3_open=True, durchfluss_k1_k2_l_min=0.0), FaultCode.ERROR_004_FLOW_K1_TO_K2_LOW.value),
        ("F04", BrewState.MASHING, ProcessSnapshot(k2_temperature_c=40, k2_level_l=18), FaultCode.ERROR_005_K2_MASHING_TEMP_LOW.value),
        ("F05", BrewState.TRANSFER_TO_K3, ProcessSnapshot(v4_open=False), FaultCode.ERROR_008_V4_CLOSED_TRANSFER_K3.value),
        ("F06", BrewState.BOILING, ProcessSnapshot(k2_temperature_c=110, k2_level_l=18), FaultCode.ERROR_011_K2_BOILING_TEMP_HIGH.value),
        ("F07", BrewState.FERMENTING, ProcessSnapshot(k4_temperature_c=30, k4_level_l=18), FaultCode.ERROR_018_K4_FERMENT_TEMP_HIGH.value),
        ("F08", BrewState.BOILING, ProcessSnapshot(emergency_stop=True), FaultCode.EMERGENCY_001_ESTOP_ACTIVE.value),
        ("F09", BrewState.MASHING, ProcessSnapshot(k2_temperature_c=130, k2_level_l=18), FaultCode.EMERGENCY_006_K2_TEMP_TOO_HIGH.value),
    ]
    passed = 0
    for test_id, initial_state, snapshot, expected in tests:
        fsm = BrewStateMachine(recipe=build_fast_recipe())
        fsm.state = initial_state
        result = fsm.update(snapshot, 1)
        ok = result.display_state == expected
        passed += int(ok)
        print(f"\n{test_id} erwartet: {expected}")
        for line in result.terminal_lines():
            print(line)
        print("Status:", "BESTANDEN" if ok else "NICHT BESTANDEN")
    print(f"\nFehlercode-Abnahme: {passed}/{len(tests)} bestanden")


if __name__ == "__main__":
    run_acceptance_suite()
