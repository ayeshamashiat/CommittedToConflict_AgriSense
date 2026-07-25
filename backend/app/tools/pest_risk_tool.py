"""Tier 1: Pest & disease risk — predicts likely pests/diseases from crop,
growth stage, AND weather, not just crop + a single weather snapshot.

For each of a crop's growth-stage checkpoints (the same 5-stage granularity
irrigation_scheduler_tool uses), this evaluates the crop's known pest/disease
list against the weather actually expected at that point in the season: the
real Open-Meteo forecast day when the stage falls within the 7-day window,
falling back to today's actual conditions (clearly labeled as such) for
later stages the forecast doesn't reach yet. See app/data/pest_knowledge.py
for sourcing notes on the pest list and stage windows themselves.
"""

from app.data.pest_knowledge import ALL_STAGES, DEFAULT_PEST_RISKS, PEST_KNOWLEDGE
from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.schemas.tool_io import ForecastDay, PestRiskInput, PestRiskItem, PestRiskOutput
from app.tools.base import AgriTool
from app.tools.crop_data import DEFAULT_CROP

STAGE_LABELS = {
    "establishment": "Establishment (seedling / early growth)",
    "vegetative": "Vegetative growth / tillering",
    "flowering": "Flowering / reproductive stage",
    "fruiting": "Fruit or grain filling",
    "preharvest": "Pre-harvest / maturity",
}
# Fraction of total crop duration at which each stage begins.
STAGE_DAY_FRACTIONS = {
    "establishment": 0.0,
    "vegetative": 0.2,
    "flowering": 0.5,
    "fruiting": 0.7,
    "preharvest": 0.9,
}


class _StageWeather:
    def __init__(self, temperature: float, humidity: float, rainfall: float, is_forecast: bool):
        self.temperature = temperature
        self.humidity = humidity
        self.rainfall = rainfall
        self.is_forecast = is_forecast


def _weather_for_day(current: PestRiskInput, forecast: list[ForecastDay], day_offset: int) -> _StageWeather:
    if day_offset < len(forecast):
        day = forecast[day_offset]
        humidity = day.humidity_mean if day.humidity_mean is not None else current.humidity
        return _StageWeather(day.temperature_max, humidity, day.precipitation_mm, True)
    # Beyond the 7-day forecast window — extrapolate from today's actual
    # conditions rather than inventing a number, and the trigger_reason below
    # says so explicitly so this is never mistaken for a real forecast.
    return _StageWeather(current.temperature, current.humidity, current.rainfall, False)


def _matches(entry: dict, weather: _StageWeather) -> bool:
    if "min_humidity" in entry and weather.humidity < entry["min_humidity"]:
        return False
    if "max_humidity" in entry and weather.humidity > entry["max_humidity"]:
        return False
    if "temp_min" in entry and weather.temperature < entry["temp_min"]:
        return False
    if "temp_max" in entry and weather.temperature > entry["temp_max"]:
        return False
    if "min_rainfall" in entry and weather.rainfall < entry["min_rainfall"]:
        return False
    if "max_rainfall" in entry and weather.rainfall > entry["max_rainfall"]:
        return False
    return True


def _trigger_reason(entry: dict, weather: _StageWeather, stage: str, day: int) -> str:
    parts = []
    if "min_humidity" in entry:
        parts.append(f"humidity {weather.humidity:.0f}% (>= {entry['min_humidity']}%)")
    if "temp_min" in entry or "temp_max" in entry:
        lo = entry.get("temp_min", "-")
        hi = entry.get("temp_max", "-")
        parts.append(f"temperature {weather.temperature:.1f}C (in {lo}-{hi}C range)")
    if "min_rainfall" in entry:
        parts.append(f"rainfall {weather.rainfall:.1f}mm (>= {entry['min_rainfall']}mm)")
    if "max_rainfall" in entry:
        parts.append(f"low rainfall {weather.rainfall:.1f}mm (<= {entry['max_rainfall']}mm, dry-favoring pest)")
    conditions = "; ".join(parts) if parts else "general seasonal risk"
    basis = (
        f"day {day} forecast"
        if weather.is_forecast
        else f"today's conditions extrapolated to day {day} (beyond the 7-day forecast)"
    )
    return f"At the {STAGE_LABELS[stage]} (~day {day}), using {basis}: {conditions}."


class PestRiskTool(AgriTool):
    name = "pest_risk_assessor"
    description = (
        "Given a crop and current weather (plus its 7-day forecast, if available), "
        "predicts likely pest/disease risks across the crop's growth stages — "
        "establishment, vegetative, flowering, fruiting, pre-harvest — each checked "
        "against the actual (or nearest-available) weather for that point in the "
        "season, with prevention, treatment, and estimated cost. Call this after "
        "weather has been fetched for the farm."
    )
    input_schema = PestRiskInput
    output_schema = PestRiskOutput

    def run(self, input_data: PestRiskInput) -> PestRiskOutput:
        candidates = PEST_KNOWLEDGE.get(input_data.crop.strip().lower(), DEFAULT_PEST_RISKS)

        db = SessionLocal()
        try:
            crop_row = get_by_name(db, input_data.crop) or DEFAULT_CROP
        finally:
            db.close()
        duration_days = crop_row.duration_days or 90

        risks: list[PestRiskItem] = []
        for stage in ALL_STAGES:
            day = round(duration_days * STAGE_DAY_FRACTIONS[stage])
            stage_weather = _weather_for_day(input_data, input_data.forecast, day)

            stage_matches = [
                entry
                for entry in candidates
                if stage in entry.get("applicable_stages", ALL_STAGES) and _matches(entry, stage_weather)
            ]
            # Highest-trigger-count (most specific) match first; cap at 2 per stage
            # so a full-season view stays readable rather than listing everything.
            stage_matches.sort(
                key=lambda e: sum(
                    1
                    for k in ("min_humidity", "max_humidity", "temp_min", "temp_max", "min_rainfall", "max_rainfall")
                    if k in e
                ),
                reverse=True,
            )
            for entry in stage_matches[:2]:
                trigger_count = sum(
                    1
                    for k in ("min_humidity", "max_humidity", "temp_min", "temp_max", "min_rainfall", "max_rainfall")
                    if k in entry
                )
                risk_level = "High" if trigger_count >= 2 else "Medium"
                risks.append(
                    PestRiskItem(
                        name=entry["name"],
                        kind=entry["kind"],
                        risk_level=risk_level,
                        growth_stage=STAGE_LABELS[stage],
                        days_after_sowing=day,
                        trigger_reason=_trigger_reason(entry, stage_weather, stage, day),
                        prevention=entry["prevention"],
                        treatment=entry["treatment"],
                        estimated_cost_bdt=entry["estimated_cost_bdt_per_acre"],
                    )
                )

        if not risks:
            risks.append(
                PestRiskItem(
                    name="No elevated risk under current/forecast conditions",
                    kind="disease",
                    risk_level="Low",
                    growth_stage=STAGE_LABELS["establishment"],
                    days_after_sowing=0,
                    trigger_reason=(
                        f"Current weather (temp {input_data.temperature}C, humidity "
                        f"{input_data.humidity}%, rainfall {input_data.rainfall}mm) and the available "
                        "forecast do not meet the trigger thresholds for this crop's common pests/diseases "
                        "at any growth stage checked."
                    ),
                    prevention="Continue routine field scouting — conditions can change with the forecast.",
                    treatment="No action needed right now.",
                    estimated_cost_bdt=0,
                )
            )

        return PestRiskOutput(
            crop=input_data.crop,
            risks=risks,
            source=(
                "Standard IPM (Integrated Pest Management) knowledge for this crop and growth stage; "
                "trigger conditions evaluated against this farm's actual fetched weather and forecast, "
                "not assumed."
            ),
        )
