"""Merges short-term + long-term memory into agent context for one turn.

Nothing here writes memory back — the caller (agent/core.py) already persists
the user/assistant messages and profile updates via the same repositories
chat.py uses, so there is a single source of truth for what "remembering"
means rather than a second parallel memory store.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session as DBSession

from app.db.models import FarmProfile
from app.db.repositories.farm_repo import missing_fields
from app.memory.long_term import known_facts
from app.memory.short_term import get_recent_turns


@dataclass
class AgentMemory:
    recent_turns: list[dict]
    known_facts: dict
    missing_fields: list[str]


def build_context(db: DBSession, session_id: str, profile: FarmProfile) -> AgentMemory:
    return AgentMemory(
        recent_turns=get_recent_turns(db, session_id),
        known_facts=known_facts(profile),
        missing_fields=missing_fields(profile),
    )
