from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class ClinicCreate(BaseModel):
    name: str
    pay_percentage: float


class ClinicOut(BaseModel):
    id: int
    name: str
    pay_percentage: float


class UploadEntry(BaseModel):
    id: int
    filename: str
    clinic_id: int
    entry_date: Optional[date]
    status: str
    created_at: str
    production_amount: Optional[float]
    collections_amount: Optional[float]
    error_reason: Optional[str]


class RollupOut(BaseModel):
    id: int
    week_start: date
    clinic_id: Optional[int]
    total_production: float
    total_collections: float
    estimated_pay: float
    created_at: str
