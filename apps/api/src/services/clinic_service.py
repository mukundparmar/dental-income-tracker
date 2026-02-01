from __future__ import annotations

from typing import Any

from apps.api.src.db.database import get_connection
from apps.api.src.utils.config import load_clinics_config, load_settings


def seed_clinics() -> None:
    settings = load_settings()
    clinics = load_clinics_config(settings.clinics_config_path)
    if not clinics:
        return

    with get_connection() as connection:
        existing = {
            row["name"]: row["id"]
            for row in connection.execute("SELECT id, name FROM clinics")
        }
        for clinic in clinics:
            name = clinic.get("name")
            pay_percentage = clinic.get("pay_percentage", settings.pay_percentage)
            if not name or name in existing:
                continue
            connection.execute(
                "INSERT INTO clinics (name, pay_percentage) VALUES (?, ?)",
                (name, float(pay_percentage)),
            )


def list_clinics() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, pay_percentage FROM clinics ORDER BY name"
        ).fetchall()
    return [dict(row) for row in rows]


def create_clinic(name: str, pay_percentage: float) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO clinics (name, pay_percentage) VALUES (?, ?)",
            (name, pay_percentage),
        )
        clinic_id = cursor.lastrowid
        row = connection.execute(
            "SELECT id, name, pay_percentage FROM clinics WHERE id = ?",
            (clinic_id,),
        ).fetchone()
    return dict(row)
