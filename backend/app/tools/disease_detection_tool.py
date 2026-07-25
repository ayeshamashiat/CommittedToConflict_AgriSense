"""Tier 2: Plant disease detection from images.

Unlike every other tool in this app, this one has no deterministic/offline
fallback — real image classification requires a vision-capable model, and
there's no local vision model in this stack. When no LLM key is configured,
this returns a clear "unavailable" result rather than faking a diagnosis; a
wrong or invented disease call could cost a farmer real money on the wrong
treatment, so silence is safer than a guess dressed up as an answer.

When a diagnosis IS made, the disease name is cross-referenced against this
app's own pest_knowledge.py — if it matches a known entry, the prevention/
treatment/cost shown come from that already-reviewed knowledge base (the
same one pest_risk_tool.py uses) instead of from the vision model's own
suggestion, which is exactly the "grounded in retrieval, not model recall"
principle used everywhere else in this app applied to a new input modality.
"""

from app.data.pest_knowledge import DEFAULT_PEST_RISKS, PEST_KNOWLEDGE
from app.llm.client import LLMClient
from app.schemas.tool_io import DiseaseDetectionInput, DiseaseDetectionOutput
from app.tools.base import AgriTool

_BASE_SYSTEM_PROMPT = (
    "You are an agricultural plant pathologist examining a photo of a crop leaf/plant sent by a "
    "Bangladeshi smallholder farmer. Identify: (1) your best guess at the crop, (2) the specific "
    "pest or disease you observe (or 'healthy' / 'unclear' if you can't tell), (3) your confidence "
    "('low'/'medium'/'high'), (4) the visible symptoms that led to your call, (5) a prevention "
    "recommendation, (6) a treatment recommendation. Be honest about uncertainty — if the image is "
    "blurry, poorly lit, or doesn't clearly show a diagnosable symptom, say so and set confidence to "
    "'low' rather than guessing confidently. Respond as a JSON object with keys: crop_guess, "
    "disease_name, confidence, symptoms_observed, prevention, treatment."
)


def _known_candidates_prompt(crop_hint: str | None) -> str:
    """Appends the specific diseases/pests AgriSense's own knowledge base
    already documents for this crop (with their distinguishing symptoms) to
    the vision prompt — grounding the model's guess in reviewed IPM data
    instead of leaving it to guess blind and name whatever it recalls.
    Without this, a real farmer photo of cucurbit downy mildew was misread as
    generic 'Fungal Leaf Spot' by the model's own untethered judgment, purely
    because the knowledge base had no entries for it to be grounded against
    at all (that gap is now fixed in pest_knowledge.py) — but even with the
    gap fixed, an image call with no candidate list still has to recall the
    right name from scratch. Listing the actual candidates + how to tell them
    apart directly targets that failure mode."""
    if not crop_hint:
        return ""
    # crop_hint comes straight from a free-text form field pre-filled with the
    # display-cased crop name ("Bitter Gourd"), but PEST_KNOWLEDGE's keys are
    # the internal snake_case crop_name ("bitter_gourd") — an exact-match
    # lookup with no normalization silently found nothing here, which is
    # exactly why the first fix (candidate list + symptom notes) never
    # actually reached the prompt for a real "Bitter Gourd" submission.
    normalized = crop_hint.strip().lower().replace(" ", "_").replace("-", "_")
    entries = PEST_KNOWLEDGE.get(normalized)
    if not entries:
        return ""
    lines = []
    for entry in entries:
        symptoms = entry.get("symptom_notes")
        if symptoms:
            lines.append(f"- {entry['name']}: {symptoms}")
        else:
            lines.append(f"- {entry['name']}")
    if not lines:
        return ""
    return (
        "\n\nAgriSense's own knowledge base documents these specific pests/diseases for this crop, "
        "each with the symptoms that distinguish it from the others:\n"
        + "\n".join(lines)
        + "\nIf what you see in the photo genuinely matches one of these, use that exact name. If it "
        "clearly doesn't match any of them, say so and name what you actually observe instead — do not "
        "force a match that isn't a good fit."
    )


def _find_known_entry(disease_name: str) -> dict | None:
    """Case-insensitive substring match against every crop's pest_knowledge
    entries — if the vision model's disease name matches one we already have
    reviewed prevention/treatment/cost data for, use that instead of the
    model's own suggestion."""
    needle = (disease_name or "").strip().lower()
    if not needle:
        return None
    for entries in list(PEST_KNOWLEDGE.values()) + [DEFAULT_PEST_RISKS]:
        for entry in entries:
            name = entry["name"].lower()
            if needle in name or name in needle:
                return entry
    return None


class DiseaseDetectionTool(AgriTool):
    name = "disease_detection"
    description = (
        "Given a photo of a crop leaf/plant, identifies likely pest/disease with prevention, "
        "treatment, and estimated cost. Requires a vision-capable LLM — has no offline fallback."
    )
    input_schema = DiseaseDetectionInput
    output_schema = DiseaseDetectionOutput

    def __init__(self, llm: LLMClient | None = None):
        self._llm = llm or LLMClient()

    def run(self, input_data: DiseaseDetectionInput) -> DiseaseDetectionOutput:
        if not self._llm.available:
            return DiseaseDetectionOutput(
                crop_guess=input_data.crop_hint or "unknown",
                disease_name="unavailable",
                is_known_in_knowledge_base=False,
                confidence="low",
                symptoms_observed="",
                prevention="",
                treatment="",
                source="none",
                disclaimer=(
                    "Image-based disease detection requires a vision-capable LLM (OpenAI API key), "
                    "which is not configured on this server right now. This is the one feature in "
                    "AgriSense that has no offline fallback, since a real diagnosis needs a real "
                    "vision model — please try again once an API key is configured."
                ),
            )

        user_prompt = "Analyze this plant photo."
        if input_data.crop_hint:
            user_prompt += f" The farmer says the crop is: {input_data.crop_hint}."

        system_prompt = _BASE_SYSTEM_PROMPT + _known_candidates_prompt(input_data.crop_hint)
        result = self._llm.classify_image_json(system_prompt, user_prompt, input_data.image_base64)
        if not result:
            return DiseaseDetectionOutput(
                crop_guess=input_data.crop_hint or "unknown",
                disease_name="unavailable",
                is_known_in_knowledge_base=False,
                confidence="low",
                symptoms_observed="",
                prevention="",
                treatment="",
                source="none",
                disclaimer="The vision model call failed or returned an unusable response — please try again.",
            )

        disease_name = str(result.get("disease_name", "unclear")).strip() or "unclear"
        known = _find_known_entry(disease_name)

        if known:
            return DiseaseDetectionOutput(
                crop_guess=str(result.get("crop_guess", input_data.crop_hint or "unknown")),
                disease_name=known["name"],
                is_known_in_knowledge_base=True,
                confidence=str(result.get("confidence", "medium")),
                symptoms_observed=str(result.get("symptoms_observed", "")),
                prevention=known["prevention"],
                treatment=known["treatment"],
                estimated_cost_bdt=known["estimated_cost_bdt_per_acre"],
                source="Matched against AgriSense's own IPM knowledge base (same source pest_risk_assessor uses).",
                disclaimer=(
                    "Crop/disease identification is from an AI vision model and may be wrong, "
                    "especially for unclear or low-quality photos — confirm with a local agricultural "
                    "extension officer before spending on treatment. Prevention/treatment/cost below "
                    "are from AgriSense's own reviewed knowledge base, not the vision model's opinion."
                ),
            )

        return DiseaseDetectionOutput(
            crop_guess=str(result.get("crop_guess", input_data.crop_hint or "unknown")),
            disease_name=disease_name,
            is_known_in_knowledge_base=False,
            confidence=str(result.get("confidence", "medium")),
            symptoms_observed=str(result.get("symptoms_observed", "")),
            prevention=str(result.get("prevention", "")),
            treatment=str(result.get("treatment", "")),
            estimated_cost_bdt=None,
            source="AI vision model's own assessment — not cross-referenced against AgriSense's knowledge base.",
            disclaimer=(
                "This diagnosis and its prevention/treatment suggestions come directly from an AI "
                "vision model, not a verified knowledge base — they are NOT independently confirmed. "
                "Treat this as a starting point, not a final diagnosis; confirm with a local "
                "agricultural extension officer before spending money on treatment."
            ),
        )
