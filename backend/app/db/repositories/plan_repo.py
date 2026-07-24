"""CRUD for SeasonPlan and FinancialProjection rows."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import FinancialProjection, SeasonPlan


def save_season_plan(db: DBSession, session_id: str, crop_name: str, stages: dict) -> SeasonPlan:
    plan = SeasonPlan(
        session_id=session_id,
        crop_name=crop_name,
        land_preparation=stages.get("land_preparation"),
        sowing=stages.get("sowing"),
        fertilizer=stages.get("fertilizer"),
        irrigation=stages.get("irrigation"),
        pest_checks=stages.get("pest_checks"),
        harvest=stages.get("harvest"),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def save_financial_projection(
    db: DBSession, session_id: str, crop_name: str, figures: dict
) -> FinancialProjection:
    projection = FinancialProjection(
        session_id=session_id,
        crop_name=crop_name,
        seed_cost=figures["seed_cost"],
        fertilizer_cost=figures["fertilizer_cost"],
        labor_cost=figures["labor_cost"],
        water_cost=figures["water_cost"],
        total_cost=figures["total_cost"],
        revenue=figures["revenue"],
        profit=figures["profit"],
        roi_percent=figures["roi_percent"],
        break_even_days=figures.get("break_even_days"),
    )
    db.add(projection)
    db.commit()
    db.refresh(projection)
    return projection


def list_season_plans(db: DBSession, session_id: str) -> list[SeasonPlan]:
    return db.query(SeasonPlan).filter(SeasonPlan.session_id == session_id).all()


def list_financial_projections(db: DBSession, session_id: str) -> list[FinancialProjection]:
    return (
        db.query(FinancialProjection)
        .filter(FinancialProjection.session_id == session_id)
        .all()
    )
