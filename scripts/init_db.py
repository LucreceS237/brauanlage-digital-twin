# scripts/init_db.py
# -*- coding: utf-8 -*-

from src.storage.database import BrewingDatabase
from src.storage.data_points import DATA_POINTS


def main() -> None:
    db = BrewingDatabase("data/brewing_data.db")
    db.initialize("database/schema.sql")
    db.seed_data_points(DATA_POINTS)

    print("Database initialized successfully.")
    print(f"Seeded {len(DATA_POINTS)} data points.")


if __name__ == "__main__":
    main()