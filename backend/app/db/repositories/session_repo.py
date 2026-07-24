"""CRUD for Session rows, called by memory_manager and api/routes."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import Session as SessionModel


def create_session(db: DBSession) -> SessionModel:
    session = SessionModel()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DBSession, session_id: str) -> SessionModel | None:
    return db.get(SessionModel, session_id)


def get_or_create_session(db: DBSession, session_id: str | None) -> SessionModel:
    if session_id:
        existing = get_session(db, session_id)
        if existing:
            return existing
    return create_session(db)


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
