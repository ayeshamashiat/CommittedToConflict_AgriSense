"""Persisted farm profile facts (location, farm size, soil, water, budget, season)
carried across sessions, so the farmer is never asked to repeat themselves."""

from app.db.models import FarmProfile
from app.db.repositories.farm_repo import REQUIRED_FIELDS


def known_facts(profile: FarmProfile | None) -> dict:
    """The subset of REQUIRED_FIELDS already collected, for prompting the LLM
    with what NOT to ask about again."""
    if profile is None:
        return {}
    return {
        field: getattr(profile, field)
        for field in REQUIRED_FIELDS
        if getattr(profile, field) not in (None, "")
    }
