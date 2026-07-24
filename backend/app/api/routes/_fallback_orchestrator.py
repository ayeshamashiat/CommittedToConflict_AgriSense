"""Temporary rule-based stand-in for app/agent/core.AgentOrchestrator (Member A).

Used by POST /chat only when the real agent hasn't been wired up yet, so the
endpoint - and the rest of the pipeline (weather, RAG, finance, logging,
history) - is testable end-to-end. Once app/agent/core.py implements
AgentOrchestrator, api/deps.get_agent() picks it up automatically and this
file stops being used; it can then be deleted.
"""

import time

from sqlalchemy.orm import Session as DBSession

from app.db.repositories.crop_reference_repo import get_by_name, list_all
from app.db.repositories.farm_repo import missing_fields as compute_missing_fields
from app.db.repositories.plan_repo import save_financial_projection, save_season_plan
from app.db.repositories.tool_log_repo import log_tool_call
from app.db.models import FarmProfile
from app.schemas.chat import CropRecommendation, SeasonPlanOut, ToolTraceEntry
from app.schemas.tool_io import FinanceInput, RAGInput, WeatherInput
from app.tools.crop_data import DEFAULT_CROP
from app.tools.finance_tool import FinanceTool
from app.tools.rag_tool import RAGTool
from app.tools.weather_tool import WeatherTool, WeatherToolError

_weather_tool = WeatherTool()
_rag_tool = RAGTool()
_finance_tool = FinanceTool()

FIELD_PROMPTS = {
    "location": "Where is your farm located (district/upazila)?",
    "farm_size": "How large is your farm, in acres?",
    "soil_type": "What is your soil type (e.g. clay, loam, sandy loam)?",
    "water_availability": "How would you describe your water availability (low, medium, high)?",
    "budget": "What is your budget for this season (in BDT)?",
    "target_season": "Which season are you planning for (e.g. Rabi, Kharif)?",
}


def _log(db, session_id, tool_name, input_json, output_json, started, status="success", error=None):
    return log_tool_call(
        db,
        session_id=session_id,
        tool_name=tool_name,
        input_json=input_json,
        output_json=output_json,
        status=status,
        error_message=error,
        latency_ms=(time.perf_counter() - started) * 1000,
    )


def _rank_candidate_crops(db: DBSession, soil_type: str | None, water_availability: str) -> list[str]:
    soil_type = (soil_type or "").lower()
    water_rank = {"low": 0, "medium": 1, "high": 2}
    target_water = water_rank.get(water_availability.lower(), 1)

    scored = []
    for row in list_all(db):
        soil_match = any(soil_type in s or s in soil_type for s in row.suitable_soils) if soil_type else False
        water_gap = abs(water_rank.get(row.water_need, 1) - target_water)
        score = (0 if soil_match else 1, water_gap)
        scored.append((score, row.crop_name))

    scored.sort(key=lambda x: x[0])
    return [name for _, name in scored[:3]]


def run_fallback_turn(db: DBSession, session_id: str, profile: FarmProfile) -> dict:
    """Returns a dict matching the non-request fields of ChatResponse."""
    missing = compute_missing_fields(profile)
    trace: list[ToolTraceEntry] = []

    if missing:
        next_field = missing[0]
        reply = (
            "Thanks! To recommend the right crops I still need a bit more info. "
            f"{FIELD_PROMPTS.get(next_field, f'Could you share your {next_field}?')}"
        )
        return {
            "reply": reply,
            "missing_fields": missing,
            "recommendations": None,
            "season_plan": None,
            "financial_summary": None,
            "weather": None,
            "trace": trace,
        }

    # All required fields present: call weather, RAG, and finance tools.
    weather_result = None
    try:
        started = time.perf_counter()
        weather_input = WeatherInput(location=profile.location)
        weather_result = _weather_tool.run(weather_input)
        _log(db, session_id, _weather_tool.name, weather_input.model_dump(), weather_result.model_dump(), started)
        trace.append(ToolTraceEntry(tool_name=_weather_tool.name, input=weather_input.model_dump(), output=weather_result.model_dump()))
    except WeatherToolError as exc:
        started = time.perf_counter()
        _log(db, session_id, _weather_tool.name, {"location": profile.location}, {}, started, status="error", error=str(exc))
        trace.append(ToolTraceEntry(tool_name=_weather_tool.name, input={"location": profile.location}, output={}, status="error"))

    candidate_crops = _rank_candidate_crops(db, profile.soil_type, profile.water_availability)

    recommendations: list[CropRecommendation] = []
    for crop_name in candidate_crops:
        econ = get_by_name(db, crop_name) or DEFAULT_CROP

        started = time.perf_counter()
        rag_input = RAGInput(
            query=f"{crop_name} suitability for {profile.soil_type} soil and {profile.water_availability} water availability",
            n_results=2,
        )
        rag_result = _rag_tool.run(rag_input)
        _log(db, session_id, _rag_tool.name, rag_input.model_dump(), rag_result.model_dump(), started)
        trace.append(ToolTraceEntry(tool_name=_rag_tool.name, input=rag_input.model_dump(), output=rag_result.model_dump()))

        started = time.perf_counter()
        finance_input = FinanceInput(crop=crop_name, farm_size=profile.farm_size, budget=profile.budget)
        finance_result = _finance_tool.run(finance_input)
        _log(db, session_id, _finance_tool.name, finance_input.model_dump(), finance_result.model_dump(), started)
        trace.append(ToolTraceEntry(tool_name=_finance_tool.name, input=finance_input.model_dump(), output=finance_result.model_dump()))
        save_financial_projection(db, session_id, crop_name, finance_result.model_dump())

        evidence = " ".join(rag_result.passages[:1])
        weather_note = ""
        if weather_result:
            weather_note = (
                f" Current conditions show {weather_result.temperature}C and "
                f"{weather_result.humidity}% humidity, consistent with a "
                f"{econ.water_need}-water crop like this."
            )
        reasoning = f"{evidence}{weather_note}".strip()

        recommendations.append(
            CropRecommendation(
                crop_name=crop_name.title(),
                suitability="Good fit" if econ.suitable_soils and profile.soil_type and profile.soil_type.lower() in " ".join(econ.suitable_soils) else "Moderate fit",
                risk_level="Low" if finance_result.within_budget else "High (over budget)",
                water_need=econ.water_need,
                estimated_profit=finance_result.profit,
                reasoning=reasoning or f"{crop_name.title()} matches the reported soil and water conditions.",
            )
        )

    top_crop = candidate_crops[0]
    season_plan_stages = {
        "land_preparation": f"Prepare and level the field for {top_crop} 1-2 weeks before {profile.target_season} sowing.",
        "sowing": f"Sow {top_crop} at the start of the {profile.target_season} season, following recommended seed spacing.",
        "fertilizer": "Apply basal fertilizer at sowing, then top-dress at the vegetative stage.",
        "irrigation": f"Irrigate according to {profile.water_availability} water availability, prioritizing critical growth stages.",
        "pest_checks": "Scout weekly for pests/disease and treat promptly if thresholds are exceeded.",
        "harvest": f"Harvest {top_crop} at maturity, roughly {(get_by_name(db, top_crop) or DEFAULT_CROP).duration_days} days after sowing.",
    }
    save_season_plan(db, session_id, top_crop, season_plan_stages)
    season_plan = SeasonPlanOut(crop_name=top_crop.title(), **season_plan_stages)

    financial_summary = _finance_tool.run(
        FinanceInput(crop=top_crop, farm_size=profile.farm_size, budget=profile.budget)
    )

    reply = (
        f"Based on your {profile.farm_size}-acre farm in {profile.location} with "
        f"{profile.soil_type} soil and {profile.water_availability} water availability, "
        f"here are the top {len(recommendations)} crop recommendations for the "
        f"{profile.target_season} season, along with a season plan and financial summary for "
        f"{top_crop.title()}."
    )

    return {
        "reply": reply,
        "missing_fields": [],
        "recommendations": recommendations,
        "season_plan": season_plan,
        "financial_summary": financial_summary,
        "weather": weather_result,
        "trace": trace,
    }
