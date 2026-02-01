from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


class OCRError(RuntimeError):
    pass


def run_ocr(image_path: Path) -> str:
    try:
        import pytesseract
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise OCRError("pytesseract is not installed") from exc

    if not image_path.exists():
        raise OCRError(f"Image not found: {image_path}")

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as exc:  # pragma: no cover - tesseract runtime
        logger.exception("OCR failed for %s", image_path)
        raise OCRError("OCR processing failed") from exc
