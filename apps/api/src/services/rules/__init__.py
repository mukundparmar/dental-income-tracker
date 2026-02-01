from __future__ import annotations

from typing import Dict

from apps.api.src.services.rules.base import BaseParser

PARSER_REGISTRY: Dict[str, BaseParser] = {}


def get_parser(clinic_name: str | None) -> BaseParser:
    if clinic_name and clinic_name in PARSER_REGISTRY:
        return PARSER_REGISTRY[clinic_name]
    return BaseParser()
