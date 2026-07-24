"""Pydantic ChatRequest / ChatResponse - the contract the frontend codes against."""

from pydantic import BaseModel, field_validator

from app.schemas.farm_profile import FarmProfileIn, FarmProfileOut
from app.schemas.tool_io import FinanceOutput, WeatherOutput

# Unlike the profile fields (which can be silently normalized to None and then
# surface as a "missing field" question), `message` is the whole reason a
# /chat turn exists — there's no sensible fallback for an empty one, so a
# blank message or Swagger's leftover "string" placeholder is rejected
# outright (422) instead of silently being treated as real farmer input.
_PLACEHOLDER_MESSAGES = {"", "string"}


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    profile: FarmProfileIn | None = None

    @field_validator("message")
    @classmethod
    def _reject_placeholder_message(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned.lower() in _PLACEHOLDER_MESSAGES:
            raise ValueError(
                "message is empty or still the example placeholder text — "
                "please enter what you'd like to ask the agent."
            )
        return cleaned


class CropRecommendation(BaseModel):
    crop_name: str
    suitability: str
    risk_level: str
    water_need: str
    estimated_profit: float | None = None
    reasoning: str


class SeasonPlanOut(BaseModel):
    crop_name: str
    land_preparation: str
    sowing: str
    fertilizer: str
    irrigation: str
    pest_checks: str
    harvest: str


class ToolTraceEntry(BaseModel):
    tool_name: str
    input: dict
    output: dict
    status: str = "success"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    farm_profile: FarmProfileOut
    missing_fields: list[str]
    recommendations: list[CropRecommendation] | None = None
    season_plan: SeasonPlanOut | None = None
    financial_summary: FinanceOutput | None = None
    weather: WeatherOutput | None = None
    trace: list[ToolTraceEntry] = []
