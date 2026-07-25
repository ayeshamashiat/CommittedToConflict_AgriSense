"""GET /price-intelligence - Tier 2 market price intelligence
(sell-now / store-and-wait). Standalone endpoint, same reasoning as
/marketplace and /simulate — farmer-initiated on demand.
"""

import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import PriceIntelligenceInput, PriceIntelligenceOutput
from app.tools.price_intelligence_tool import PriceIntelligenceTool

router = APIRouter(tags=["price_intelligence"])
_tool = PriceIntelligenceTool()


@router.get("/price-intelligence", response_model=PriceIntelligenceOutput)
def price_intelligence(
    crop: str = Query(...),
    session_id: str | None = Query(default=None, description="If given, logs the call to that session's trace"),
    db: DBSession = Depends(get_db),
) -> PriceIntelligenceOutput:
    input_data = PriceIntelligenceInput(crop=crop)

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
