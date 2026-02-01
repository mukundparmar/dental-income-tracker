from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from apps.api.src.db.database import init_db
from apps.api.src.services.clinic_service import seed_clinics
from apps.api.src.services.process_service import process_new_uploads

logging.basicConfig(level=logging.INFO)


def main() -> None:
    init_db()
    seed_clinics()
    processed = process_new_uploads()
    logging.info("Processed %s uploads", len(processed))


if __name__ == "__main__":
    main()
