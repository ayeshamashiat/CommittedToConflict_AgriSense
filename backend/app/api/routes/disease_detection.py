"""POST /disease-detection - Tier 2 plant disease detection from images.

Accepts a multipart image upload (a farmer's leaf photo), not JSON, since
that's the natural shape for a file upload — everything else in this app is
JSON because it doesn't need to move binary data.
"""

import base64
import time

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import DiseaseDetectionInput, DiseaseDetectionOutput
from app.tools.disease_detection_tool import DiseaseDetectionTool

router = APIRouter(tags=["disease_detection"])
_tool = DiseaseDetectionTool()

_MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8MB


@router.post("/disease-detection", response_model=DiseaseDetectionOutput)
async def disease_detection(
    image: UploadFile = File(...),
    crop_hint: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    db: DBSession = Depends(get_db),
) -> DiseaseDetectionOutput:
    if image.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=422, detail="Image must be JPEG, PNG, or WEBP.")

    raw = await image.read()
    if len(raw) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=422, detail="Image too large (max 8MB).")

    input_data = DiseaseDetectionInput(image_base64=base64.b64encode(raw).decode(), crop_hint=crop_hint)

    started = time.perf_counter()
    result = _tool.run(input_data)

    if session_id:
        # Don't log the (large) base64 image blob into the trace — the crop
        # hint and result are what a judge needs to see, the image bytes
        # themselves would just bloat the Agent Activity view.
        log_tool_call(
            db,
            session_id=session_id,
            tool_name=_tool.name,
            input_json={"crop_hint": crop_hint, "image_provided": True},
            output_json=result.model_dump(),
            status="success",
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    return result
