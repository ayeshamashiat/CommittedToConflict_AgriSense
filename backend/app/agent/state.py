"""AgentTurn / AgentDecision data structures shared across planner, executor, explainer."""

from dataclasses import dataclass, field
from typing import Literal

AgentAction = Literal["ask_clarifying_question", "recommend", "chat_reply"]


@dataclass
class AgentDecision:
    """What the planner decided to do for this turn."""

    action: AgentAction
    clarifying_question: str | None = None  # set when action == "ask_clarifying_question"
    candidate_crops: list[str] = field(default_factory=list)  # set when action == "recommend"
    crop_selection_source: str = "heuristic"  # "llm" | "heuristic" — for the trace/debugging


@dataclass
class ToolCallRecord:
    """One executed tool call, normalized for both persistence (ToolCallLog)
    and the API response (ToolTraceEntry)."""

    tool_name: str
    input: dict
    output: dict
    status: str = "success"
    error_message: str | None = None


@dataclass
class AgentTurn:
    """Everything accumulated while handling one /chat turn."""

    session_id: str
    message: str
    decision: AgentDecision | None = None
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    weather: dict | None = None
    per_crop_finance: dict[str, dict] = field(default_factory=dict)
    per_crop_rag: dict[str, list[str]] = field(default_factory=dict)
