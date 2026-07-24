"""CRUD for Message rows, called by memory_manager and api/routes."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import Message


def add_message(db: DBSession, session_id: str, role: str, content: str) -> Message:
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: DBSession, session_id: str) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )
