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
    humidity_mean: float | None = None


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
    # Optional 7-day forecast (same shape weather_tool already returns) so risk
    # can be predicted per growth stage using the actual forecast for near-term
    # stages, not just today's snapshot repeated for the whole season. Omitting
    # it (e.g. a direct /calculate-style caller) falls back to the single
    # current-conditions behavior this tool always had.
    forecast: list[ForecastDay] = []


class PestRiskItem(BaseModel):
    name: str
    kind: str  # "pest" | "disease"
    risk_level: str  # "Low" | "Medium" | "High"
    growth_stage: str
    days_after_sowing: int
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


# ---- Marketplace & supplier comparison tool (Tier 2) ---------------------


class MarketplaceInput(BaseModel):
    item: str = Field(..., description="'urea' | 'tsp' | 'mop' | 'pesticide' | 'seed'")
    crop: str | None = Field(default=None, description="Required when item='seed'")
    quantity: float | None = Field(default=None, description="Quantity needed, in the offer's unit")
    farmer_location: str | None = None


class SupplierOffer(BaseModel):
    supplier_name: str
    district: str
    price_per_unit: float
    unit: str
    delivery_days: int
    distance_km: float
    rating: float | None = None
    estimated_total_cost: float | None = None
    composite_score: float
    # True when supplier_name/location/distance_km came from a real
    # OpenStreetMap lookup rather than the seeded mock catalog — price/
    # delivery_days are still estimates even then (see marketplace_tool.py),
    # since no public source publishes real per-shop pricing for these
    # informal retailers.
    is_real_location: bool = False


class MarketplaceOutput(BaseModel):
    item: str
    unit: str
    offers: list[SupplierOffer]
    ranking_method: str
    source: str
    distance_note: str = ""


# ---- Market price intelligence tool (Tier 2) ------------------------------


class PriceIntelligenceInput(BaseModel):
    crop: str


class HistoricalPricePoint(BaseModel):
    months_ago: int
    price: float


class PriceIntelligenceOutput(BaseModel):
    crop: str
    unit: str
    currency: str
    current_price: float
    price_source: str
    historical_prices: list[HistoricalPricePoint]
    recommendation: str  # "sell_now" | "store_and_wait"
    reasoning: str
    confidence: str


# ---- Plant disease detection from images tool (Tier 2) --------------------


class DiseaseDetectionInput(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image bytes (JPEG/PNG)")
    crop_hint: str | None = Field(default=None, description="Farmer-stated crop, if known")


class DiseaseDetectionOutput(BaseModel):
    crop_guess: str
    disease_name: str
    is_known_in_knowledge_base: bool
    confidence: str  # "low" | "medium" | "high"
    symptoms_observed: str
    prevention: str
    treatment: str
    estimated_cost_bdt: float | None = None
    source: str
    disclaimer: str
