from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from apps.api.src.db.database import get_connection

router = APIRouter()

templates = Jinja2Templates(directory="apps/api/src/templates")


@router.get("/")
def get_dashboard(request: Request):
    with get_connection() as connection:
        latest_week = connection.execute(
            "SELECT week_start FROM rollups ORDER BY week_start DESC LIMIT 1"
        ).fetchone()

        rollups = []
        if latest_week:
            rollups = connection.execute(
                """
                SELECT rollups.*, clinics.name AS clinic_name
                FROM rollups
                LEFT JOIN clinics ON clinics.id = rollups.clinic_id
                WHERE rollups.week_start = ?
                ORDER BY rollups.clinic_id
                """,
                (latest_week["week_start"],),
            ).fetchall()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "latest_week": latest_week["week_start"] if latest_week else None,
            "rollups": rollups,
        },
    )
