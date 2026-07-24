"""POST /chat - the main entry point the frontend calls each turn."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_agent, get_db
from app.api.routes._fallback_orchestrator import run_fallback_turn
from app.db.repositories.farm_repo import get_or_create_profile, missing_fields, update_profile
from app.db.repositories.message_repo import add_message
from app.db.repositories.session_repo import get_or_create_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.farm_profile import FarmProfileOut

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: DBSession = Depends(get_db), agent=Depends(get_agent)) -> ChatResponse:
    session = get_or_create_session(db, payload.session_id)
    add_message(db, session.id, role="user", content=payload.message)

    if payload.profile is not None:
        update_profile(db, session.id, payload.profile.model_dump(exclude_unset=True))
    profile = get_or_create_profile(db, session.id)

    if agent is not None:
        # Member A's real orchestrator (memory + planner + tool executor + explainer).
        result = agent.handle_turn(db=db, session_id=session.id, message=payload.message, profile=profile)
    else:
        result = run_fallback_turn(db, session.id, profile)

    add_message(db, session.id, role="assistant", content=result["reply"])

    return ChatResponse(
        session_id=session.id,
        reply=result["reply"],
        farm_profile=FarmProfileOut.model_validate(profile),
        missing_fields=result.get("missing_fields", missing_fields(profile)),
        recommendations=result.get("recommendations"),
        season_plan=result.get("season_plan"),
        financial_summary=result.get("financial_summary"),
        weather=result.get("weather"),
        trace=result.get("trace", []),
    )
