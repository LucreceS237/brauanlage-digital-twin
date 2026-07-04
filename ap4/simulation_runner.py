from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .ap4_interfaces import build_ap5_payload, build_ap6_dashboard_payload
from .data_loader import load_snapshots_from_csv
from .fsm import BrewStateMachine
from .fsm_contract import TransitionResult
from .process_snapshot import ProcessSnapshot
from .recipe import BrewRecipe, DEFAULT_RECIPE


def _dt(previous: ProcessSnapshot | None, current: ProcessSnapshot, default_dt_s: float = 1.0) -> float:
    if previous is None:
        return default_dt_s
    if previous.timestamp_s and current.timestamp_s:
        value = current.timestamp_s - previous.timestamp_s
        return value if value > 0 else default_dt_s
    return default_dt_s


def run_snapshots(snapshots: Iterable[ProcessSnapshot], recipe: BrewRecipe = DEFAULT_RECIPE, print_terminal: bool = True) -> list[TransitionResult]:
    fsm = BrewStateMachine(recipe=recipe)
    results: list[TransitionResult] = []
    previous: ProcessSnapshot | None = None
    if print_terminal:
        print("AP4 FSM Live-/Replay-Simulation mit ProcessSnapshot-Daten")
        print("Equipment: K1=Nachguss, K2=Maischen/Kochen, K3=Läutern, K4=Gären")
        print("Durchfluss: nur K1 -> K2")
        print("=" * 100)
    for idx, snapshot in enumerate(snapshots, start=1):
        dt_s = _dt(previous, snapshot, default_dt_s=1.0)
        result = fsm.update(snapshot, dt_s=dt_s)
        results.append(result)
        context = fsm.get_context_for_anomaly()
        if print_terminal:
            print(f"\n[{idx:03d}] timestamp={snapshot.timestamp or '-'} dt_s={dt_s:.1f}")
            print(f"Snapshot: Schritt={snapshot.aktueller_schritt}, K1_T={snapshot.k1_temperature_c:.1f}, K2_T={snapshot.k2_temperature_c:.1f}, K3_L={snapshot.k3_level_l:.1f}, K4_L={snapshot.k4_level_l:.1f}, DF_K1K2={snapshot.durchfluss_k1_k2_l_min:.2f}")
            for line in result.terminal_lines():
                print(line)
            print("AP5 payload:", json.dumps(build_ap5_payload(context), ensure_ascii=False)[:700])
            print("AP6 payload:", json.dumps(build_ap6_dashboard_payload(context), ensure_ascii=False)[:700])
        previous = snapshot
    return results


def run_csv(path: str | Path, recipe: BrewRecipe = DEFAULT_RECIPE) -> list[TransitionResult]:
    return run_snapshots(load_snapshots_from_csv(path), recipe=recipe, print_terminal=True)
