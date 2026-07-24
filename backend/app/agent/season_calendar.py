"""Tier 1: turns a crop's duration into an actual dated calendar (not just
staged text descriptions) — land prep starts today, sowing follows a standard
1-week prep window, fertilizer/pest-check checkpoints are placed at typical
growth-stage offsets, and harvest is duration_days after sowing.

The offsets themselves (7 days prep, first fertilizer at ~20 days, first pest
check at ~25 days) are standard general practice, not crop-specific sourced
figures — only the crop's total duration_days is a sourced number.
"""

from datetime import date, timedelta

PREP_TO_SOWING_DAYS = 7
FERTILIZER_OFFSET_DAYS = 20
PEST_CHECK_OFFSET_DAYS = 25


def compute_stage_dates(duration_days: int, start: date | None = None) -> dict[str, str]:
    today = start or date.today()
    sowing = today + timedelta(days=PREP_TO_SOWING_DAYS)
    return {
        "land_preparation_date": today.isoformat(),
        "sowing_date": sowing.isoformat(),
        "fertilizer_date": (sowing + timedelta(days=FERTILIZER_OFFSET_DAYS)).isoformat(),
        "pest_check_date": (sowing + timedelta(days=PEST_CHECK_OFFSET_DAYS)).isoformat(),
        "harvest_date": (sowing + timedelta(days=duration_days)).isoformat(),
    }
