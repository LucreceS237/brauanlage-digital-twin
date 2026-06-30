from __future__ import annotations

import argparse

from ap4.demo_run import run_demo
from ap4.terminal_acceptance import run_acceptance_suite, run_fault_catalog_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="AP4 Brauanlage FSM Version 4 - eindeutige ERROR/EMERGENCY-Codes")
    parser.add_argument(
        "mode",
        nargs="?",
        default="demo",
        choices=["demo", "acceptance", "faults"],
        help="demo = Normalablauf, acceptance = Abnahme, faults = einzelne Fehlercodes",
    )
    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()
    elif args.mode == "acceptance":
        run_acceptance_suite()
    elif args.mode == "faults":
        run_fault_catalog_suite()


if __name__ == "__main__":
    main()
