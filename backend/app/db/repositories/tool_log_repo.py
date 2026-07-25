"""CRUD for ToolCallLog rows - powers the frontend Agent Trace panel."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import ToolCallLog


def log_tool_call(
    db: DBSession,
    session_id: str,
    tool_name: str,
    input_json: dict,
    output_json: dict,
    status: str = "success",
    error_message: str | None = None,
    latency_ms: float | None = None,
) -> ToolCallLog:
    entry = ToolCallLog(
        session_id=session_id,
        tool_name=tool_name,
        input_json=input_json,
        output_json=output_json,
        status=status,
        error_message=error_message,
        latency_ms=latency_ms,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_tool_calls(db: DBSession, session_id: str) -> list[ToolCallLog]:
    return (
        db.query(ToolCallLog)
        .filter(ToolCallLog.session_id == session_id)
        .order_by(ToolCallLog.created_at.asc())
        .all()
    )
