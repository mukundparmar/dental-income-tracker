from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from apps.api.src.db.database import get_connection
from apps.api.src.models.schemas import UploadEntry

router = APIRouter()


@router.get("/entries", response_model=list[UploadEntry])
def get_entries() -> list[UploadEntry]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, clinic_id, entry_date, status, created_at,
                   production_amount, collections_amount, error_reason
            FROM uploads
            ORDER BY created_at DESC
            """
        ).fetchall()
    entries = []
    for row in rows:
        entry_date = date.fromisoformat(row["entry_date"]) if row["entry_date"] else None
        entries.append({**dict(row), "entry_date": entry_date})
    return entries
