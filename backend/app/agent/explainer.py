"""Turns combined tool outputs into a justified, explained recommendation.

Numbers (profit, ROI, yield, weather readings) always come straight from the
tool outputs already computed by the executor; the LLM (when available) is
only asked to write suitability/risk labels, reasoning text, a reply, and
season-plan wording — never a number. Falls back to deterministic templating
if no LLM key is configured, or if the LLM's JSON doesn't match the expected
shape.
"""

from app.agent.i18n import DEFAULT_REPLY_TEMPLATE_BN, LLM_BN_INSTRUCTION
from app.db.models import FarmProfile
from app.llm.client import LLMClient
from app.llm.prompts.explanation_prompt import build_explanation_prompt
from app.schemas.chat import CropRecommendation, SeasonPlanOut


def _season_plan_matches_top_crop(sp: dict, top_name: str, all_names: list[str]) -> bool:
    """Best-effort check that the season plan text is actually about the top
    crop, not one of the other candidates. Not foolproof (crop names can be
    absent from short stage sentences entirely), but reliably catches the
    failure mode of the LLM writing every stage about a different crop."""
    combined = " ".join(str(v) for v in sp.values()).lower()
    other_names = [n for n in all_names if n != top_name]
    top_display = top_name.replace("_", " ").lower()

    mentions_top = top_display in combined
    mentions_other = any(n.replace("_", " ").lower() in combined for n in other_names)

    if mentions_other and not mentions_top:
        return False
    return True


def compose(
    llm: LLMClient,
    profile: FarmProfile,
    weather: dict | None,
    per_crop: dict[str, dict],
    message: str,
    language: str = "en",
) -> tuple[list[CropRecommendation], SeasonPlanOut, str]:
    """per_crop: {crop_name: {"rag_passages": [...], "finance": FinanceOutput dict,
    "water_need": str, "duration_days": int, "suitable_soils": list[str]}}"""

    llm_result = _try_llm(llm, profile, weather, per_crop, message, language)
    if llm_result is not None:
        return llm_result

    return _deterministic(profile, weather, per_crop, language)


def _try_llm(
    llm: LLMClient,
    profile: FarmProfile,
    weather: dict | None,
    per_crop: dict[str, dict],
    message: str,
    language: str = "en",
) -> tuple[list[CropRecommendation], SeasonPlanOut, str] | None:
    crop_names = list(per_crop.keys())
    profile_dict = {
        "location": profile.location,
        "farm_size_acres": profile.farm_size,
        "soil_type": profile.soil_type,
        "water_availability": profile.water_availability,
        "budget": profile.budget,
        "target_season": profile.target_season,
    }
    evidence = [
        {
            "crop_name": name,
            "rag_passages": per_crop[name]["rag_passages"],
            "finance_summary": per_crop[name]["finance"],
        }
        for name in crop_names
    ]
    system, user = build_explanation_prompt(profile_dict, weather, evidence, message)
    if language == "bn":
        system += LLM_BN_INSTRUCTION
    result = llm.complete_json(system, user)
    if not result or not isinstance(result.get("crops"), list):
        return None

    by_name = {c.get("crop_name"): c for c in result["crops"] if isinstance(c, dict)}
    if not all(name in by_name for name in crop_names):
        return None

    recommendations = []
    for name in crop_names:
        llm_crop = by_name[name]
        finance = per_crop[name]["finance"]
        recommendations.append(
            CropRecommendation(
                crop_name=name.replace("_", " ").title(),
                suitability=str(llm_crop.get("suitability", "Moderate fit")),
                risk_level=str(llm_crop.get("risk_level", "Medium")),
                water_need=per_crop[name]["water_need"],
                estimated_profit=finance["profit"],
                reasoning=str(llm_crop.get("reasoning", "")).strip()
                or f"{name.title()} matches the reported soil and water conditions.",
            )
        )

    sp = result.get("season_plan")
    top_name = crop_names[0]
    if not isinstance(sp, dict) or not all(
        k in sp for k in ("land_preparation", "sowing", "fertilizer", "irrigation", "pest_checks", "harvest")
    ):
        return None
    if not _season_plan_matches_top_crop(sp, top_name, crop_names):
        # LLM's stage text names a different candidate crop than the labeled top
        # pick (a real failure mode this prompt has hit before) — don't ship an
        # internally inconsistent response, fall back to deterministic wording.
        return None
    season_plan = SeasonPlanOut(
        crop_name=top_name.replace("_", " ").title(),
        land_preparation=str(sp["land_preparation"]),
        sowing=str(sp["sowing"]),
        fertilizer=str(sp["fertilizer"]),
        irrigation=str(sp["irrigation"]),
        pest_checks=str(sp["pest_checks"]),
        harvest=str(sp["harvest"]),
    )

    reply = str(result.get("reply", "")).strip()
    reply_sp_shape = {"reply": reply}  # reuse the same mismatch heuristic for the reply text
    if not reply or not _season_plan_matches_top_crop(reply_sp_shape, top_name, crop_names):
        reply = _default_reply(profile, crop_names, language)
    return recommendations, season_plan, reply


def _deterministic(
    profile: FarmProfile, weather: dict | None, per_crop: dict[str, dict], language: str = "en"
) -> tuple[list[CropRecommendation], SeasonPlanOut, str]:
    recommendations = []
    for name, data in per_crop.items():
        finance = data["finance"]
        soils = data["suitable_soils"]
        soil_match = bool(profile.soil_type) and any(
            profile.soil_type.lower() in s or s in profile.soil_type.lower() for s in soils
        )
        evidence = " ".join(data["rag_passages"][:1])
        weather_note = ""
        if weather:
            weather_note = (
                f" Current conditions show {weather['temperature']}C and "
                f"{weather['humidity']}% humidity, consistent with a "
                f"{data['water_need']}-water crop like this."
            )
        recommendations.append(
            CropRecommendation(
                crop_name=name.replace("_", " ").title(),
                suitability="Good fit" if soil_match else "Moderate fit",
                risk_level="Low" if finance["within_budget"] else "High (over budget)",
                water_need=data["water_need"],
                estimated_profit=finance["profit"],
                reasoning=(evidence + weather_note).strip()
                or f"{name.title()} matches the reported soil and water conditions.",
            )
        )

    top_name = next(iter(per_crop))
    top_data = per_crop[top_name]
    top_display = top_name.replace("_", " ")
    if language == "bn":
        season_plan = SeasonPlanOut(
            crop_name=top_name.replace("_", " ").title(),
            land_preparation=f"{profile.target_season} মৌসুমে বপনের ১-২ সপ্তাহ আগে {top_display}-এর জন্য জমি প্রস্তুত ও সমতল করুন।",
            sowing=f"{profile.target_season} মৌসুমের শুরুতে সুপারিশকৃত বীজের দূরত্ব মেনে {top_display} বপন করুন।",
            fertilizer="বপনের সময় মূল সার প্রয়োগ করুন, তারপর বৃদ্ধির পর্যায়ে টপ-ড্রেসিং করুন।",
            irrigation=f"{profile.water_availability} পানির প্রাপ্যতা অনুযায়ী সেচ দিন, গুরুত্বপূর্ণ বৃদ্ধির পর্যায়গুলোকে অগ্রাধিকার দিন।",
            pest_checks="সাপ্তাহিক পোকামাকড়/রোগ পর্যবেক্ষণ করুন এবং সীমা ছাড়িয়ে গেলে দ্রুত ব্যবস্থা নিন।",
            harvest=f"{top_display} পরিপক্ব হলে, বপনের প্রায় {top_data['duration_days']} দিন পরে ফসল কাটুন।",
        )
    else:
        season_plan = SeasonPlanOut(
            crop_name=top_name.replace("_", " ").title(),
            land_preparation=f"Prepare and level the field for {top_name} 1-2 weeks before {profile.target_season} sowing.",
            sowing=f"Sow {top_name} at the start of the {profile.target_season} season, following recommended seed spacing.",
            fertilizer="Apply basal fertilizer at sowing, then top-dress at the vegetative stage.",
            irrigation=f"Irrigate according to {profile.water_availability} water availability, prioritizing critical growth stages.",
            pest_checks="Scout weekly for pests/disease and treat promptly if thresholds are exceeded.",
            harvest=f"Harvest {top_name} at maturity, roughly {top_data['duration_days']} days after sowing.",
        )

    reply = _default_reply(profile, list(per_crop.keys()), language)
    return recommendations, season_plan, reply


def _default_reply(profile: FarmProfile, crop_names: list[str], language: str = "en") -> str:
    top = crop_names[0].replace("_", " ").title() if crop_names else ""
    if language == "bn":
        return DEFAULT_REPLY_TEMPLATE_BN.format(
            location=profile.location,
            farm_size=profile.farm_size,
            soil_type=profile.soil_type,
            water_availability=profile.water_availability,
            season=profile.target_season,
            count=len(crop_names),
            top=top,
        )
    return (
        f"Based on your {profile.farm_size}-acre farm in {profile.location} with "
        f"{profile.soil_type} soil and {profile.water_availability} water availability, "
        f"here are the top {len(crop_names)} crop recommendations for the "
        f"{profile.target_season} season, along with a season plan and financial summary for "
        f"{top}."
    )
