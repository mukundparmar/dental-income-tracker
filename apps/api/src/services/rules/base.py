from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParseResult:
    production_amount: float | None
    collections_amount: float | None


class BaseParser:
    production_patterns = [
        re.compile(r"production\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)", re.I),
        re.compile(r"prod\.?\s*\$?([\d,]+(?:\.\d{2})?)", re.I),
    ]
    collections_patterns = [
        re.compile(r"collections?\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)", re.I),
        re.compile(r"coll\.?\s*\$?([\d,]+(?:\.\d{2})?)", re.I),
    ]

    @staticmethod
    def _extract(patterns: list[re.Pattern[str]], text: str) -> float | None:
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                raw = match.group(1).replace(",", "")
                try:
                    return float(raw)
                except ValueError:
                    continue
        return None

    def parse(self, text: str) -> ParseResult:
        production = self._extract(self.production_patterns, text)
        collections = self._extract(self.collections_patterns, text)
        return ParseResult(production_amount=production, collections_amount=collections)
