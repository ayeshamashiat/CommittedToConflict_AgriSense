"""POST /weather - real weather lookup for a location, logged for the Agent Trace panel."""

import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.session_repo import get_or_create_session
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import WeatherInput, WeatherOutput
from app.tools.weather_tool import WeatherTool, WeatherToolError

router = APIRouter(tags=["weather"])
_tool = WeatherTool()


class WeatherRequest(WeatherInput):
    session_id: str | None = None


class WeatherResponse(WeatherOutput):
    session_id: str


@router.post("/weather", response_model=WeatherResponse)
def get_weather(payload: WeatherRequest, db: DBSession = Depends(get_db)) -> WeatherResponse:
    session, _ = get_or_create_session(db, payload.session_id)
    input_data = WeatherInput(location=payload.location)

    started = time.perf_counter()
    try:
        result = _tool.run(input_data)
    except WeatherToolError as exc:
        log_tool_call(
            db,
            session_id=session.id,
            tool_name=_tool.name,
            input_json=input_data.model_dump(),
            output_json={},
            status="error",
            error_message=str(exc),
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    log_tool_call(
        db,
        session_id=session.id,
        tool_name=_tool.name,
        input_json=input_data.model_dump(),
        output_json=result.model_dump(),
        status="success",
        latency_ms=(time.perf_counter() - started) * 1000,
    )

    return WeatherResponse(session_id=session.id, **result.model_dump())
