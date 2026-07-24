"""Tier 1: Proactive, weather-triggered advice — watches the real 7-day
forecast just fetched for this farm and adjusts the plan, e.g. "Heavy rain
in 4 days. Delay the nitrogen application by 4 days to cut runoff loss."

Every alert here is derived from the actual WeatherOutput.forecast values for
this farm, not invented — the thresholds (what counts as "heavy rain" or
"heat stress") are standard agronomic rules of thumb, not crop-specific
sourced figures.
"""

from datetime import date, timedelta

HEAVY_RAIN_MM = 15.0
HEAT_STRESS_C = 35.0
LOW_WEEKLY_RAIN_MM = 10.0


def generate_alerts(
    weather: dict | None, stage_dates: dict[str, str], water_need: str
) -> tuple[list[str], dict[str, str]]:
    """Returns (alerts, possibly-adjusted stage_dates) — if heavy rain overlaps
    the planned fertilizer date, that date is actually pushed out, not just
    mentioned in passing."""
    alerts: list[str] = []
    dates = dict(stage_dates)

    forecast = (weather or {}).get("forecast") or []
    if not forecast:
        return alerts, dates

    # On a brand-new plan, land prep starts today and sowing follows in ~1
    # week — that's the only stage that actually falls inside a 7-day
    # forecast window (fertilizer/pest checkpoints are weeks further out).
    # This is the alert that's realistically reachable on a first-time plan;
    # the fertilizer-delay check below still applies whenever a returning
    # farmer's fertilizer date happens to land within the current forecast.
    sowing_date_str = dates.get("sowing_date")
    if sowing_date_str:
        sowing_date = date.fromisoformat(sowing_date_str)
        for day in forecast:
            day_date = date.fromisoformat(day["date"])
            if day_date <= sowing_date and day["precipitation_mm"] >= HEAVY_RAIN_MM:
                days_until = (day_date - date.today()).days
                delay = 3
                new_land_prep = date.today() + timedelta(days=delay) if day_date <= date.today() + timedelta(days=2) else None
                new_sowing = sowing_date + timedelta(days=delay)
                dates["sowing_date"] = new_sowing.isoformat()
                if new_land_prep:
                    dates["land_preparation_date"] = new_land_prep.isoformat()
                alerts.append(
                    f"Heavy rain ({day['precipitation_mm']}mm) forecast in {max(days_until, 0)} "
                    f"day(s) on {day['date']}. Delayed land preparation/sowing by {delay} days to "
                    "avoid working wet, compacted soil."
                )
                break

    fert_date_str = dates.get("fertilizer_date")
    if fert_date_str:
        fert_date = date.fromisoformat(fert_date_str)
        for day in forecast:
            day_date = date.fromisoformat(day["date"])
            days_until = (day_date - date.today()).days
            if abs((day_date - fert_date).days) <= 2 and day["precipitation_mm"] >= HEAVY_RAIN_MM:
                new_fert_date = fert_date + timedelta(days=4)
                dates["fertilizer_date"] = new_fert_date.isoformat()
                alerts.append(
                    f"Heavy rain ({day['precipitation_mm']}mm) forecast in {max(days_until, 0)} "
                    f"day(s) on {day['date']}. Delayed the fertilizer application from "
                    f"{fert_date.isoformat()} to {new_fert_date.isoformat()} to cut runoff loss."
                )
                break

    total_rain_7d = round(sum(d["precipitation_mm"] for d in forecast[:7]), 1)
    if water_need in ("medium", "high") and total_rain_7d < LOW_WEEKLY_RAIN_MM:
        alerts.append(
            f"Only {total_rain_7d}mm of rain forecast over the next 7 days — this crop needs "
            f"{water_need} water, so plan manual irrigation to maintain soil moisture."
        )

    hot_days = [d for d in forecast[:3] if d["temperature_max"] >= HEAT_STRESS_C]
    if hot_days:
        peak = max(d["temperature_max"] for d in hot_days)
        alerts.append(
            f"High temperatures (up to {peak}C) forecast in the next 3 days — monitor for "
            "heat stress and consider extra irrigation to cool the root zone."
        )

    return alerts, dates
