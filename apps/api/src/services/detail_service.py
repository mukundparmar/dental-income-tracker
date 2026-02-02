from __future__ import annotations

import re
from datetime import date


DATE_PATTERN = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
PHONE_PATTERN = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
TREATMENT_CODE_PATTERN = re.compile(r"\b[A-Z]\d{3,4}\b")
TOOTH_PATTERN = re.compile(r"(?:tooth|tooth#|#)\s*(\d{1,2})", re.IGNORECASE)
CURRENCY_PATTERN = re.compile(r"\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})")
PATIENT_PATTERN = re.compile(
    r"(?:patient|pt)\s*[:\-]\s*([A-Za-z ,.'-]+)", re.IGNORECASE
)


def _parse_date(value: str) -> date | None:
    for separator in ("/", "-"):
        parts = value.split(separator)
        if len(parts) != 3:
            continue
        if len(parts[0]) == 4:
            year, month, day = parts
        else:
            month, day, year = parts
        if len(year) == 2:
            year = f"20{year}"
        try:
            return date(int(year), int(month), int(day))
        except ValueError:
            return None
    return None


def _clean_description(line: str, tokens: list[str]) -> str:
    cleaned = line
    for token in tokens:
        if token:
            cleaned = cleaned.replace(token, "")
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -\t")
    return cleaned


def parse_detail_lines(raw_text: str, default_date: date | None) -> list[dict[str, object]]:
    details: list[dict[str, object]] = []
    for line in (line.strip() for line in raw_text.splitlines()):
        if not line:
            continue
        lowered = line.lower()
        if "production" in lowered or "collections" in lowered:
            continue

        date_match = DATE_PATTERN.search(line)
        parsed_date = _parse_date(date_match.group(1)) if date_match else None
        phone_match = PHONE_PATTERN.search(line)
        patient_match = PATIENT_PATTERN.search(line)
        treatment_match = TREATMENT_CODE_PATTERN.search(line)
        tooth_match = TOOTH_PATTERN.search(line)
        amounts = [match.group(0) for match in CURRENCY_PATTERN.finditer(line)]

        charges = None
        payments = None
        if amounts:
            parsed_amounts = []
            for amount in amounts:
                raw = amount.replace("$", "").replace(",", "")
                try:
                    parsed_amounts.append(float(raw))
                except ValueError:
                    continue
            if parsed_amounts:
                charges = parsed_amounts[0]
                if len(parsed_amounts) > 1:
                    payments = parsed_amounts[1]

        tokens = [
            date_match.group(1) if date_match else "",
            phone_match.group(0) if phone_match else "",
            patient_match.group(0) if patient_match else "",
            treatment_match.group(0) if treatment_match else "",
            tooth_match.group(0) if tooth_match else "",
            *amounts,
        ]
        description = _clean_description(line, tokens)
        patient_name = patient_match.group(1).strip() if patient_match else None
        tooth_number = tooth_match.group(1) if tooth_match else None

        has_signal = any(
            value is not None and value != ""
            for value in (
                patient_name,
                tooth_number,
                treatment_match.group(0) if treatment_match else None,
                charges,
                payments,
                phone_match.group(0) if phone_match else None,
            )
        )
        if not has_signal:
            continue

        details.append(
            {
                "entry_date": parsed_date or default_date,
                "patient_name": patient_name,
                "tooth_number": tooth_number,
                "treatment_code": treatment_match.group(0) if treatment_match else None,
                "description": description or line,
                "charges": charges,
                "payments": payments,
                "phone_number": phone_match.group(0) if phone_match else None,
                "raw_line": line,
            }
        )
    return details
