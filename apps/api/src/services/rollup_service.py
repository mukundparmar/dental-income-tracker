from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from apps.api.src.db.database import get_connection
from apps.api.src.utils.config import load_settings

logger = logging.getLogger(__name__)


def generate_weekly_rollups(week_start: date) -> list[int]:
    week_end = week_start + timedelta(days=7)
    created_at = datetime.now(tz=timezone.utc).isoformat()
    settings = load_settings()

    with get_connection() as connection:
        entries = connection.execute(
            """
            SELECT uploads.clinic_id, clinics.pay_percentage,
                   COALESCE(uploads.production_amount, 0) AS production_amount,
                   COALESCE(uploads.collections_amount, 0) AS collections_amount
            FROM uploads
            JOIN clinics ON clinics.id = uploads.clinic_id
            WHERE uploads.status = 'processed'
              AND uploads.entry_date >= ?
              AND uploads.entry_date < ?
            """,
            (week_start.isoformat(), week_end.isoformat()),
        ).fetchall()

        totals_by_clinic: dict[int, dict[str, float]] = {}
        for entry in entries:
            clinic_id = int(entry["clinic_id"])
            totals = totals_by_clinic.setdefault(
                clinic_id,
                {
                    "production": 0.0,
                    "collections": 0.0,
                    "pay_percentage": float(entry["pay_percentage"]),
                },
            )
            totals["production"] += float(entry["production_amount"])
            totals["collections"] += float(entry["collections_amount"])

        rollup_ids: list[int] = []
        overall_production = 0.0
        overall_collections = 0.0

        for clinic_id, totals in totals_by_clinic.items():
            estimated_pay = totals["collections"] * totals["pay_percentage"]
            cursor = connection.execute(
                """
                INSERT INTO rollups (
                    week_start, clinic_id, total_production, total_collections, estimated_pay, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    week_start.isoformat(),
                    clinic_id,
                    totals["production"],
                    totals["collections"],
                    estimated_pay,
                    created_at,
                ),
            )
            rollup_ids.append(int(cursor.lastrowid))
            overall_production += totals["production"]
            overall_collections += totals["collections"]

        if totals_by_clinic:
            overall_pay = overall_collections * settings.pay_percentage
            cursor = connection.execute(
                """
                INSERT INTO rollups (
                    week_start, clinic_id, total_production, total_collections, estimated_pay, created_at
                ) VALUES (?, NULL, ?, ?, ?, ?)
                """,
                (
                    week_start.isoformat(),
                    overall_production,
                    overall_collections,
                    overall_pay,
                    created_at,
                ),
            )
            rollup_ids.append(int(cursor.lastrowid))

    logger.info("Generated %s rollups for week %s", len(rollup_ids), week_start)
    return rollup_ids


def refresh_weekly_rollups(week_start: date) -> list[int]:
    with get_connection() as connection:
        connection.execute("DELETE FROM rollups WHERE week_start = ?", (week_start.isoformat(),))
    return generate_weekly_rollups(week_start)
