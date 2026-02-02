from __future__ import annotations

import shutil
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.api.src.db.database import get_connection
from apps.api.src.services.process_service import process_new_uploads
from apps.api.src.services.rollup_service import refresh_weekly_rollups
from apps.api.src.utils.config import load_settings

router = APIRouter()

templates = Jinja2Templates(directory="apps/api/src/templates")


def _get_dashboard_data() -> tuple[str | None, list[dict], list[dict]]:
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
        clinics = connection.execute(
            "SELECT id, name FROM clinics ORDER BY name"
        ).fetchall()

    return (
        latest_week["week_start"] if latest_week else None,
        rollups,
        clinics,
    )


def _build_dashboard_response(
    request: Request,
    upload_message: str | None = None,
    upload_error: str | None = None,
) -> templates.TemplateResponse:
    latest_week, rollups, clinics = _get_dashboard_data()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "latest_week": latest_week,
            "rollups": rollups,
            "clinics": clinics,
            "upload_message": upload_message,
            "upload_error": upload_error,
        },
    )


@router.get("/")
def get_dashboard(request: Request):
    upload_message = "Upload received. Processing started." if request.query_params.get(
        "uploaded"
    ) else None
    return _build_dashboard_response(request, upload_message=upload_message)


@router.post("/upload")
async def post_upload(
    request: Request,
    clinic_id: int = Form(...),
    entry_date: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.filename:
        return _build_dashboard_response(
            request, upload_error="Please choose an image to upload."
        )
    try:
        parsed_date = date.fromisoformat(entry_date)
    except ValueError:
        return _build_dashboard_response(
            request,
            upload_error="Please provide a valid entry date (YYYY-MM-DD).",
        )

    settings = load_settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name
    unique_suffix = uuid.uuid4().hex[:8]
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
    stored_name = f"{timestamp}_{unique_suffix}_{safe_name}"
    destination = settings.uploads_dir / stored_name

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    created_at = datetime.now(tz=timezone.utc).isoformat()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO uploads (filename, clinic_id, entry_date, status, created_at)
            VALUES (?, ?, ?, 'new', ?)
            """,
            (stored_name, clinic_id, parsed_date.isoformat(), created_at),
        )

    week_start = parsed_date - timedelta(days=parsed_date.weekday())
    try:
        process_new_uploads()
        refresh_weekly_rollups(week_start)
    except Exception as exc:
        return _build_dashboard_response(
            request,
            upload_error=(
                "Upload saved, but processing failed. "
                f"Run the process/rollup scripts or try again. ({exc})"
            ),
        )

    return RedirectResponse(url="/?uploaded=1", status_code=303)
