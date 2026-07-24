"""CRUD for Session rows, called by memory_manager and api/routes."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import Session as SessionModel


def create_session(db: DBSession, farmer_key: str | None = None) -> SessionModel:
    session = SessionModel(farmer_key=farmer_key)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DBSession, session_id: str) -> SessionModel | None:
    return db.get(SessionModel, session_id)


def get_or_create_session(
    db: DBSession, session_id: str | None, farmer_key: str | None = None
) -> tuple[SessionModel, bool]:
    """Returns (session, is_new) — callers need is_new to know whether it's safe/
    meaningful to carry forward a returning farmer's prior profile."""
    if session_id:
        existing = get_session(db, session_id)
        if existing:
            return existing, False
    return create_session(db, farmer_key=farmer_key), True


def find_latest_profile_session(
    db: DBSession, farmer_key: str, exclude_session_id: str
) -> SessionModel | None:
    """Most recently updated OTHER session for this farmer_key that has a farm
    profile — used to carry the farm forward into a brand new session."""
    return (
        db.query(SessionModel)
        .filter(SessionModel.farmer_key == farmer_key, SessionModel.id != exclude_session_id)
        .order_by(SessionModel.updated_at.desc())
        .first()
    )


def list_sessions_for_farmer(db: DBSession, farmer_key: str, limit: int = 50) -> list[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(SessionModel.farmer_key == farmer_key)
        .order_by(SessionModel.updated_at.desc())
        .limit(limit)
        .all()
    )


def list_sessions(db: DBSession, limit: int = 50) -> list[SessionModel]:
    return (
        db.query(SessionModel)
        .order_by(SessionModel.updated_at.desc())
        .limit(limit)
        .all()
    )


def touch_session(db: DBSession, session_id: str) -> None:
    session = get_session(db, session_id)
    if session is None:
        return
    db.add(session)
    db.commit()
