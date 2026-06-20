# scripts/inspect_latest.py
# -*- coding: utf-8 -*-

from pprint import pprint

from src.storage.database import BrewingDatabase


def main() -> None:
    db = BrewingDatabase("data/brewing_data.db")
    snapshot = db.get_latest_snapshot()

    print("\nLATEST DIGITAL TWIN SNAPSHOT")
    print("=" * 40)

    for key, value in snapshot.items():
        if key not in {"_meta", "alarms"}:
            print(f"{key}: {value}")

    print("\nMETA")
    print("=" * 40)
    pprint(snapshot.get("_meta", {}))

    print("\nALARMS")
    print("=" * 40)
    pprint(snapshot.get("alarms", []))


if __name__ == "__main__":
    main()