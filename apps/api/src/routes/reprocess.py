from __future__ import annotations

from fastapi import APIRouter, HTTPException

from apps.api.src.services.process_service import reprocess_upload

router = APIRouter()


@router.post("/reprocess/{upload_id}")
def post_reprocess(upload_id: int) -> dict[str, str]:
    success = reprocess_upload(upload_id)
    if not success:
        raise HTTPException(status_code=404, detail="Upload not found")
    return {"status": "reprocessed"}
