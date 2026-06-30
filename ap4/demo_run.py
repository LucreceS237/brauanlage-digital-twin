from __future__ import annotations

from .fsm import BrewStateMachine
from .process_snapshot import ProcessSnapshot
from .recipe import BrewRecipe


def run_demo() -> None:
    recipe = BrewRecipe(nachguss_min_duration_s=2, mashing_duration_s=2, lautering_duration_s=2, boiling_duration_s=2, transfer_to_k4_duration_s=2, fermentation_duration_s=2)
    fsm = BrewStateMachine(recipe=recipe)
    base = ProcessSnapshot()
    steps = [
        ("Start", base.with_updates(start_requested=True), 1),
        ("Precheck OK", base.with_updates(start_requested=True), 1),
        ("Nachguss", base.with_updates(v3_open=True, flow_k3_to_k1_l_min=1.1, k1_level_l=4.0), 3),
        ("Maischen", base.with_updates(k1_level_l=4.0, k1_temperature_c=66.0, v4_open=True, flow_k1_to_k2_l_min=1.0), 3),
        ("Läutern", base.with_updates(v4_open=True, flow_k1_to_k2_l_min=1.0, k2_level_l=4.0), 3),
        ("Kochen", base.with_updates(k2_level_l=4.0, k2_temperature_c=100.0), 3),
        ("Kühlen", base.with_updates(k2_temperature_c=24.0, v5_open=True, pump_on_feedback=True), 1),
        ("Austrag", base.with_updates(v5_open=True, pump_on_feedback=True, flow_k2_to_k4_l_min=1.0, k4_level_l=3.0), 3),
        ("Gären", base.with_updates(k4_level_l=3.0, k4_temperature_c=18.0), 3),
    ]
    print("AP4 Demo Version 4 - Normalpfad K3 -> K1 -> K2 -> K4")
    print("=" * 80)
    for name, snap, dt in steps:
        result = fsm.update(snap, dt_s=dt)
        print(f"\n{name}")
        for line in result.terminal_lines():
            print(line)
    print("\nFsmContext für AP5/AP6:")
    print(fsm.get_context_for_anomaly())
