"""Pydantic ChatRequest / ChatResponse - the contract the frontend codes against."""

from pydantic import BaseModel, field_validator

from app.schemas.farm_profile import FarmProfileIn, FarmProfileOut
from app.schemas.tool_io import (
    FertilizerScheduleOutput,
    FinanceOutput,
    IrrigationScheduleOutput,
    MarketplaceOutput,
    PestRiskOutput,
    PriceIntelligenceOutput,
    WeatherOutput,
)

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
    farmer_key: str | None = None
    # Tier 1 persistent memory: a stable identifier (e.g. phone number) the
    # farmer provides so a brand-new session can recognize them and carry
    # their farm profile forward without asking again. Optional — omit it
    # and the agent behaves exactly as a single-session chat.
    language: str = "en"  # Tier 2: "en" | "bn" — reply language

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
    # Tier 1: an actual dated calendar, not just staged descriptions — computed
    # from today's date + the crop's known duration, in agent/core.py.
    land_preparation_date: str | None = None
    sowing_date: str | None = None
    fertilizer_date: str | None = None
    pest_check_date: str | None = None
    harvest_date: str | None = None


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
    remembered_profile: bool = False  # Tier 1: true if carried forward via farmer_key
    recommendations: list[CropRecommendation] | None = None
    season_plan: SeasonPlanOut | None = None
    financial_summary: FinanceOutput | None = None
    weather: WeatherOutput | None = None
    trace: list[ToolTraceEntry] = []
    # Tier 1 additions, all for the top recommended crop:
    alerts: list[str] = []  # proactive weather-triggered advice
    fertilizer_schedule: FertilizerScheduleOutput | None = None
    irrigation_schedule: IrrigationScheduleOutput | None = None
    pest_risks: PestRiskOutput | None = None
    marketplace_offers: MarketplaceOutput | None = None  # Tier 2
    price_intelligence: PriceIntelligenceOutput | None = None  # Tier 2
