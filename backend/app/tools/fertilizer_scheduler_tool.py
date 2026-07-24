"""Tier 1: Fertilizer scheduler — splits a crop's total fertilizer dose into
growth-stage applications (quantity, timing, cost), plus an organic alternative.

The per-nutrient split is derived, not re-invented: it reuses the same real
rice dose (180-43-42 kg/ha Urea-TSP-MoP) and the same intensity ratio already
used to estimate each crop's total fertilizer cost in crop_data.py — read
straight from the DB (crop.fertilizer_cost_per_acre / rice's real cost), so
this tool can never drift out of sync with the numbers /calculate returns.

The three-way stage split (basal / early top-dress / late top-dress) and the
organic-alternative suggestion are general, widely-documented agronomic
practice for split fertilizer application — not tied to a specific citable
source, and disclosed as such via data_confidence="mixed".
"""

from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.schemas.tool_io import (
    FertilizerScheduleInput,
    FertilizerScheduleOutput,
    FertilizerStageDose,
)
from app.tools.base import AgriTool
from app.tools.crop_data import (
    DEFAULT_CROP,
    FERTILIZER_PRICE_BDT_PER_KG,
    RICE_FERTILIZER_COST_PER_ACRE,
    RICE_MOP_KG_ACRE,
    RICE_TSP_KG_ACRE,
    RICE_UREA_KG_ACRE,
)

# Fraction of each nutrient applied at each stage. TSP and MoP are almost
# entirely basal (standard practice — phosphorus/potassium don't leach the
# way nitrogen does); urea is commonly split to reduce leaching/volatilization
# loss and match plant uptake through the season.
STAGE_SPLIT = [
    {"stage": "Basal (at land preparation / sowing)", "days_after_sowing": 0, "urea": 0.34, "tsp": 0.9, "mop": 0.5},
    {"stage": "First top-dress (early vegetative)", "days_after_sowing": 20, "urea": 0.33, "tsp": 0.1, "mop": 0.25},
    {"stage": "Second top-dress (tillering / flowering)", "days_after_sowing": 45, "urea": 0.33, "tsp": 0.0, "mop": 0.25},
]

ORGANIC_ALTERNATIVE = (
    "Well-rotted cow dung or compost (~2-3 tons/acre, worked in at land preparation) can "
    "replace part of the basal dose — roughly 1 ton of well-decomposed cow dung supplies "
    "about as much available N as 8-10 kg of urea, plus organic matter that improves soil "
    "structure. It won't fully replace top-dress urea for fast-growing cereals, but it "
    "reduces the chemical fertilizer bill and is worth combining with a reduced urea rate."
)


class FertilizerSchedulerTool(AgriTool):
    name = "fertilizer_scheduler"
    description = (
        "Given a crop and farm size, returns a growth-stage fertilizer schedule "
        "(Urea/TSP/MoP quantity and cost per stage) plus an organic alternative. "
        "Call this after a crop has been chosen, to give the farmer an actionable "
        "application plan rather than just a total cost."
    )
    input_schema = FertilizerScheduleInput
    output_schema = FertilizerScheduleOutput

    def run(self, input_data: FertilizerScheduleInput) -> FertilizerScheduleOutput:
        db = SessionLocal()
        try:
            crop_row = get_by_name(db, input_data.crop) or DEFAULT_CROP
        finally:
            db.close()

        size = input_data.farm_size
        ratio = crop_row.fertilizer_cost_per_acre / RICE_FERTILIZER_COST_PER_ACRE if RICE_FERTILIZER_COST_PER_ACRE else 1.0

        total_urea_kg = RICE_UREA_KG_ACRE * ratio * size
        total_tsp_kg = RICE_TSP_KG_ACRE * ratio * size
        total_mop_kg = RICE_MOP_KG_ACRE * ratio * size

        stages = []
        total_cost = 0.0
        for split in STAGE_SPLIT:
            urea_kg = round(total_urea_kg * split["urea"], 2)
            tsp_kg = round(total_tsp_kg * split["tsp"], 2)
            mop_kg = round(total_mop_kg * split["mop"], 2)
            cost = round(
                urea_kg * FERTILIZER_PRICE_BDT_PER_KG["urea"]
                + tsp_kg * FERTILIZER_PRICE_BDT_PER_KG["tsp"]
                + mop_kg * FERTILIZER_PRICE_BDT_PER_KG["mop"],
                2,
            )
            total_cost += cost
            stages.append(
                FertilizerStageDose(
                    stage=split["stage"],
                    days_after_sowing=split["days_after_sowing"],
                    urea_kg=urea_kg,
                    tsp_kg=tsp_kg,
                    mop_kg=mop_kg,
                    cost_bdt=cost,
                    organic_alternative=ORGANIC_ALTERNATIVE if split["days_after_sowing"] == 0 else "",
                )
            )

        return FertilizerScheduleOutput(
            crop=input_data.crop,
            stages=stages,
            total_cost_bdt=round(total_cost, 2),
            data_confidence=crop_row.cost_confidence,
            notes=(
                "Per-nutrient split derived from rice's real measured dose (180-43-42 kg/ha "
                "Urea-TSP-MoP) scaled by this crop's fertilizer-cost ratio; the 3-stage timing "
                "split is standard agronomic practice, not a crop-specific cited figure."
            ),
        )
