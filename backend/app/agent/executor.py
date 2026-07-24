"""Calls the tool(s) chosen by the planner and normalizes their outputs.

Every call goes through app.tools.registry so the executor stays agnostic to
how each tool is implemented, and every call is logged via tool_log_repo so
it shows up in the frontend's Agent Trace panel regardless of whether it was
triggered by the real agent or the /weather, /retrieve, /calculate routes.
"""

import time

from sqlalchemy.orm import Session as DBSession

from app.agent.state import ToolCallRecord
from app.db.repositories.tool_log_repo import log_tool_call
from app.tools.registry import get_tool


def call_tool(db: DBSession, session_id: str, tool_name: str, input_dict: dict) -> ToolCallRecord:
    tool = get_tool(tool_name)
    started = time.perf_counter()
    try:
        output = tool.run_dict(input_dict)
        record = ToolCallRecord(tool_name=tool_name, input=input_dict, output=output)
    except Exception as exc:  # noqa: BLE001 - a failed tool call must not crash the turn
        record = ToolCallRecord(
            tool_name=tool_name,
            input=input_dict,
            output={},
            status="error",
            error_message=str(exc),
        )

    log_tool_call(
        db,
        session_id=session_id,
        tool_name=tool_name,
        input_json=record.input,
        output_json=record.output,
        status=record.status,
        error_message=record.error_message,
        latency_ms=(time.perf_counter() - started) * 1000,
    )
    return record
