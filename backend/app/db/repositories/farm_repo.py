"""CRUD for FarmProfile (long-term memory), called by memory/long_term.py."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import FarmProfile
from app.tools.units import to_acres

# Fields the farmer must supply before the agent can call weather/RAG/finance tools.
REQUIRED_FIELDS = (
    "location",
    "farm_size",
    "soil_type",
    "water_availability",
    "budget",
    "target_season",
)

# Everything update_profile() is allowed to write, including farm_size bookkeeping.
SETTABLE_FIELDS = REQUIRED_FIELDS + ("farm_size_unit", "farm_size_original")

# Kept for backwards compatibility with any existing callers/imports.
PROFILE_FIELDS = REQUIRED_FIELDS


def get_profile(db: DBSession, session_id: str) -> FarmProfile | None:
    return (
        db.query(FarmProfile).filter(FarmProfile.session_id == session_id).first()
    )


def get_or_create_profile(db: DBSession, session_id: str) -> FarmProfile:
    profile = get_profile(db, session_id)
    if profile:
        return profile
    profile = FarmProfile(session_id=session_id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: DBSession, session_id: str, fields: dict) -> FarmProfile:
    profile = get_or_create_profile(db, session_id)
    fields = dict(fields)

    if fields.get("farm_size") is not None:
        unit = fields.get("farm_size_unit") or profile.farm_size_unit or "acre"
        fields["farm_size_original"] = fields["farm_size"]
        fields["farm_size_unit"] = unit
        fields["farm_size"] = to_acres(fields["farm_size"], unit)

    for key, value in fields.items():
        if key in SETTABLE_FIELDS and value is not None:
            setattr(profile, key, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def missing_fields(profile: FarmProfile | None) -> list[str]:
    if profile is None:
        return list(REQUIRED_FIELDS)
    return [f for f in REQUIRED_FIELDS if getattr(profile, f) in (None, "")]
