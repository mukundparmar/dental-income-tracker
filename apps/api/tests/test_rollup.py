from __future__ import annotations

from datetime import date
from pathlib import Path

from apps.api.src.db.database import get_connection, init_db
from apps.api.src.services.rollup_service import generate_weekly_rollups


def test_generate_weekly_rollups(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    init_db()
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO clinics (name, pay_percentage) VALUES (?, ?)",
            ("Test Clinic", 0.4),
        )
        connection.execute(
            """
            INSERT INTO uploads (filename, clinic_id, entry_date, status, created_at,
                                 production_amount, collections_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "sample.png",
                1,
                "2024-02-05",
                "processed",
                "2024-02-05T00:00:00Z",
                1000.0,
                800.0,
            ),
        )

    rollup_ids = generate_weekly_rollups(date(2024, 2, 5))
    assert rollup_ids

    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM rollups").fetchall()

    assert len(rows) == 2
    clinic_rollup = next(row for row in rows if row["clinic_id"] == 1)
    assert clinic_rollup["total_collections"] == 800.0
    assert clinic_rollup["estimated_pay"] == 320.0
