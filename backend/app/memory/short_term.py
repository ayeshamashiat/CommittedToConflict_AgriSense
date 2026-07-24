"""Per-session rolling conversation buffer used to keep LLM context coherent."""

from sqlalchemy.orm import Session as DBSession

from app.db.repositories.message_repo import list_messages

MAX_TURNS = 8  # cap how much history we feed the LLM per call


def get_recent_turns(db: DBSession, session_id: str) -> list[dict]:
    """Last MAX_TURNS messages as {"role", "content"} dicts, oldest first —
    ready to splice into an OpenAI `messages` list."""
    messages = list_messages(db, session_id)[-MAX_TURNS:]
    return [{"role": m.role, "content": m.content} for m in messages]
