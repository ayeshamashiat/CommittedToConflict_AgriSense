"""Registers AgriTool implementations and exposes lookup for planner/executor."""

from app.tools.base import AgriTool
from app.tools.fertilizer_scheduler_tool import FertilizerSchedulerTool
from app.tools.finance_tool import FinanceTool
from app.tools.irrigation_scheduler_tool import IrrigationSchedulerTool
from app.tools.disease_detection_tool import DiseaseDetectionTool
from app.tools.marketplace_tool import MarketplaceTool
from app.tools.pest_risk_tool import PestRiskTool
from app.tools.price_intelligence_tool import PriceIntelligenceTool
from app.tools.rag_tool import RAGTool
from app.tools.scenario_simulator_tool import ScenarioSimulatorTool
from app.tools.weather_tool import WeatherTool

_TOOLS: dict[str, AgriTool] = {
    WeatherTool.name: WeatherTool(),
    RAGTool.name: RAGTool(),
    FinanceTool.name: FinanceTool(),
    FertilizerSchedulerTool.name: FertilizerSchedulerTool(),
    IrrigationSchedulerTool.name: IrrigationSchedulerTool(),
    PestRiskTool.name: PestRiskTool(),
    ScenarioSimulatorTool.name: ScenarioSimulatorTool(),
    MarketplaceTool.name: MarketplaceTool(),
    PriceIntelligenceTool.name: PriceIntelligenceTool(),
    DiseaseDetectionTool.name: DiseaseDetectionTool(),
}


def get_tool(name: str) -> AgriTool:
    try:
        return _TOOLS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown tool: {name!r}. Available: {list(_TOOLS)}") from exc


def list_tools() -> list[AgriTool]:
    return list(_TOOLS.values())


def tool_specs() -> list[dict]:
    """Description of each tool, in a shape suitable for LLM function-calling."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema.model_json_schema(),
        }
        for tool in _TOOLS.values()
    ]
