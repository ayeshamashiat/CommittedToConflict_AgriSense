"""AgentOrchestrator: runs one full turn - memory in, planner, executor, explainer, memory out.

This is the object api/deps.get_agent() instantiates and api/routes/chat.py
calls .handle_turn() on. It never touches HTTP concerns (request/response
schemas) — chat.py owns those — and never decides persistence of the
conversation messages themselves (chat.py does that too, via message_repo),
keeping "the agent" scoped to: read memory, decide, act, explain.
"""

from sqlalchemy.orm import Session as DBSession

from app.agent import executor, planner
from app.agent import explainer as explainer_module
from app.db.models import FarmProfile
from app.db.repositories.crop_reference_repo import get_by_name
from app.db.repositories.plan_repo import save_financial_projection, save_season_plan
from app.llm.client import LLMClient
from app.memory.memory_manager import build_context
from app.schemas.chat import ToolTraceEntry
from app.tools.crop_data import DEFAULT_CROP


class AgentOrchestrator:
    def __init__(self):
        self.llm = LLMClient()

    def handle_turn(self, db: DBSession, session_id: str, message: str, profile: FarmProfile) -> dict:
        memory = build_context(db, session_id, profile)
        decision = planner.decide(self.llm, db, profile, memory, message)

        if decision.action == "ask_clarifying_question":
            return {
                "reply": decision.clarifying_question,
                "missing_fields": memory.missing_fields,
                "recommendations": None,
                "season_plan": None,
                "financial_summary": None,
                "weather": None,
                "trace": [],
            }

        return self._recommend(db, session_id, profile, decision.candidate_crops, message)

    def _recommend(
        self,
        db: DBSession,
        session_id: str,
        profile: FarmProfile,
        candidate_crops: list[str],
        message: str,
    ) -> dict:
        tool_calls = []

        weather_record = executor.call_tool(db, session_id, "weather", {"location": profile.location})
        tool_calls.append(weather_record)
        weather_output = weather_record.output if weather_record.status == "success" else None

        per_crop: dict[str, dict] = {}
        for crop_name in candidate_crops:
            rag_record = executor.call_tool(
                db,
                session_id,
                "rag_search",
                {
                    "query": (
                        f"{crop_name} suitability for {profile.soil_type} soil and "
                        f"{profile.water_availability} water availability"
                    ),
                    "n_results": 2,
                },
            )
            tool_calls.append(rag_record)

            finance_record = executor.call_tool(
                db,
                session_id,
                "financial_calculator",
                {"crop": crop_name, "farm_size": profile.farm_size, "budget": profile.budget},
            )
            tool_calls.append(finance_record)
            if finance_record.status == "success":
                save_financial_projection(db, session_id, crop_name, finance_record.output)

            crop_row = get_by_name(db, crop_name) or DEFAULT_CROP
            per_crop[crop_name] = {
                "rag_passages": rag_record.output.get("passages", []),
                "finance": finance_record.output,
                "water_need": crop_row.water_need,
                "duration_days": crop_row.duration_days,
                "suitable_soils": crop_row.suitable_soils,
            }

        recommendations, season_plan, reply = explainer_module.compose(
            self.llm, profile, weather_output, per_crop, message
        )
        save_season_plan(db, session_id, season_plan.crop_name, season_plan.model_dump(exclude={"crop_name"}))

        top_crop = candidate_crops[0]
        financial_summary = per_crop[top_crop]["finance"]

        trace = [
            ToolTraceEntry(tool_name=r.tool_name, input=r.input, output=r.output, status=r.status)
            for r in tool_calls
        ]

        return {
            "reply": reply,
            "missing_fields": [],
            "recommendations": recommendations,
            "season_plan": season_plan,
            "financial_summary": financial_summary,
            "weather": weather_output,
            "trace": trace,
        }
