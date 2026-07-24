"""Shared FastAPI dependencies: get_db(), get_agent(), get_current_session()."""

from collections.abc import Generator
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session as DBSession

from app.db.database import SessionLocal


def get_db() -> Generator[DBSession, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_agent() -> Any | None:
    """Returns the AgentOrchestrator (Member A's app/agent/core.py) if it has been
    implemented yet, else None so callers can fall back gracefully."""
    try:
        from app.agent.core import AgentOrchestrator  # noqa: PLC0415
    except ImportError:
        return None
    try:
        return AgentOrchestrator()
    except Exception:
        return None


DbDep = Depends(get_db)
