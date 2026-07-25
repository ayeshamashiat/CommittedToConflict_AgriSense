"""Handles turns that are plain conversation, not a crop-recommendation request
— greetings, "thanks", or a general question like "what is Rabi season?" once the
agent already has a season plan for this session. Without this, agent/core.py
would re-run the full recommendation pipeline on every single message (including
"hi"), which is why the chat used to feel rigid: every reply forced itself back
into "here's your crop recommendation" regardless of what was actually asked.
"""

from app.agent.i18n import (
    CHAT_FALLBACK_BN,
    FIELD_LOOKUP_LABELS_BN,
    GREETING_REPLY_BN_NO_CROP,
    GREETING_REPLY_BN_WITH_CROP,
    LLM_BN_INSTRUCTION,
)
from app.db.models import FarmProfile
from app.llm.client import LLMClient

_GREETING_WORDS = {"hi", "hello", "hey", "yo", "assalamu", "salam", "morning", "evening"}
_THANKS_WORDS = {"thanks", "thank", "thx", "ok", "okay", "great", "cool", "nice"}


def is_greeting_or_thanks(message: str) -> bool:
    words = set((message or "").lower().strip(" !.,?").split())
    return bool(words & _GREETING_WORDS) or bool(words & _THANKS_WORDS)


# Deterministic fallback for "what is my <field>" style lookups when no LLM is
# configured — Tier 0 requires the agent to keep working without an API key,
# and a farmer asking to recall a fact they already gave shouldn't need one.
_FIELD_LOOKUP = {
    "farm_size": ("farm size", lambda p: f"{p.farm_size} acres" if p.farm_size is not None else None),
    "location": ("location", lambda p: p.location),
    "soil_type": ("soil type", lambda p: p.soil_type),
    "water_availability": ("water availability", lambda p: p.water_availability),
    "budget": ("budget", lambda p: f"৳{p.budget:,.0f}" if p.budget is not None else None),
    "target_season": ("season", lambda p: p.target_season),
}
_FIELD_KEYWORDS = {
    "farm_size": ("farm size", "acreage", "how many acres", "how much land"),
    "location": ("my location", "where is my farm", "where's my farm"),
    "soil_type": ("soil type", "my soil"),
    "water_availability": ("water availability", "my water"),
    "budget": ("my budget",),
    "target_season": ("my season", "target season"),
}


def _bare_field_lookup(message: str, profile: FarmProfile, language: str = "en") -> str | None:
    low = (message or "").lower()
    for field, keywords in _FIELD_KEYWORDS.items():
        if any(kw in low for kw in keywords):
            label, getter = _FIELD_LOOKUP[field]
            value = getter(profile)
            if value:
                if language == "bn":
                    return f"আপনার {FIELD_LOOKUP_LABELS_BN.get(field, label)} হলো {value}।"
                return f"Your {label} is {value}."
    return None


# Tier 2: marketplace/supplier lookup — "where can I buy urea" style
# messages. Deterministic (no LLM needed) since it's just relaying real
# numbers from marketplace_tool.py's output, consistent with this project's
# rule that the LLM writes text but never numbers.
_ITEM_KEYWORDS = {
    "urea": ("urea",),
    "tsp": ("tsp",),
    "mop": ("mop", "potash"),
    "pesticide": ("pesticide", "insecticide", "fungicide", "pest spray"),
    "seed": ("seed", "seeds"),
}
_BUY_INTENT_KEYWORDS = (
    "buy",
    "purchase",
    "supplier",
    "suppliers",
    "vendor",
    "dealer",
    "where can i",
    "where to buy",
    "where do i",
    "compare price",
    "cheapest",
    "market for",
    "price of",
)


def detect_marketplace_request(message: str) -> str | None:
    """Returns the item ('urea'/'tsp'/'mop'/'pesticide'/'seed') a message is
    asking to buy/compare, or None if it isn't a marketplace-shaped request."""
    low = (message or "").lower()
    if not any(kw in low for kw in _BUY_INTENT_KEYWORDS):
        return None
    for item, keywords in _ITEM_KEYWORDS.items():
        if any(kw in low for kw in keywords):
            return item
    return None


def compose_marketplace_reply(offers_output: dict, item: str, language: str = "en") -> str:
    offers = offers_output.get("offers", [])
    if not offers:
        if language == "bn":
            return f"এই মুহূর্তে {item}-এর জন্য কোনো তালিকাভুক্ত সরবরাহকারী পাওয়া যায়নি।"
        return f"I couldn't find any catalogued suppliers for {item} right now."
    top = offers[0]
    unit = offers_output.get("unit", "unit")
    if language == "bn":
        summary = (
            f"{item}-এর জন্য সেরা মিল: {top['supplier_name']} ({top['district']}) — "
            f"৳{top['price_per_unit']:.2f}/{unit}, {top['delivery_days']} দিনে ডেলিভারি, "
            f"{top['distance_km']:.0f}কিমি দূরে, রেটিং {top['rating']}/৫।"
        )
        if len(offers) > 1:
            summary += f" (আরও {len(offers) - 1}টি বিকল্প নিচে দেখুন।)"
        return summary
    summary = (
        f"Top match for {item}: {top['supplier_name']} ({top['district']}) at "
        f"৳{top['price_per_unit']:.2f}/{unit}, {top['delivery_days']}-day delivery, "
        f"{top['distance_km']:.0f}km away, rated {top['rating']}/5."
    )
    if len(offers) > 1:
        summary += f" ({len(offers) - 1} more option(s) below.)"
    return summary


# Tier 2: market price intelligence — "should I sell my rice now?" style
# messages. Deterministic keyword check (crop-name resolution happens in
# core.py, which has DB access to match against known crop names and to fall
# back to the session's last-recommended crop).
_SELL_INTENT_KEYWORDS = (
    "sell now",
    "sell my",
    "should i sell",
    "should i store",
    "store or sell",
    "sell or store",
    "wait to sell",
    "market price",
    "current price",
    "what's the price",
    "what is the price",
    "price of",
)


def is_price_query(message: str) -> bool:
    low = (message or "").lower()
    return any(kw in low for kw in _SELL_INTENT_KEYWORDS)


def compose_price_reply(output: dict, language: str = "en") -> str:
    crop_display = output["crop"].replace("_", " ")
    price = output["current_price"]
    unit = output["unit"]
    if language == "bn":
        rec = "মজুদ করে রাখুন" if output["recommendation"] == "store_and_wait" else "এখনই বিক্রি করুন"
        return (
            f"{crop_display}-এর বর্তমান দাম প্রায় ৳{price:.2f}/{unit}। সুপারিশ: {rec}। {output['reasoning']}"
        )
    rec = "Store & Wait" if output["recommendation"] == "store_and_wait" else "Sell Now"
    return f"{crop_display.title()}'s current price is about ৳{price:.2f}/{unit}. Recommendation: {rec}. {output['reasoning']}"


def compose(
    llm: LLMClient,
    profile: FarmProfile,
    rag_passages: list[str],
    message: str,
    last_crop: str | None,
    language: str = "en",
) -> str:
    """Returns a short, natural reply. Grounded in rag_passages when they're
    relevant, but never forced into a crop pitch the farmer didn't ask for."""
    if llm.available:
        system = (
            "You are AgriSense, a friendly Bangladeshi farm advisory chatbot already mid-conversation "
            "with a farmer whose profile you know. Reply to their latest message directly and "
            "conversationally, in 1-4 short sentences — like a knowledgeable extension officer texting "
            "back, not a form letter. Only bring up crop recommendations if they actually asked about "
            "crops, planting, or their season plan; otherwise just answer what they asked. Use the "
            "reference notes if they're relevant to the question, but don't force them in otherwise. "
            "If the farmer asks about a specific fact you already have (their farm size, budget, "
            "location, soil, water availability, or season), answer directly from the profile given "
            "below — never say you don't have it if it's listed there."
        )
        if language == "bn":
            system += LLM_BN_INSTRUCTION
        notes = "\n".join(f"- {p}" for p in rag_passages) or "(no reference notes retrieved)"
        # Every known profile field goes in here — a farmer asking "what is my
        # farm size" or "what's my budget" needs the LLM to actually have that
        # number, not just location/soil/water/season. Omitting a field here
        # previously made the LLM (correctly, per its "don't invent facts"
        # instruction) claim it didn't know a fact that was sitting right in
        # the database — this is what fed that wrong answer, not a save failure.
        profile_bits = ", ".join(
            f"{label}={value}"
            for label, value in [
                ("location", profile.location),
                ("farm size (acres)", profile.farm_size),
                ("soil", profile.soil_type),
                ("water availability", profile.water_availability),
                ("budget (BDT)", profile.budget),
                ("season", profile.target_season),
            ]
            if value is not None and value != ""
        )
        user = (
            f"Farmer profile: {profile_bits or 'not fully known yet'}"
            + (f"\nMost recently recommended crop: {last_crop.replace('_', ' ').title()}" if last_crop else "")
            + f"\n\nReference notes:\n{notes}\n\nFarmer's message: {message!r}\n\nReply naturally now."
        )
        reply = llm.complete(system, user, temperature=0.5, max_tokens=220)
        if reply:
            return reply.strip()

    field_answer = _bare_field_lookup(message, profile, language)
    if field_answer:
        return field_answer

    if is_greeting_or_thanks(message):
        if language == "bn":
            if last_crop:
                return GREETING_REPLY_BN_WITH_CROP.format(crop=last_crop.replace("_", " ").title())
            return GREETING_REPLY_BN_NO_CROP
        if last_crop:
            return (
                f"Hey! Still here — your last recommendation was {last_crop.replace('_', ' ').title()}. "
                "Ask me anything about it, or let me know if anything's changed on your farm."
            )
        return "Hi there! Ask me anything, or tell me about your farm and I'll put together a plan."

    if rag_passages:
        return rag_passages[0]

    return CHAT_FALLBACK_BN if language == "bn" else "Could you tell me a bit more about what you'd like to know?"
