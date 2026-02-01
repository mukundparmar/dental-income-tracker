from __future__ import annotations

from fastapi import APIRouter

from apps.api.src.models.schemas import ClinicCreate, ClinicOut
from apps.api.src.services.clinic_service import create_clinic, list_clinics

router = APIRouter()


@router.get("/clinics", response_model=list[ClinicOut])
def get_clinics() -> list[ClinicOut]:
    return list_clinics()


@router.post("/clinics", response_model=ClinicOut)
def post_clinic(payload: ClinicCreate) -> ClinicOut:
    return create_clinic(payload.name, payload.pay_percentage)
