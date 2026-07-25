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
from app.tools.finance_calc import compute_finance


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

        figures = compute_finance(econ, input_data.farm_size, input_data.budget)

        return FinanceOutput(
            crop=input_data.crop,
            **figures,
            data_confidence=econ.cost_confidence,
            yield_source=econ.yield_source,
            price_source=econ.price_source,
            notes=econ.notes,
        )
