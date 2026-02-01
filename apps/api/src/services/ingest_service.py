from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from apps.api.src.db.database import get_connection
from apps.api.src.utils.config import load_settings

logger = logging.getLogger(__name__)

DATE_PATTERNS = [
    re.compile(r"(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(\d{4})(\d{2})(\d{2})"),
]


def _parse_date_from_filename(filename: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(filename)
        if match:
            if len(match.groups()) == 1:
                return match.group(1)
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None


def _default_clinic_id() -> int:
    with get_connection() as connection:
        row = connection.execute("SELECT id FROM clinics ORDER BY id LIMIT 1").fetchone()
        if not row:
            raise ValueError("No clinics available. Create a clinic before ingesting.")
        return int(row["id"])


def ingest_uploads() -> list[int]:
    settings = load_settings()
    uploads_dir = settings.uploads_dir
    uploads_dir.mkdir(parents=True, exist_ok=True)

    processed_ids: list[int] = []
    with get_connection() as connection:
        existing_files = {
            row["filename"]
            for row in connection.execute("SELECT filename FROM uploads")
        }

        for file_path in sorted(uploads_dir.iterdir()):
            if file_path.is_dir():
                continue
            if file_path.name in existing_files:
                continue

            entry_date = _parse_date_from_filename(file_path.name)
            created_at = datetime.now(tz=timezone.utc).isoformat()
            clinic_id = _default_clinic_id()
            cursor = connection.execute(
                """
                INSERT INTO uploads (filename, clinic_id, entry_date, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (file_path.name, clinic_id, entry_date, "new", created_at),
            )
            processed_ids.append(int(cursor.lastrowid))
            logger.info("Registered upload %s", file_path.name)
    return processed_ids
