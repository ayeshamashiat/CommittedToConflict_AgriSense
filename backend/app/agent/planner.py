"""Decides whether info is missing (ask a clarifying question) or which tool(s) to call.

Every LLM-backed decision here has a deterministic fallback, so the agent
produces the same *shape* of answer whether or not an OpenAI key is
configured — the LLM improves phrasing and crop selection, it isn't load
bearing for the agent to function (Tier 0 requirement).
"""

from sqlalchemy.orm import Session as DBSession

from app.agent import chat_responder
from app.agent.i18n import FIELD_PROMPTS_BN, LLM_BN_INSTRUCTION
from app.agent.state import AgentDecision
from app.db.models import FarmProfile
from app.db.repositories.crop_reference_repo import list_all
from app.db.repositories.plan_repo import list_season_plans
from app.llm.client import LLMClient
from app.llm.prompts.planning_prompt import (
    build_clarifying_question_prompt,
    build_crop_selection_prompt,
)
from app.memory.memory_manager import AgentMemory

# Phrases that signal the farmer actually wants a crop recommendation (as
# opposed to a general question or greeting) once their profile is already
# complete and a recommendation has already been given once this session —
# without this, every follow-up message (including "hi") would re-trigger the
# full recommendation pipeline instead of just answering what was asked.
RECOMMEND_INTENT_KEYWORDS = (
    "recommend",
    "suggest",
    "should i plant",
    "should i grow",
    "which crop",
    "what crop",
    "best crop",
    "what should i grow",
    "what should i plant",
    "top crop",
    "another crop",
    "different crop",
    "other crop",
    "other option",
    "alternative crop",
    "change crop",
    "switch crop",
    "season plan",
    "re-plan",
    "replan",
)

FIELD_PROMPTS = {
    "location": "Where is your farm located (district/upazila)?",
    "farm_size": "How large is your farm? (You can answer in acre, bigha, katha, or decimal.)",
    "soil_type": "What is your soil type (e.g. clay, loam, sandy loam)?",
    "water_availability": "How would you describe your water availability (low, medium, high)?",
    "budget": "What is your budget for this season (in BDT)?",
    "target_season": "Which season are you planning for (e.g. Rabi, Kharif)?",
}

WATER_RANK = {"low": 0, "medium": 1, "high": 2}


def decide(
    llm: LLMClient,
    db: DBSession,
    profile: FarmProfile,
    memory: AgentMemory,
    message: str,
    session_id: str,
    profile_updated: bool = False,
    language: str = "en",
) -> AgentDecision:
    if memory.missing_fields:
        question = _ask_missing_field(llm, memory, message, language)
        return AgentDecision(action="ask_clarifying_question", clarifying_question=question)

    rows = list_all(db)
    has_prior_recommendation = bool(list_season_plans(db, session_id))

    # Tier 2: a marketplace lookup ("where can I buy urea") should be answered
    # directly even as the very first message of a session — it doesn't need
    # a crop recommendation first. A 'seed' lookup is the exception since it
    # needs a crop already in context, so that one still falls through to a
    # first recommendation if there isn't one yet.
    marketplace_item = chat_responder.detect_marketplace_request(message)
    if marketplace_item and (marketplace_item != "seed" or has_prior_recommendation):
        return AgentDecision(action="chat_reply")

    # Tier 2: a price/sell question ("should I sell my rice now?") is answered
    # directly too — as long as a crop is named in the message itself, or (if
    # not) there's already a prior recommendation to fall back on for "which
    # crop". Otherwise it falls through to the normal logic below.
    if chat_responder.is_price_query(message) and (_mentioned_crop(message, rows) or has_prior_recommendation):
        return AgentDecision(action="chat_reply")

    # Always run the full pipeline the first time a session has a complete
    # profile, or when the farmer just changed a profile fact via chat (new
    # location/soil/etc materially changes the recommendation). Otherwise,
    # only re-run it if the message actually asks for one — a plain "hi" or
    # a factual question shouldn't force a fresh crop pitch.
    if not has_prior_recommendation or profile_updated or _wants_recommendation(message, rows):
        crops, source = _select_candidate_crops(llm, db, profile, message, rows)
        return AgentDecision(action="recommend", candidate_crops=crops, crop_selection_source=source)

    return AgentDecision(action="chat_reply")


def _wants_recommendation(message: str, rows) -> bool:
    msg = (message or "").lower()
    if any(kw in msg for kw in RECOMMEND_INTENT_KEYWORDS):
        return True
    return _mentioned_crop(message, rows) is not None


def _ask_missing_field(llm: LLMClient, memory: AgentMemory, message: str, language: str = "en") -> str:
    next_field = memory.missing_fields[0]
    system, user = build_clarifying_question_prompt(memory.known_facts, memory.missing_fields, message)
    if language == "bn":
        system += LLM_BN_INSTRUCTION
    llm_question = llm.complete(system, user, max_tokens=60)
    if llm_question:
        return llm_question.strip()
    if language == "bn":
        return FIELD_PROMPTS_BN.get(next_field, f"আপনার {next_field} সম্পর্কে বলবেন কি?")
    return FIELD_PROMPTS.get(next_field, f"Could you share your {next_field}?")


def _select_candidate_crops(
    llm: LLMClient, db: DBSession, profile: FarmProfile, message: str, rows=None
) -> tuple[list[str], str]:
    rows = rows if rows is not None else list_all(db)
    heuristic_order = _rank_by_soil_water(rows, profile.soil_type, profile.water_availability)

    # If the farmer named a specific crop, it must appear in the results even if
    # it isn't the algorithmically "best" soil/water match — otherwise a message
    # like "I want to plant cabbage" gets silently dropped and the chat never
    # actually responds to what was asked. This is enforced in code, not just
    # requested in the LLM prompt, so it holds even without an LLM key.
    mentioned = _mentioned_crop(message, rows)
    if mentioned:
        heuristic_order = [mentioned] + [c for c in heuristic_order if c != mentioned]

    crop_meta = [
        {
            "crop_name": r.crop_name,
            "suitable_soils": r.suitable_soils,
            "water_need": r.water_need,
            "duration_days": r.duration_days,
        }
        for r in rows
    ]
    profile_dict = {
        "location": profile.location,
        "farm_size_acres": profile.farm_size,
        "soil_type": profile.soil_type,
        "water_availability": profile.water_availability,
        "budget": profile.budget,
        "target_season": profile.target_season,
    }
    system, user = build_crop_selection_prompt(profile_dict, crop_meta, message)
    result = llm.complete_json(system, user)

    if result and isinstance(result.get("crops"), list):
        valid_names = {r.crop_name for r in rows}
        chosen = [c for c in result["crops"] if c in valid_names]
        if mentioned and mentioned not in chosen:
            chosen = [mentioned, *chosen]
        if len(chosen) >= 3:
            return chosen[:3], "llm"

    return heuristic_order[:3], "heuristic"


def _mentioned_crop(message: str, rows) -> str | None:
    """Cheap, deterministic keyword match against the 34 known crop names —
    catches "I want to plant cabbage" without needing an LLM call."""
    msg = (message or "").lower()
    for row in rows:
        display = row.crop_name.replace("_", " ")
        if row.crop_name in msg or display in msg:
            return row.crop_name
    return None


def _rank_by_soil_water(rows, soil_type: str | None, water_availability: str) -> list[str]:
    soil_type = (soil_type or "").lower()
    target_water = WATER_RANK.get((water_availability or "").lower(), 1)

    scored = []
    for row in rows:
        soil_match = (
            any(soil_type in s or s in soil_type for s in row.suitable_soils) if soil_type else False
        )
        water_gap = abs(WATER_RANK.get(row.water_need, 1) - target_water)
        scored.append(((0 if soil_match else 1, water_gap), row.crop_name))

    scored.sort(key=lambda x: x[0])
    return [name for _, name in scored]
