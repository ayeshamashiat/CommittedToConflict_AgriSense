"""Tier 1: Irrigation scheduler — turns a crop's water need and total water
cost (already in crop_data.py) into a concrete event-by-event schedule:
how often to irrigate and what each round costs.

Interval-by-water-need is standard irrigation-scheduling practice (shorter
intervals for thirstier crops), not a crop-specific cited figure — the cost
per event *is* grounded, since it's the same water_cost_per_acre already in
the DB, just divided across the computed number of events.

For long-duration crops (e.g. sugarcane at 330 days), a literal "every 6
days" schedule would produce 50+ line items — not actionable for a farmer to
read. Above MAX_DISPLAY_EVENTS, the schedule collapses to representative
growth-stage checkpoints instead, each carrying an even share of the same
total cost, with a note on the underlying watering frequency.
"""

from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.schemas.tool_io import IrrigationEvent, IrrigationScheduleInput, IrrigationScheduleOutput
from app.tools.base import AgriTool
from app.tools.crop_data import DEFAULT_CROP

# Days between irrigation events, by crop water_need category.
INTERVAL_DAYS = {"low": 15, "medium": 10, "high": 6}

MAX_DISPLAY_EVENTS = 6
STAGE_LABELS = [
    "Establishment irrigation (right after sowing/transplanting)",
    "Early vegetative growth",
    "Active vegetative growth / tillering",
    "Flowering / reproductive stage",
    "Fruit or grain filling",
    "Pre-harvest",
]


class IrrigationSchedulerTool(AgriTool):
    name = "irrigation_scheduler"
    description = (
        "Given a crop, farm size, and the farmer's water availability, returns "
        "an irrigation event schedule (timing and cost per round). Call this "
        "after a crop has been chosen to turn the total water cost into an "
        "actionable calendar."
    )
    input_schema = IrrigationScheduleInput
    output_schema = IrrigationScheduleOutput

    def run(self, input_data: IrrigationScheduleInput) -> IrrigationScheduleOutput:
        db = SessionLocal()
        try:
            crop_row = get_by_name(db, input_data.crop) or DEFAULT_CROP
        finally:
            db.close()

        interval = INTERVAL_DAYS.get(crop_row.water_need, 10)
        raw_event_count = max(1, crop_row.duration_days // interval)
        total_water_cost = round(crop_row.water_cost_per_acre * input_data.farm_size, 2)

        farmer_water = (input_data.water_availability or "").lower()
        constrained = farmer_water == "low" and crop_row.water_need in ("medium", "high")
        constraint_note = (
            f" Your reported water availability is low for this crop's {crop_row.water_need} "
            "water need; consider mulching or drip/furrow irrigation to stretch limited water further."
            if constrained
            else ""
        )

        if raw_event_count <= MAX_DISPLAY_EVENTS:
            display_count = raw_event_count
            step = interval
            frequency_note = ""
        else:
            display_count = MAX_DISPLAY_EVENTS
            step = crop_row.duration_days // display_count
            frequency_note = (
                f" (collapsed from ~{raw_event_count} individual waterings at the recommended "
                f"{interval}-day interval into {display_count} growth-stage checkpoints for readability)"
            )

        cost_per_event = round(total_water_cost / display_count, 2)
        events = []
        for i in range(display_count):
            day = i * step
            label = STAGE_LABELS[i] if i < len(STAGE_LABELS) else f"Round {i + 1} irrigation"
            note = label + (constraint_note if i == 0 else "")
            events.append(IrrigationEvent(stage=label, days_after_sowing=day, note=note, cost_bdt=cost_per_event))

        return IrrigationScheduleOutput(
            crop=input_data.crop,
            events=events,
            total_cost_bdt=total_water_cost,
            notes=(
                f"Recommended watering interval is every {interval} days for a "
                f"'{crop_row.water_need}' water-need crop (standard practice, not a "
                f"crop-specific cited figure){frequency_note}. Total cost is the real "
                "water_cost_per_acre from the financial calculator, split across events shown."
            ),
        )
