"""Tier 1: Scenario simulation — "what if rainfall drops 30%?" / "what if my
budget is cut 40%?" — returns a genuinely revised financial projection, not a
generic answer.

Budget changes are a direct, exact recomputation (no heuristic needed — the
same real cost/yield/price figures, just a different budget to compare
against). Rainfall changes require a yield-sensitivity assumption that isn't
in any of our sourced data, so it's an explicit, disclosed heuristic: yield
loss scales with how rainfall-dependent the crop is (its water_need
category), not a single universal multiplier. This is intentionally
transparent in the output rather than presented as measured fact.
"""

from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.schemas.tool_io import FinanceOutput, ScenarioSimulationInput, ScenarioSimulationOutput
from app.tools.base import AgriTool
from app.tools.crop_data import DEFAULT_CROP
from app.tools.finance_calc import compute_finance

# Fractional yield impact per 100% rainfall change, by water-need category —
# thirstier crops are hit harder by a rainfall shortfall. Disclosed heuristic,
# not a sourced figure (see module docstring).
RAINFALL_SENSITIVITY = {"low": 0.15, "medium": 0.35, "high": 0.6}


def _rainfall_yield_multiplier(water_need: str, pct_change: float) -> float:
    sensitivity = RAINFALL_SENSITIVITY.get(water_need, 0.35)
    multiplier = 1 + sensitivity * (pct_change / 100)
    return max(0.2, min(1.3, multiplier))


class ScenarioSimulatorTool(AgriTool):
    name = "scenario_simulator"
    description = (
        "Given a crop and a hypothetical change in rainfall and/or budget, "
        "returns both the original and revised financial projection so the "
        "farmer can see exactly what changes. Call this when the farmer asks "
        "a 'what if' question."
    )
    input_schema = ScenarioSimulationInput
    output_schema = ScenarioSimulationOutput

    def run(self, input_data: ScenarioSimulationInput) -> ScenarioSimulationOutput:
        db = SessionLocal()
        try:
            econ = get_by_name(db, input_data.crop) or DEFAULT_CROP
        finally:
            db.close()

        original_figures = compute_finance(econ, input_data.farm_size, input_data.budget)
        original = FinanceOutput(
            crop=input_data.crop,
            **original_figures,
            data_confidence=econ.cost_confidence,
            yield_source=econ.yield_source,
            price_source=econ.price_source,
            notes=econ.notes,
        )

        revised_budget = input_data.budget * (1 + input_data.budget_change_percent / 100)
        yield_multiplier = _rainfall_yield_multiplier(econ.water_need, input_data.rainfall_change_percent)
        revised_figures = compute_finance(
            econ, input_data.farm_size, revised_budget, yield_multiplier=yield_multiplier
        )
        revised = FinanceOutput(
            crop=input_data.crop,
            **revised_figures,
            data_confidence="mixed",  # rainfall sensitivity is a heuristic even when cost base is sourced
            yield_source=econ.yield_source,
            price_source=econ.price_source,
            notes="Yield adjusted by a disclosed rainfall-sensitivity heuristic; see 'assumptions'.",
        )

        assumptions = (
            f"Budget adjusted {input_data.budget_change_percent:+.0f}% "
            f"({input_data.budget:,.0f} -> {revised_budget:,.0f} BDT). "
            f"Rainfall adjusted {input_data.rainfall_change_percent:+.0f}%, applied as a "
            f"{(yield_multiplier - 1) * 100:+.1f}% yield change for a '{econ.water_need}' "
            f"water-need crop (sensitivity={RAINFALL_SENSITIVITY.get(econ.water_need, 0.35)}) — "
            "a disclosed estimate, not a measured crop-yield model."
        )

        profit_delta = revised.profit - original.profit
        direction = "up" if profit_delta >= 0 else "down"
        explanation = (
            f"Profit would go {direction} by {abs(profit_delta):,.0f} BDT "
            f"({original.profit:,.0f} -> {revised.profit:,.0f}). "
        )
        if not revised.within_budget:
            max_affordable_acres = round(revised_budget / (original.total_cost / input_data.farm_size), 2) if original.total_cost else 0
            explanation += (
                f"At the revised budget, the full {input_data.farm_size}-acre plan is no longer "
                f"affordable — the farmer could cover about {max_affordable_acres} acres instead."
            )

        return ScenarioSimulationOutput(
            crop=input_data.crop,
            original=original,
            revised=revised,
            assumptions=assumptions,
            explanation=explanation,
        )
