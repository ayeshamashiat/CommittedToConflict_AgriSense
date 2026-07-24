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


# ---- Fertilizer scheduler tool (Tier 1) ----------------------------------


class FertilizerScheduleInput(BaseModel):
    crop: str
    farm_size: float = Field(..., description="Farm size in acres")


class FertilizerStageDose(BaseModel):
    stage: str
    days_after_sowing: int
    urea_kg: float
    tsp_kg: float
    mop_kg: float
    cost_bdt: float
    organic_alternative: str


class FertilizerScheduleOutput(BaseModel):
    crop: str
    stages: list[FertilizerStageDose]
    total_cost_bdt: float
    data_confidence: str
    notes: str


# ---- Irrigation scheduler tool (Tier 1) ----------------------------------


class IrrigationScheduleInput(BaseModel):
    crop: str
    farm_size: float = Field(..., description="Farm size in acres")
    water_availability: str


class IrrigationEvent(BaseModel):
    stage: str
    days_after_sowing: int
    note: str
    cost_bdt: float


class IrrigationScheduleOutput(BaseModel):
    crop: str
    events: list[IrrigationEvent]
    total_cost_bdt: float
    notes: str


# ---- Pest & disease risk tool (Tier 1) -----------------------------------


class PestRiskInput(BaseModel):
    crop: str
    temperature: float
    humidity: float
    rainfall: float


class PestRiskItem(BaseModel):
    name: str
    kind: str  # "pest" | "disease"
    risk_level: str  # "Low" | "Medium" | "High"
    trigger_reason: str
    prevention: str
    treatment: str
    estimated_cost_bdt: float


class PestRiskOutput(BaseModel):
    crop: str
    risks: list[PestRiskItem]
    source: str


# ---- Scenario simulation tool (Tier 1) -----------------------------------


class ScenarioSimulationInput(BaseModel):
    crop: str
    farm_size: float = Field(..., description="Farm size in acres")
    budget: float
    rainfall_change_percent: float = Field(
        default=0.0, description="e.g. -30 for 'rainfall drops 30%', +20 for 'rises 20%'"
    )
    budget_change_percent: float = Field(
        default=0.0, description="e.g. -40 for 'budget cut 40%'"
    )


class ScenarioSimulationOutput(BaseModel):
    crop: str
    original: FinanceOutput
    revised: FinanceOutput
    assumptions: str
    explanation: str
