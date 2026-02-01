from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from apps.api.src.db.database import init_db
from apps.api.src.services.clinic_service import seed_clinics
from apps.api.src.services.ingest_service import ingest_uploads

logging.basicConfig(level=logging.INFO)


def main() -> None:
    init_db()
    seed_clinics()
    new_ids = ingest_uploads()
    logging.info("Registered %s new uploads", len(new_ids))


if __name__ == "__main__":
    main()
