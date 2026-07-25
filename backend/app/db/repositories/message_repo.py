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


def get_first_user_message(db: DBSession, session_id: str) -> Message | None:
    """Used as the chat sidebar's conversation title/preview — the farmer's
    opening message is a far more useful label than a bare timestamp."""
    return (
        db.query(Message)
        .filter(Message.session_id == session_id, Message.role == "user")
        .order_by(Message.created_at.asc())
        .first()
    )
