"""GET /marketplace - Tier 2 marketplace & supplier comparison.

Standalone endpoint (same reasoning as /simulate): comparing suppliers is
farmer-initiated on demand ("where can I buy urea"), not part of the standard
intake -> recommend flow, so it doesn't need to be folded into /chat's turn
handling. The chat agent can still call the same tool via chat_reply (see
agent/core.py) when a farmer asks about it in conversation.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import MarketplaceInput, MarketplaceOutput
from app.tools.marketplace_tool import MarketplaceTool

router = APIRouter(tags=["marketplace"])
_tool = MarketplaceTool()


@router.get("/marketplace", response_model=MarketplaceOutput)
def marketplace(
    item: str = Query(..., description="'urea' | 'tsp' | 'mop' | 'pesticide' | 'seed'"),
    crop: str | None = Query(default=None, description="Required when item='seed'"),
    quantity: float | None = Query(default=None),
    location: str | None = Query(default=None),
    session_id: str | None = Query(default=None, description="If given, logs the call to that session's trace"),
    db: DBSession = Depends(get_db),
) -> MarketplaceOutput:
    if item.strip().lower() == "seed" and not crop:
        raise HTTPException(status_code=422, detail="'crop' is required when item='seed'")

    input_data = MarketplaceInput(item=item, crop=crop, quantity=quantity, farmer_location=location)

    started = time.perf_counter()
    result = _tool.run(input_data)

    if session_id:
        log_tool_call(
            db,
            session_id=session_id,
            tool_name=_tool.name,
            input_json=input_data.model_dump(),
            output_json=result.model_dump(),
            status="success",
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    return result
