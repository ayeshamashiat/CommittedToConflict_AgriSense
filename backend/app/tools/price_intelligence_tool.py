"""Tier 2: Market price intelligence — current price (real, sourced from the
same crop_reference table the financial calculator uses) plus a sell-now /
store-and-wait recommendation with disclosed reasoning.

What's real: current_price and its source citation (BBS/DAM, same as
finance_calc.py). What's disclosed heuristic, not measured data: the
"historical_prices" trend and the seasonal price-rise assumption behind the
store/wait call — no free historical per-crop wholesale price time series
for Bangladesh was available in the time given, so rather than inventing
specific numbers and presenting them as fact, this generates an explicitly
labeled illustrative seasonal curve (lowest right after harvest, rising
toward the next season) and grounds the recommendation in that disclosed
model plus each crop's real perishability/storability, which IS a genuine
agronomic fact (a tomato spoils in days; rice stores for months).
"""

from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.schemas.tool_io import HistoricalPricePoint, PriceIntelligenceInput, PriceIntelligenceOutput
from app.tools.base import AgriTool
from app.tools.crop_data import DEFAULT_CROP

# Crops that spoil within days to a couple of weeks — for these, spoilage risk
# dominates any potential price gain from waiting, so the call is always
# "sell now" regardless of the seasonal price model.
PERISHABLE_CROPS = {
    "tomato",
    "cabbage",
    "cauliflower",
    "cucumber",
    "pumpkin",
    "bitter_gourd",
    "okra",
    "brinjal",
}

# Illustrative seasonal price index by months-since-harvest, for storable
# crops: prices are typically lowest at harvest (supply glut) and rise as
# stock is drawn down toward the next season. Disclosed heuristic — not a
# measured time series (see module docstring).
SEASONAL_INDEX_BY_MONTH = [1.00, 1.03, 1.07, 1.11, 1.15, 1.18]


class PriceIntelligenceTool(AgriTool):
    name = "price_intelligence"
    description = (
        "Given a crop, returns its current market price (real, sourced), an "
        "illustrative seasonal price trend, and a sell-now vs store-and-wait "
        "recommendation with reasoning. Call this when the farmer asks whether "
        "to sell now or store their harvest."
    )
    input_schema = PriceIntelligenceInput
    output_schema = PriceIntelligenceOutput

    def run(self, input_data: PriceIntelligenceInput) -> PriceIntelligenceOutput:
        crop_key = input_data.crop.strip().lower()
        db = SessionLocal()
        try:
            econ = get_by_name(db, crop_key) or DEFAULT_CROP
        finally:
            db.close()

        current_price = econ.price_per_unit
        n = len(SEASONAL_INDEX_BY_MONTH)
        # SEASONAL_INDEX_BY_MONTH's last entry represents "now" — scale the whole
        # curve so that point lands exactly on the real current_price.
        base = current_price / SEASONAL_INDEX_BY_MONTH[-1] if SEASONAL_INDEX_BY_MONTH[-1] else current_price
        historical = [
            HistoricalPricePoint(months_ago=n - 1 - i, price=round(base * idx, 2))
            for i, idx in enumerate(SEASONAL_INDEX_BY_MONTH)
        ]

        is_perishable = crop_key in PERISHABLE_CROPS
        # Average monthly growth rate implied by the trailing curve, projected
        # forward 3 months from today — same disclosed model, not a new one.
        monthly_growth = (SEASONAL_INDEX_BY_MONTH[-1] / SEASONAL_INDEX_BY_MONTH[0]) ** (1 / (n - 1)) - 1
        projected_3mo_price = round(current_price * (1 + monthly_growth) ** 3, 2)
        projected_gain_percent = round((projected_3mo_price / current_price - 1) * 100, 1) if current_price else 0.0

        if is_perishable:
            recommendation = "sell_now"
            reasoning = (
                f"{crop_key.replace('_', ' ').title()} is highly perishable and cannot be stored — "
                "spoilage risk outweighs any potential price gain, so sell as soon as possible after harvest."
            )
        elif projected_gain_percent >= 8:
            recommendation = "store_and_wait"
            reasoning = (
                f"{crop_key.replace('_', ' ').title()} stores reasonably well. Based on the typical seasonal "
                f"pattern, prices tend to rise roughly {projected_gain_percent:.1f}% over the 3 months after "
                "harvest as post-harvest supply eases — storing (if you have safe, dry storage and can "
                "absorb the wait) may be worth more than selling into the immediate post-harvest glut."
            )
        else:
            recommendation = "sell_now"
            reasoning = (
                f"The typical seasonal price rise for {crop_key.replace('_', ' ')} over the next few months "
                f"(~{projected_gain_percent:.1f}%) is modest — likely not enough to outweigh storage costs, "
                "shrinkage, and price risk, so selling at the current price is the safer call."
            )

        return PriceIntelligenceOutput(
            crop=crop_key,
            unit="kg",
            currency="BDT",
            current_price=current_price,
            price_source=econ.price_source,
            historical_prices=historical,
            recommendation=recommendation,
            reasoning=reasoning,
            confidence=(
                "Current price is sourced (see price_source). The historical trend and seasonal price-rise "
                "estimate are an illustrative, disclosed model, not measured historical data — no free "
                "historical wholesale price series for this crop was available."
            ),
        )
