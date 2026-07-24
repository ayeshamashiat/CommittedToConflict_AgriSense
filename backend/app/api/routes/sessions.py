"""Session listing and conversation history endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.farm_repo import get_profile, missing_fields
from app.db.repositories.message_repo import list_messages
from app.db.repositories.plan_repo import list_financial_projections, list_season_plans
from app.db.repositories.session_repo import get_session, list_sessions, list_sessions_for_farmer
from app.db.repositories.tool_log_repo import list_tool_calls
from app.schemas.farm_profile import FarmProfileOut

router = APIRouter(tags=["history"])


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: str

    model_config = {"from_attributes": True}


class ToolTraceOut(BaseModel):
    tool_name: str
    input_json: dict
    output_json: dict
    status: str
    latency_ms: float | None
    created_at: str


class SessionSummary(BaseModel):
    session_id: str
    created_at: str
    updated_at: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageOut]
    farm_profile: FarmProfileOut
    missing_fields: list[str]
    tool_trace: list[ToolTraceOut]
    season_plans: list[dict]
    financial_projections: list[dict]


@router.get("/sessions", response_model=list[SessionSummary])
def get_sessions(farmer_key: str | None = None, db: DBSession = Depends(get_db)) -> list[SessionSummary]:
    rows = list_sessions_for_farmer(db, farmer_key) if farmer_key else list_sessions(db)
    return [
        SessionSummary(
            session_id=s.id,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
        )
        for s in rows
    ]


@router.get("/history", response_model=HistoryResponse)
def get_history(session_id: str, db: DBSession = Depends(get_db)) -> HistoryResponse:
    session = get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    profile = get_profile(db, session_id)
    messages = list_messages(db, session_id)
    tool_calls = list_tool_calls(db, session_id)
    season_plans = list_season_plans(db, session_id)
    financial_projections = list_financial_projections(db, session_id)

    return HistoryResponse(
        session_id=session_id,
        messages=[
            MessageOut(role=m.role, content=m.content, created_at=m.created_at.isoformat())
            for m in messages
        ],
        farm_profile=FarmProfileOut.model_validate(profile) if profile else FarmProfileOut(),
        missing_fields=missing_fields(profile),
        tool_trace=[
            ToolTraceOut(
                tool_name=t.tool_name,
                input_json=t.input_json,
                output_json=t.output_json,
                status=t.status,
                latency_ms=t.latency_ms,
                created_at=t.created_at.isoformat(),
            )
            for t in tool_calls
        ],
        season_plans=[
            {
                "crop_name": p.crop_name,
                "land_preparation": p.land_preparation,
                "sowing": p.sowing,
                "fertilizer": p.fertilizer,
                "irrigation": p.irrigation,
                "pest_checks": p.pest_checks,
                "harvest": p.harvest,
            }
            for p in season_plans
        ],
        financial_projections=[
            {
                "crop_name": f.crop_name,
                "seed_cost": f.seed_cost,
                "fertilizer_cost": f.fertilizer_cost,
                "labor_cost": f.labor_cost,
                "water_cost": f.water_cost,
                "total_cost": f.total_cost,
                "revenue": f.revenue,
                "profit": f.profit,
                "roi_percent": f.roi_percent,
                "break_even_days": f.break_even_days,
            }
            for f in financial_projections
        ],
    )
