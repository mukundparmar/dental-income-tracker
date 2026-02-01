from __future__ import annotations

import logging

from fastapi import FastAPI

from apps.api.src.db.database import init_db
from apps.api.src.routes.clinics import router as clinics_router
from apps.api.src.routes.dashboard import router as dashboard_router
from apps.api.src.routes.entries import router as entries_router
from apps.api.src.routes.reprocess import router as reprocess_router
from apps.api.src.routes.rollups import router as rollups_router
from apps.api.src.services.clinic_service import seed_clinics

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Dental Income Tracker")


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    seed_clinics()


app.include_router(dashboard_router)
app.include_router(clinics_router)
app.include_router(entries_router)
app.include_router(rollups_router)
app.include_router(reprocess_router)
