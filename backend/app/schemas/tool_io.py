"""Shared Pydantic input/output shapes used across all AgriTool implementations."""

from pydantic import BaseModel, Field


# ---- Weather tool -----------------------------------------------------


class WeatherInput(BaseModel):
    location: str = Field(..., description="Free-text location, e.g. 'Rangpur, Bangladesh'")


class ForecastDay(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    precipitation_mm: float


class WeatherOutput(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature: float = Field(..., description="Current temperature in Celsius")
    rainfall: float = Field(..., description="Current/most recent precipitation in mm")
    humidity: float = Field(..., description="Current relative humidity percent")
    forecast: list[ForecastDay]


# ---- RAG tool -----------------------------------------------------------


class RAGInput(BaseModel):
    query: str
    n_results: int = 3


class RetrievedPassage(BaseModel):
    text: str
    source: str
    score: float | None = None


class RAGOutput(BaseModel):
    passages: list[str]
    sources: list[str]
    results: list[RetrievedPassage]


# ---- Financial calculator tool ------------------------------------------


class FinanceInput(BaseModel):
    crop: str
    farm_size: float = Field(..., description="Farm size in acres")
    budget: float = Field(..., description="Available budget in local currency")


class FinanceOutput(BaseModel):
    crop: str
    seed_cost: float
    fertilizer_cost: float
    labor_cost: float
    water_cost: float
    total_cost: float
    revenue: float
    profit: float
    roi_percent: float
    break_even_days: float | None
    within_budget: bool
    currency: str = "BDT"
    data_confidence: str = Field(
        default="mixed",
        description=(
            "'official' if yield/price/fertilizer cost are all from cited sources; "
            "'mixed' if some cost components (seed/labor-days/water) are estimated."
        ),
    )
    yield_source: str = ""
    price_source: str = ""
    notes: str = ""
