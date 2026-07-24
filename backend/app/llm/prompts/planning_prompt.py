"""Prompt template used by agent/planner.py to decide next action / tool selection.

Two decisions the planner delegates to the LLM (each with a deterministic
fallback in planner.py so the agent still works with no API key):

1. How to phrase the next clarifying question, given what's already known.
2. Which 3 crops (from the crops actually priced in the DB) are worth
   investigating further for this farmer, before spending tool calls on them.
"""


def build_clarifying_question_prompt(
    known_facts: dict, missing_fields: list[str], latest_message: str
) -> tuple[str, str]:
    system = (
        "You are asking a Bangladeshi farmer for the next piece of information you need. "
        "Ask for only ONE missing field at a time, in one short, friendly sentence. "
        "Do not repeat information you already have."
    )
    known_str = ", ".join(f"{k}={v}" for k, v in known_facts.items() if v) or "none yet"
    user = (
        f"Already known: {known_str}\n"
        f"Still missing (ask about the first one only): {missing_fields}\n"
        f"Farmer's latest message: {latest_message!r}\n\n"
        "Write the single next question to ask."
    )
    return system, user


def build_crop_selection_prompt(
    profile: dict, available_crops: list[dict], message: str
) -> tuple[str, str]:
    system = (
        "You select which crops are worth investigating further for a farmer, given their "
        "profile, a list of crops with known soil/water suitability, and their latest message. "
        'Respond with a JSON object of the exact shape {"crops": ["crop_key", "crop_key", '
        '"crop_key"]} — exactly 3 crop_key values, each copied verbatim from the provided list. '
        "IMPORTANT: if the farmer's message names a specific crop they're interested in, that "
        "crop MUST be included as the first entry, even if it isn't the best soil/water match — "
        "the response should directly address what they asked, not silently substitute your own "
        "pick. Fill the remaining slots with crops whose suitable_soils and water_need best "
        "match the farmer's soil_type and water_availability."
    )
    crops_str = "\n".join(
        f"- {c['crop_name']}: soils={c['suitable_soils']}, water_need={c['water_need']}, "
        f"duration_days={c['duration_days']}"
        for c in available_crops
    )
    user = (
        f"Farmer profile: {profile}\n\n"
        f"Farmer's latest message: {message!r}\n\n"
        f"Available crops:\n{crops_str}\n\n"
        "Return the JSON object now."
    )
    return system, user
