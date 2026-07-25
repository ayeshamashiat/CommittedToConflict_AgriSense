"""POST /simulate - Tier 1 scenario simulation ("what if rainfall drops 30%?").

Standalone endpoint (rather than folded into /chat) since it's farmer-initiated
on demand against an existing recommendation, not part of the standard intake
-> recommend flow.
"""

import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.farm_repo import get_profile
from app.db.repositories.plan_repo import get_latest_financial_projection
from app.db.repositories.session_repo import get_or_create_session
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import ScenarioSimulationInput, ScenarioSimulationOutput
from app.tools.scenario_simulator_tool import ScenarioSimulatorTool

router = APIRouter(tags=["simulate"])
_tool = ScenarioSimulatorTool()


class SimulateRequest(BaseModel):
    session_id: str
    crop: str | None = Field(
        default=None, description="Defaults to the last crop discussed in this session"
    )
    farm_size: float | None = Field(default=None, description="Defaults to the session's farm profile")
    budget: float | None = Field(default=None, description="Defaults to the session's farm profile")
    rainfall_change_percent: float = 0.0
    budget_change_percent: float = 0.0


class SimulateResponse(ScenarioSimulationOutput):
    session_id: str


@router.post("/simulate", response_model=SimulateResponse)
def simulate(payload: SimulateRequest, db: DBSession = Depends(get_db)) -> SimulateResponse:
    session, _ = get_or_create_session(db, payload.session_id)

    crop = payload.crop
    if crop is None:
        latest = get_latest_financial_projection(db, session.id)
        if latest is None:
            raise HTTPException(
                status_code=422,
                detail="No crop specified and no prior recommendation found in this session — "
                "pass 'crop' explicitly, or run /chat first.",
            )
        crop = latest.crop_name

    profile = get_profile(db, session.id)
    farm_size = payload.farm_size or (profile.farm_size if profile else None)
    budget = payload.budget or (profile.budget if profile else None)
    if farm_size is None or budget is None:
        raise HTTPException(
            status_code=422,
            detail="farm_size and budget must be provided (or already known from the session's farm profile).",
        )

    input_data = ScenarioSimulationInput(
        crop=crop,
        farm_size=farm_size,
        budget=budget,
        rainfall_change_percent=payload.rainfall_change_percent,
        budget_change_percent=payload.budget_change_percent,
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

    return SimulateResponse(session_id=session.id, **result.model_dump())
