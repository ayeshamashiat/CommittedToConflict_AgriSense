"""CRUD for CropReference rows, and seeding from app/tools/crop_data.py."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import CropReference


def get_by_name(db: DBSession, crop_name: str) -> CropReference | None:
    return (
        db.query(CropReference)
        .filter(CropReference.crop_name == crop_name.strip().lower())
        .first()
    )


def list_all(db: DBSession) -> list[CropReference]:
    return db.query(CropReference).order_by(CropReference.crop_name).all()


def seed_if_empty(db: DBSession) -> None:
    """Populate crop_references from the sourced data in app/tools/crop_data.py
    the first time the app runs against a fresh database. No-op if rows already
    exist, so re-seeding never clobbers any future admin edits."""
    if db.query(CropReference).first() is not None:
        return

    from app.tools.crop_data import CROP_REFERENCE  # noqa: PLC0415 (avoid import cycle at module load)

    for crop_name, econ in CROP_REFERENCE.items():
        db.add(
            CropReference(
                crop_name=crop_name,
                seed_cost_per_acre=econ.seed_cost_per_acre,
                fertilizer_cost_per_acre=econ.fertilizer_cost_per_acre,
                labor_cost_per_acre=econ.labor_cost_per_acre,
                water_cost_per_acre=econ.water_cost_per_acre,
                yield_per_acre_units=econ.yield_per_acre_units,
                price_per_unit=econ.price_per_unit,
                duration_days=econ.duration_days,
                water_need=econ.water_need,
                suitable_soils=econ.suitable_soils,
                cost_confidence=econ.cost_confidence,
                yield_source=econ.yield_source,
                price_source=econ.price_source,
                notes=econ.notes,
            )
        )
    db.commit()
