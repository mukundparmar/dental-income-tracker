from __future__ import annotations

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from apps.api.src.db.database import get_connection
from apps.api.src.services.ocr_service import OCRError, run_ocr
from apps.api.src.services.rules import get_parser
from apps.api.src.utils.config import load_settings

logger = logging.getLogger(__name__)


def process_new_uploads() -> list[int]:
    settings = load_settings()
    settings.processed_dir.mkdir(parents=True, exist_ok=True)

    processed_ids: list[int] = []
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT uploads.id, uploads.filename, clinics.name as clinic_name
            FROM uploads
            JOIN clinics ON clinics.id = uploads.clinic_id
            WHERE uploads.status = 'new'
            ORDER BY uploads.created_at
            """
        ).fetchall()

        for row in rows:
            upload_id = row["id"]
            filename = row["filename"]
            clinic_name = row["clinic_name"]
            file_path = settings.uploads_dir / filename
            try:
                raw_text = run_ocr(file_path)
                parser = get_parser(clinic_name)
                parsed = parser.parse(raw_text)

                connection.execute(
                    """
                    UPDATE uploads
                    SET raw_ocr_text = ?, production_amount = ?, collections_amount = ?,
                        status = 'processed', error_reason = NULL
                    WHERE id = ?
                    """,
                    (
                        raw_text,
                        parsed.production_amount,
                        parsed.collections_amount,
                        upload_id,
                    ),
                )
                _move_processed(file_path, settings.processed_dir)
                processed_ids.append(int(upload_id))
                logger.info("Processed upload %s", filename)
            except (OCRError, Exception) as exc:
                logger.exception("Failed to process %s", filename)
                connection.execute(
                    "UPDATE uploads SET status = 'failed', error_reason = ? WHERE id = ?",
                    (str(exc), upload_id),
                )
    return processed_ids


def _move_processed(file_path: Path, processed_dir: Path) -> None:
    if file_path.exists():
        destination = processed_dir / file_path.name
        shutil.move(str(file_path), str(destination))


def reprocess_upload(upload_id: int) -> bool:
    settings = load_settings()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT uploads.id, uploads.filename, clinics.name as clinic_name
            FROM uploads
            JOIN clinics ON clinics.id = uploads.clinic_id
            WHERE uploads.id = ?
            """,
            (upload_id,),
        ).fetchone()

        if not row:
            return False

        filename = row["filename"]
        clinic_name = row["clinic_name"]
        file_path = settings.processed_dir / filename
        if not file_path.exists():
            file_path = settings.uploads_dir / filename

        try:
            raw_text = run_ocr(file_path)
            parser = get_parser(clinic_name)
            parsed = parser.parse(raw_text)
            connection.execute(
                """
                UPDATE uploads
                SET raw_ocr_text = ?, production_amount = ?, collections_amount = ?,
                    status = 'processed', error_reason = NULL
                WHERE id = ?
                """,
                (
                    raw_text,
                    parsed.production_amount,
                    parsed.collections_amount,
                    upload_id,
                ),
            )
            if file_path.parent != settings.processed_dir:
                _move_processed(file_path, settings.processed_dir)
            return True
        except (OCRError, Exception) as exc:
            logger.exception("Failed to reprocess %s", filename)
            connection.execute(
                "UPDATE uploads SET status = 'failed', error_reason = ? WHERE id = ?",
                (str(exc), upload_id),
            )
            return False
