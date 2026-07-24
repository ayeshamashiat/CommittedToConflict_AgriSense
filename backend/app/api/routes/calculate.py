"""POST /calculate - financial calculator (costs, revenue, profit, ROI, break-even)."""

import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.plan_repo import save_financial_projection
from app.db.repositories.session_repo import get_or_create_session
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import FinanceInput, FinanceOutput
from app.tools.finance_tool import FinanceTool

router = APIRouter(tags=["calculate"])
_tool = FinanceTool()


class CalculateRequest(FinanceInput):
    session_id: str | None = None


class CalculateResponse(FinanceOutput):
    session_id: str


@router.post("/calculate", response_model=CalculateResponse)
def calculate(payload: CalculateRequest, db: DBSession = Depends(get_db)) -> CalculateResponse:
    session = get_or_create_session(db, payload.session_id)
    input_data = FinanceInput(
        crop=payload.crop, farm_size=payload.farm_size, budget=payload.budget
    )

    started = time.perf_counter()
    result = _tool.run(input_data)

    log_tool_call(
        db,
        session_id=session.id,
        tool_name=_tool.name,
        input_json=input_data.model_dump(),
        output_json=result.model_dump(),
        status="success",
        latency_ms=(time.perf_counter() - started) * 1000,
    )

    save_financial_projection(
        db,
        session_id=session.id,
        crop_name=result.crop,
        figures=result.model_dump(),
    )

    return CalculateResponse(session_id=session.id, **result.model_dump())
