"""AgentOrchestrator: runs one full turn - memory in, planner, executor, explainer, memory out.

This is the object api/deps.get_agent() instantiates and api/routes/chat.py
calls .handle_turn() on. It never touches HTTP concerns (request/response
schemas) — chat.py owns those — and never decides persistence of the
conversation messages themselves (chat.py does that too, via message_repo),
keeping "the agent" scoped to: read memory, decide, act, explain.
"""

from sqlalchemy.orm import Session as DBSession

from app.agent import chat_responder, executor, planner
from app.agent import explainer as explainer_module
from app.agent.proactive import generate_alerts
from app.agent.season_calendar import compute_stage_dates
from app.db.models import FarmProfile
from app.db.repositories.crop_reference_repo import get_by_name, list_all
from app.db.repositories.plan_repo import list_season_plans, save_financial_projection, save_season_plan
from app.llm.client import LLMClient
from app.memory.memory_manager import build_context
from app.schemas.chat import ToolTraceEntry
from app.tools.crop_data import DEFAULT_CROP


class AgentOrchestrator:
    def __init__(self):
        self.llm = LLMClient()

    def handle_turn(
        self,
        db: DBSession,
        session_id: str,
        message: str,
        profile: FarmProfile,
        profile_updated: bool = False,
        language: str = "en",
    ) -> dict:
        memory = build_context(db, session_id, profile)
        decision = planner.decide(self.llm, db, profile, memory, message, session_id, profile_updated, language)

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

        if decision.action == "chat_reply":
            return self._chat_reply(db, session_id, profile, message, language)

        return self._recommend(db, session_id, profile, decision.candidate_crops, message, language)

    def _chat_reply(
        self, db: DBSession, session_id: str, profile: FarmProfile, message: str, language: str = "en"
    ) -> dict:
        prior_plans = list_season_plans(db, session_id)
        last_crop = prior_plans[-1].crop_name if prior_plans else None

        # Tier 2: "where can I buy urea" style messages get real supplier data
        # instead of a generic chat reply — only when there's enough context
        # (a seed lookup needs a crop; everything else doesn't).
        item = chat_responder.detect_marketplace_request(message)
        if item and (item != "seed" or last_crop):
            mp_record = executor.call_tool(
                db,
                session_id,
                "marketplace",
                {"item": item, "crop": last_crop, "farmer_location": profile.location},
            )
            if mp_record.status == "success":
                trace = [
                    ToolTraceEntry(
                        tool_name=mp_record.tool_name,
                        input=mp_record.input,
                        output=mp_record.output,
                        status=mp_record.status,
                    )
                ]
                return {
                    "reply": chat_responder.compose_marketplace_reply(mp_record.output, item, language),
                    "missing_fields": [],
                    "recommendations": None,
                    "season_plan": None,
                    "financial_summary": None,
                    "weather": None,
                    "trace": trace,
                    "alerts": [],
                    "marketplace_offers": mp_record.output,
                }

        # Tier 2: "should I sell my rice now?" style messages get real price
        # data instead of a generic chat reply. A named crop in the message
        # wins; otherwise falls back to the crop last recommended this session.
        if chat_responder.is_price_query(message):
            price_crop = self._match_crop_name(db, message) or last_crop
            if price_crop:
                price_record = executor.call_tool(db, session_id, "price_intelligence", {"crop": price_crop})
                if price_record.status == "success":
                    trace = [
                        ToolTraceEntry(
                            tool_name=price_record.tool_name,
                            input=price_record.input,
                            output=price_record.output,
                            status=price_record.status,
                        )
                    ]
                    return {
                        "reply": chat_responder.compose_price_reply(price_record.output, language),
                        "missing_fields": [],
                        "recommendations": None,
                        "season_plan": None,
                        "financial_summary": None,
                        "weather": None,
                        "trace": trace,
                        "alerts": [],
                        "price_intelligence": price_record.output,
                    }

        rag_record = executor.call_tool(db, session_id, "rag_search", {"query": message, "n_results": 2})
        passages = rag_record.output.get("passages", []) if rag_record.status == "success" else []

        reply = chat_responder.compose(self.llm, profile, passages, message, last_crop, language)

        trace = [ToolTraceEntry(tool_name=rag_record.tool_name, input=rag_record.input, output=rag_record.output, status=rag_record.status)]

        return {
            "reply": reply,
            "missing_fields": [],
            "recommendations": None,
            "season_plan": None,
            "financial_summary": None,
            "weather": None,
            "trace": trace,
            "alerts": [],
        }

    @staticmethod
    def _match_crop_name(db: DBSession, message: str) -> str | None:
        """Cheap, deterministic keyword match against the known crop names —
        same technique planner._mentioned_crop uses for recommendation intent,
        applied here to resolve which crop a price/sell question is about."""
        low = (message or "").lower()
        for row in list_all(db):
            display = row.crop_name.replace("_", " ")
            if row.crop_name in low or display in low:
                return row.crop_name
        return None

    def _recommend(
        self,
        db: DBSession,
        session_id: str,
        profile: FarmProfile,
        candidate_crops: list[str],
        message: str,
        language: str = "en",
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
            self.llm, profile, weather_output, per_crop, message, language
        )

        top_crop = candidate_crops[0]
        top_crop_row = get_by_name(db, top_crop) or DEFAULT_CROP
        financial_summary = per_crop[top_crop]["finance"]

        # Tier 1: dated calendar + proactive weather-triggered adjustment.
        stage_dates = compute_stage_dates(top_crop_row.duration_days)
        alerts, stage_dates = generate_alerts(weather_output, stage_dates, top_crop_row.water_need)
        season_plan_dict = season_plan.model_dump()
        season_plan_dict.update(stage_dates)

        save_season_plan(db, session_id, season_plan.crop_name, season_plan.model_dump(exclude={"crop_name"}))

        # Tier 1: fertilizer/irrigation scheduler + pest risk for the top crop.
        fert_record = executor.call_tool(
            db, session_id, "fertilizer_scheduler", {"crop": top_crop, "farm_size": profile.farm_size}
        )
        tool_calls.append(fert_record)

        irrigation_record = executor.call_tool(
            db,
            session_id,
            "irrigation_scheduler",
            {
                "crop": top_crop,
                "farm_size": profile.farm_size,
                "water_availability": profile.water_availability,
            },
        )
        tool_calls.append(irrigation_record)

        pest_record = None
        if weather_output:
            pest_record = executor.call_tool(
                db,
                session_id,
                "pest_risk_assessor",
                {
                    "crop": top_crop,
                    "temperature": weather_output["temperature"],
                    "humidity": weather_output["humidity"],
                    "rainfall": weather_output["rainfall"],
                    "forecast": weather_output.get("forecast", []),
                },
            )
            tool_calls.append(pest_record)

        trace = [
            ToolTraceEntry(tool_name=r.tool_name, input=r.input, output=r.output, status=r.status)
            for r in tool_calls
        ]

        return {
            "reply": reply,
            "missing_fields": [],
            "recommendations": recommendations,
            "season_plan": season_plan_dict,
            "financial_summary": financial_summary,
            "weather": weather_output,
            "trace": trace,
            "alerts": alerts,
            "fertilizer_schedule": fert_record.output if fert_record.status == "success" else None,
            "irrigation_schedule": irrigation_record.output if irrigation_record.status == "success" else None,
            "pest_risks": pest_record.output if pest_record and pest_record.status == "success" else None,
        }
