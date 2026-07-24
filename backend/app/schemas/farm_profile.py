"""Pydantic schema for farm profile data exchanged via the API."""

from typing import Literal

from pydantic import BaseModel

FarmSizeUnit = Literal["acre", "bigha", "katha", "decimal", "shotangsho"]


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
