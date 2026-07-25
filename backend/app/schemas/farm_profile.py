"""Pydantic schema for farm profile data exchanged via the API."""

from typing import Literal

from pydantic import BaseModel, field_validator

FarmSizeUnit = Literal["acre", "bigha", "katha", "decimal", "shotangsho"]

# Swagger/OpenAPI "Try it out" pre-fills every string field with the literal
# word "string" and every number field with 0. Farmers obviously never enter
# these, but nothing rejects them either — they pass isinstance/not-None
# checks and get treated as real, complete data. Silently converting these
# to None here means the API's own placeholder defaults can never be
# mistaken for a farmer-provided value downstream.
_PLACEHOLDER_STRINGS = {"", "string"}


class FarmProfileIn(BaseModel):
    """Any subset of profile fields the farmer has provided so far.

    farm_size is entered in whatever unit is natural for the farmer
    (acre, bigha, katha, decimal/shotangsho) and converted to acres
    server-side for calculations.
    """

    location: str | None = None
    farm_size: float | None = None
    farm_size_unit: FarmSizeUnit = "acre"
    soil_type: str | None = None
    water_availability: str | None = None
    budget: float | None = None
    target_season: str | None = None

    @field_validator("location", "soil_type", "water_availability", "target_season")
    @classmethod
    def _reject_placeholder_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return None if cleaned.lower() in _PLACEHOLDER_STRINGS else cleaned

    @field_validator("farm_size", "budget")
    @classmethod
    def _reject_non_positive(cls, value: float | None) -> float | None:
        return None if value is None or value <= 0 else value


class FarmProfileOut(BaseModel):
    location: str | None = None
    farm_size: float | None = None  # acres, used for all calculations
    farm_size_unit: str = "acre"  # unit the farmer originally entered
    farm_size_original: float | None = None  # value as entered, in farm_size_unit
    soil_type: str | None = None
    water_availability: str | None = None
    budget: float | None = None
    target_season: str | None = None

    model_config = {"from_attributes": True}
