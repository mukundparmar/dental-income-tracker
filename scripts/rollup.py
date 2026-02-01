from __future__ import annotations

import argparse
import logging
from datetime import date

from apps.api.src.db.database import init_db
from apps.api.src.services.clinic_service import seed_clinics
from apps.api.src.services.rollup_service import generate_weekly_rollups

logging.basicConfig(level=logging.INFO)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week-start", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()

    week_start = date.fromisoformat(args.week_start)
    init_db()
    seed_clinics()
    rollup_ids = generate_weekly_rollups(week_start)
    logging.info("Created %s rollup rows", len(rollup_ids))


if __name__ == "__main__":
    main()
