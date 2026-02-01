from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    database_url: str
    uploads_dir: Path
    processed_dir: Path
    clinics_config_path: Path
    pay_percentage: float


def load_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///data/db.sqlite3")
    uploads_dir = Path(os.getenv("UPLOADS_DIR", "data/uploads")).resolve()
    processed_dir = Path(os.getenv("PROCESSED_DIR", "data/processed")).resolve()
    clinics_config_path = Path(os.getenv("CLINICS_CONFIG", "data/clinics.json")).resolve()
    pay_percentage = float(os.getenv("PAY_PERCENTAGE", "0.35"))
    return Settings(
        database_url=database_url,
        uploads_dir=uploads_dir,
        processed_dir=processed_dir,
        clinics_config_path=clinics_config_path,
        pay_percentage=pay_percentage,
    )


def load_clinics_config(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    if not isinstance(data, list):
        raise ValueError("Clinics config must be a list of clinics")
    return data
