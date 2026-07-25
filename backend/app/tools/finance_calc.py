"""Shared financial-projection math, used by both FinanceTool (real crop
economics straight from the DB) and ScenarioSimulatorTool (same math, with a
farmer-requested "what if" adjustment applied on top) — one formula, so the
two can never silently drift apart.
"""


def compute_finance(
    econ,
    farm_size: float,
    budget: float,
    yield_multiplier: float = 1.0,
) -> dict:
    """`econ` is anything with the CropEconomics/CropReference attribute shape
    (seed_cost_per_acre, fertilizer_cost_per_acre, labor_cost_per_acre,
    water_cost_per_acre, yield_per_acre_units, price_per_unit, duration_days)."""
    seed_cost = econ.seed_cost_per_acre * farm_size
    fertilizer_cost = econ.fertilizer_cost_per_acre * farm_size
    labor_cost = econ.labor_cost_per_acre * farm_size
    water_cost = econ.water_cost_per_acre * farm_size
    total_cost = seed_cost + fertilizer_cost + labor_cost + water_cost

    adjusted_yield = econ.yield_per_acre_units * yield_multiplier
    revenue = adjusted_yield * farm_size * econ.price_per_unit
    profit = revenue - total_cost
    roi_percent = (profit / total_cost * 100) if total_cost > 0 else 0.0

    break_even_days = None
    if revenue > 0:
        daily_revenue = revenue / econ.duration_days
        break_even_days = round(total_cost / daily_revenue, 1) if daily_revenue else None

    return {
        "seed_cost": round(seed_cost, 2),
        "fertilizer_cost": round(fertilizer_cost, 2),
        "labor_cost": round(labor_cost, 2),
        "water_cost": round(water_cost, 2),
        "total_cost": round(total_cost, 2),
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "roi_percent": round(roi_percent, 2),
        "break_even_days": break_even_days,
        "within_budget": total_cost <= budget,
    }
