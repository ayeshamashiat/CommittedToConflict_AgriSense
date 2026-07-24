"""Pydantic ChatRequest / ChatResponse - the contract the frontend codes against."""

from pydantic import BaseModel

from app.schemas.farm_profile import FarmProfileIn, FarmProfileOut
from app.schemas.tool_io import FinanceOutput, WeatherOutput


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    profile: FarmProfileIn | None = None


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
