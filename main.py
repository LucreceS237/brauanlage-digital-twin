from __future__ import annotations

import argparse
from pathlib import Path

from ap4.simulation_runner import run_csv
from ap4.terminal_acceptance import run_acceptance_suite, run_fault_catalog_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="AP4 FSM Version 5 - ProcessSnapshot-Replay")
    parser.add_argument("mode", nargs="?", default="acceptance", choices=["acceptance", "faults", "csv"])
    parser.add_argument("--csv", default=str(Path(__file__).parent / "data" / "AP4_ProcessSnapshots_Normalzyklus_V5.csv"))
    args = parser.parse_args()
    if args.mode == "acceptance":
        run_acceptance_suite()
    elif args.mode == "faults":
        run_fault_catalog_suite()
    elif args.mode == "csv":
        run_csv(args.csv)


if __name__ == "__main__":
    main()
