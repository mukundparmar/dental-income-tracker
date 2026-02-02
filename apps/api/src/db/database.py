from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from apps.api.src.utils.config import load_settings


def _sqlite_path(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// paths are supported in MVP")
    return Path(database_url.replace("sqlite:///", "")).resolve()


def init_db() -> None:
    settings = load_settings()
    db_path = _sqlite_path(settings.database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS clinics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pay_percentage REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                clinic_id INTEGER NOT NULL,
                entry_date TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                raw_ocr_text TEXT,
                production_amount REAL,
                collections_amount REAL,
                error_reason TEXT,
                FOREIGN KEY (clinic_id) REFERENCES clinics(id)
            );

            CREATE TABLE IF NOT EXISTS rollups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start TEXT NOT NULL,
                clinic_id INTEGER,
                total_production REAL NOT NULL,
                total_collections REAL NOT NULL,
                estimated_pay REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (clinic_id) REFERENCES clinics(id)
            );

            CREATE TABLE IF NOT EXISTS entry_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                entry_date TEXT,
                patient_name TEXT,
                tooth_number TEXT,
                treatment_code TEXT,
                description TEXT,
                charges REAL,
                payments REAL,
                phone_number TEXT,
                raw_line TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
            );
            """
        )


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings = load_settings()
    db_path = _sqlite_path(settings.database_url)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
