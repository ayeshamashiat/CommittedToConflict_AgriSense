"""AgriTool abstract base class: the plug-in contract (name, description, input_schema, run())."""

from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel


class AgriTool(ABC):
    """Every tool (weather, RAG, finance) implements this so the planner/executor
    can call them uniformly and every call can be logged for the Agent Trace panel."""

    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[type[BaseModel]]
    output_schema: ClassVar[type[BaseModel]]

    @abstractmethod
    def run(self, input_data: BaseModel) -> BaseModel:
        """Execute the tool synchronously and return a validated output_schema instance."""
        raise NotImplementedError

    def run_dict(self, input_dict: dict) -> dict:
        """Convenience wrapper for callers that work in raw dicts (routes, executor)."""
        parsed_input = self.input_schema(**input_dict)
        result = self.run(parsed_input)
        return result.model_dump()
