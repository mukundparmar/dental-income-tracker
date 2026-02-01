from __future__ import annotations

from apps.api.src.services.rules.base import BaseParser


def test_base_parser_extracts_values() -> None:
    text = "Production: $12,345.67\nCollections: $8,765.43"
    parser = BaseParser()
    result = parser.parse(text)
    assert result.production_amount == 12345.67
    assert result.collections_amount == 8765.43
