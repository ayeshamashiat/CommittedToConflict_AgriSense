"""Owned by Member B: wraps the financial calculator behind the AgriTool interface.

Crop economics are read from the crop_references DB table (seeded from
app/tools/crop_data.py at startup) rather than imported as a static dict,
so prices/yields can be updated without a redeploy. Opens its own short-lived
session per call, the same self-contained pattern WeatherTool uses for its
httpx client.
"""

from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.schemas.tool_io import FinanceInput, FinanceOutput
from app.tools.base import AgriTool
from app.tools.crop_data import DEFAULT_CROP


class FinanceTool(AgriTool):
    name = "financial_calculator"
    description = (
        "Given a crop, farm size (acres), and budget, computes itemized costs, "
        "expected revenue, profit, ROI, and break-even time. Call this after a "
        "candidate crop has been chosen to ground the recommendation in numbers."
    )
    input_schema = FinanceInput
    output_schema = FinanceOutput

    def run(self, input_data: FinanceInput) -> FinanceOutput:
        db = SessionLocal()
        try:
            econ = get_by_name(db, input_data.crop) or DEFAULT_CROP
        finally:
            db.close()

        size = input_data.farm_size

        seed_cost = econ.seed_cost_per_acre * size
        fertilizer_cost = econ.fertilizer_cost_per_acre * size
        labor_cost = econ.labor_cost_per_acre * size
        water_cost = econ.water_cost_per_acre * size
        total_cost = seed_cost + fertilizer_cost + labor_cost + water_cost

        revenue = econ.yield_per_acre_units * size * econ.price_per_unit
        profit = revenue - total_cost
        roi_percent = (profit / total_cost * 100) if total_cost > 0 else 0.0

        break_even_days = None
        if revenue > 0:
            daily_revenue = revenue / econ.duration_days
            break_even_days = round(total_cost / daily_revenue, 1) if daily_revenue else None

        return FinanceOutput(
            crop=input_data.crop,
            seed_cost=round(seed_cost, 2),
            fertilizer_cost=round(fertilizer_cost, 2),
            labor_cost=round(labor_cost, 2),
            water_cost=round(water_cost, 2),
            total_cost=round(total_cost, 2),
            revenue=round(revenue, 2),
            profit=round(profit, 2),
            roi_percent=round(roi_percent, 2),
            break_even_days=break_even_days,
            within_budget=total_cost <= input_data.budget,
            data_confidence=econ.cost_confidence,
            yield_source=econ.yield_source,
            price_source=econ.price_source,
            notes=econ.notes,
        )
