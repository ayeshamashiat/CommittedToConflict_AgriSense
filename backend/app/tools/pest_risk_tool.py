"""Tier 1: Pest & disease risk — cross-references a crop's known pest/disease
list against the *actual* weather values already fetched for this farm, so
"blast risk" is only flagged when today's humidity genuinely supports it,
not as a static per-crop label. See app/data/pest_knowledge.py for sourcing
notes.
"""

from app.data.pest_knowledge import DEFAULT_PEST_RISKS, PEST_KNOWLEDGE
from app.schemas.tool_io import PestRiskInput, PestRiskItem, PestRiskOutput
from app.tools.base import AgriTool


def _matches(entry: dict, weather: PestRiskInput) -> bool:
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


def _trigger_reason(entry: dict, weather: PestRiskInput) -> str:
    parts = []
    if "min_humidity" in entry:
        parts.append(f"humidity {weather.humidity}% (>= {entry['min_humidity']}%)")
    if "temp_min" in entry or "temp_max" in entry:
        lo = entry.get("temp_min", "-")
        hi = entry.get("temp_max", "-")
        parts.append(f"temperature {weather.temperature}C (in {lo}-{hi}C range)")
    if "min_rainfall" in entry:
        parts.append(f"rainfall {weather.rainfall}mm (>= {entry['min_rainfall']}mm)")
    if "max_rainfall" in entry:
        parts.append(f"low rainfall {weather.rainfall}mm (<= {entry['max_rainfall']}mm, dry-favoring pest)")
    return "Triggered by current conditions: " + "; ".join(parts) if parts else "General seasonal risk."


class PestRiskTool(AgriTool):
    name = "pest_risk_assessor"
    description = (
        "Given a crop and the current weather (temperature, humidity, rainfall), "
        "returns likely pest/disease risks with prevention, treatment, and "
        "estimated cost. Call this after weather has been fetched for the farm."
    )
    input_schema = PestRiskInput
    output_schema = PestRiskOutput

    def run(self, input_data: PestRiskInput) -> PestRiskOutput:
        candidates = PEST_KNOWLEDGE.get(input_data.crop.strip().lower(), DEFAULT_PEST_RISKS)

        risks = []
        for entry in candidates:
            if not _matches(entry, input_data):
                continue
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
                    trigger_reason=_trigger_reason(entry, input_data),
                    prevention=entry["prevention"],
                    treatment=entry["treatment"],
                    estimated_cost_bdt=entry["estimated_cost_bdt_per_acre"],
                )
            )

        if not risks:
            risks.append(
                PestRiskItem(
                    name="No elevated risk under current conditions",
                    kind="disease",
                    risk_level="Low",
                    trigger_reason=(
                        f"Current weather (temp {input_data.temperature}C, humidity "
                        f"{input_data.humidity}%, rainfall {input_data.rainfall}mm) does not "
                        "meet the trigger thresholds for this crop's common pests/diseases."
                    ),
                    prevention="Continue routine field scouting — conditions can change with the forecast.",
                    treatment="No action needed right now.",
                    estimated_cost_bdt=0,
                )
            )

        return PestRiskOutput(
            crop=input_data.crop,
            risks=risks[:3],
            source=(
                "Standard IPM (Integrated Pest Management) knowledge for this crop; trigger "
                "conditions evaluated against this farm's actual fetched weather, not assumed."
            ),
        )
