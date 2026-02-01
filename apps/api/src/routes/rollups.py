from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from apps.api.src.db.database import get_connection
from apps.api.src.models.schemas import RollupOut

router = APIRouter()


@router.get("/weekly-rollups", response_model=list[RollupOut])
def get_weekly_rollups() -> list[RollupOut]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, week_start, clinic_id, total_production, total_collections,
                   estimated_pay, created_at
            FROM rollups
            ORDER BY week_start DESC, clinic_id
            """
        ).fetchall()

    rollups = []
    for row in rows:
        rollups.append(
            {
                **dict(row),
                "week_start": date.fromisoformat(row["week_start"]),
            }
        )
    return rollups
