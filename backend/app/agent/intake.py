"""Conversational intake: extracts farm-profile facts from a farmer's free-text
chat message — this is what Tier 0 requirement #1 actually means by "from a
vague opening message, the agent collects location, farm size, soil type...".
A structured `profile` object alongside the message is still supported (and
always wins over anything extracted here), but a farmer describing their farm
in one sentence must also work.

LLM-based when available; falls back to a deterministic regex/keyword
extractor so intake still functions without an API key, consistent with the
rest of the agent.
"""

import re

from app.llm.client import LLMClient

FIELD_KEYS = (
    "location",
    "farm_size",
    "farm_size_unit",
    "soil_type",
    "water_availability",
    "budget",
    "target_season",
)

EXTRACTION_SYSTEM_PROMPT = (
    "Extract any farm profile facts the farmer's message states, for these fields only: "
    "location (place name), farm_size (a number), farm_size_unit (one of acre/bigha/katha/"
    "decimal/shotangsho — default 'acre' if a size is given with no unit), soil_type (free "
    "text, e.g. loam/clay/sandy loam), water_availability (low/medium/high), budget (a number, "
    "in BDT), target_season (e.g. Rabi/Kharif/Aus/Aman/Boro/summer/winter). Respond as a JSON "
    "object with ONLY the fields you are confident the message actually states — omit any "
    "field not mentioned. Do not guess or invent values."
)

# The LLM is instructed to "omit any field not mentioned" but doesn't always
# obey that — it sometimes fills every field with a literal placeholder
# string like "not specified" instead of leaving it out. Without filtering
# these, a value like "not specified" would pass the "not None/empty" check,
# get treated as the farmer's real stated farm_size, and crash unit
# conversion (which expects a number) — this is what actually happened.
_LLM_PLACEHOLDER_VALUES = {
    "not specified",
    "unspecified",
    "unknown",
    "n/a",
    "na",
    "none",
    "not mentioned",
    "not stated",
    "not given",
    "not applicable",
    "not provided",
}

SOIL_KEYWORDS = ["sandy loam", "clay loam", "loamy", "loam", "clay", "sandy", "silty", "silt", "peaty", "peat"]
WATER_WORD_TO_VALUE = {"low": "low", "medium": "medium", "med": "medium", "high": "high"}
SEASON_KEYWORDS = ["rabi", "kharif", "aus", "aman", "boro", "summer", "winter", "monsoon", "autumn", "spring"]
_NON_LOCATION_WORDS = set(SOIL_KEYWORDS) | set(SEASON_KEYWORDS) | {"acre", "acres", "acre,"}

# Deliberately narrow: only the wh-word starters that reliably mean "explain
# a concept to me" (e.g. "what is Rabi season?"). Decision/request phrasings
# like "should I plant cabbage in summer" or "can I grow rice with low water"
# are NOT included here — they commonly state a real fact (a season, a crop,
# a soil type) alongside the question, and blocking extraction on them was
# itself a bug: it silently dropped "summer" from a farmer's very first
# message just because it started with "should".
_QUESTION_STARTERS = ("what", "why", "how", "when", "who", "which")


def _looks_like_question(message: str) -> bool:
    """A farmer asking "what is Rabi season?" is not stating a profile fact —
    without this guard, the regex fallback would misread the word "Rabi" in
    that question as the farmer declaring their target season, silently
    overwriting whatever season they'd actually already told us."""
    stripped = (message or "").strip()
    if not stripped:
        return False
    if stripped.endswith("?"):
        return False if any(k in stripped.lower().split() for k in ("should", "can", "could", "would")) else True
    first_word = stripped.lower().split(" ", 1)[0].strip(",.!")
    return first_word in _QUESTION_STARTERS


def _bare_answer_for_expected_field(message: str, expected_field: str | None) -> dict:
    """A short, otherwise-ambiguous reply like "medium", "2", or "60000" only
    means anything in light of which question was just asked. Without this,
    extraction has to guess the field purely from the word's shape with no
    conversation context — which is exactly why farmers were seeing the same
    clarifying question repeat: an LLM call sampled a different guess (or no
    guess) for the identical word "medium" on a later turn. Grounding a bare
    reply in the specific field currently being asked makes this deterministic
    instead of a coin flip."""
    if not expected_field:
        return {}
    stripped = (message or "").strip()
    if not stripped or _looks_like_question(stripped):
        return {}
    low = stripped.lower().strip(" .!")

    if expected_field == "water_availability" and low in WATER_WORD_TO_VALUE:
        return {"water_availability": WATER_WORD_TO_VALUE[low]}

    if expected_field == "farm_size":
        m = re.match(r"^(\d+(?:\.\d+)?)\s*(acre|bigha|katha|decimal|shotangsho)?s?$", low)
        if m:
            return {"farm_size": float(m.group(1)), "farm_size_unit": m.group(2) or "acre"}

    if expected_field == "budget":
        m = re.match(r"^(\d[\d,]*)(?:\s*(?:taka|bdt|tk))?$", low)
        if m:
            return {"budget": float(m.group(1).replace(",", ""))}

    if expected_field == "soil_type":
        for kw in SOIL_KEYWORDS:
            if kw == low or kw in low:
                return {"soil_type": kw}

    if expected_field == "target_season":
        for kw in SEASON_KEYWORDS:
            if kw == low:
                return {"target_season": kw.title()}

    if expected_field == "location" and 1 <= len(stripped.split()) <= 4 and low not in _NON_LOCATION_WORDS:
        return {"location": stripped.title()}

    return {}


def _regex_extract(message: str) -> dict:
    text = message.lower()
    facts: dict = {}

    loc_match = re.search(r"\b(?:in|from|at|near)\s+([A-Za-z][A-Za-z\s]{2,30}?)(?:,|\.| \d|$)", message)
    if loc_match:
        candidate = loc_match.group(1).strip()
        if candidate and candidate.lower() not in _NON_LOCATION_WORDS:
            facts["location"] = candidate.title()

    size_match = re.search(r"(\d+(?:\.\d+)?)\s*(acre|bigha|katha|decimal|shotangsho)s?\b", text)
    if size_match:
        facts["farm_size"] = float(size_match.group(1))
        facts["farm_size_unit"] = size_match.group(2)

    for kw in SOIL_KEYWORDS:
        if kw in text:
            facts["soil_type"] = kw
            break

    water_match = re.search(r"\b(low|medium|med|high)\b\s*water", text) or re.search(
        r"water\s*(?:availability)?[:\s]*\b(low|medium|med|high)\b", text
    )
    if water_match:
        facts["water_availability"] = WATER_WORD_TO_VALUE.get(water_match.group(1), water_match.group(1))

    budget_match = re.search(r"budget[^\d]{0,12}(\d[\d,]*)", text) or re.search(
        r"(\d[\d,]*)\s*(?:taka|bdt|tk)\b", text
    )
    if budget_match:
        facts["budget"] = float(budget_match.group(1).replace(",", ""))

    for kw in SEASON_KEYWORDS:
        if kw in text:
            facts["target_season"] = kw.title()
            break

    return facts


def extract_profile_facts(llm: LLMClient, message: str, expected_field: str | None = None) -> dict:
    """Returns whatever subset of FIELD_KEYS the message seems to state. Facts
    returned here may be applied even to a field the profile already has a
    value for — the farmer correcting or updating a fact in chat ("actually
    my farm is in Dinajpur now") must take effect, not just fill blanks.

    expected_field is the field the agent's last clarifying question asked
    about (or None once the profile is already complete) — used to resolve
    bare one-word answers deterministically before falling back to the
    general-purpose (LLM, then regex) extraction below."""
    if _looks_like_question(message):
        return {}

    bare = _bare_answer_for_expected_field(message, expected_field)
    if bare:
        return bare

    llm_result = llm.complete_json(EXTRACTION_SYSTEM_PROMPT, f"Farmer's message: {message!r}")
    if isinstance(llm_result, dict):
        facts = {
            k: v
            for k, v in llm_result.items()
            if k in FIELD_KEYS and v not in (None, "") and str(v).strip().lower() not in _LLM_PLACEHOLDER_VALUES
        }
        # farm_size/budget must actually be numbers — if the LLM put something
        # non-numeric in a numeric field (whatever the reason), drop just that
        # field rather than letting it crash unit conversion downstream.
        for numeric_field in ("farm_size", "budget"):
            if numeric_field not in facts:
                continue
            try:
                facts[numeric_field] = float(facts[numeric_field])
            except (TypeError, ValueError):
                del facts[numeric_field]
                if numeric_field == "farm_size":
                    facts.pop("farm_size_unit", None)
        if facts:
            return facts

    return _regex_extract(message)
