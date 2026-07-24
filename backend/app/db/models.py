"""SQLAlchemy ORM models: Session, Message, FarmProfile, ToolCallLog, SeasonPlan, FinancialProjection."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Session(Base):
    """A farmer's conversation session. Acts as the aggregate root for memory."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    # Farmer-chosen identifier (e.g. phone number) that persists across devices/sessions.
    # When a new session starts with a farmer_key that has a prior session, the farm
    # profile is carried forward automatically — this is Tier 1 "persistent memory".
    farmer_key: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at"
    )
    farm_profile: Mapped["FarmProfile"] = relationship(
        back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    tool_calls: Mapped[list["ToolCallLog"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ToolCallLog.created_at"
    )
    season_plans: Mapped[list["SeasonPlan"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    financial_projections: Mapped[list["FinancialProjection"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    """One turn of the conversation (user, assistant, or tool)."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String)  # user | assistant | system | tool
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship(back_populates="messages")


class FarmProfile(Base):
    """Long-term memory: the farmer's profile, collected incrementally over the conversation."""

    __tablename__ = "farm_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), unique=True, index=True)

    location: Mapped[str | None] = mapped_column(String, nullable=True)
    farm_size: Mapped[float | None] = mapped_column(Float, nullable=True)  # always stored in acres
    farm_size_unit: Mapped[str] = mapped_column(String, default="acre")  # unit the farmer entered
    farm_size_original: Mapped[float | None] = mapped_column(Float, nullable=True)  # value as entered
    soil_type: Mapped[str | None] = mapped_column(String, nullable=True)
    water_availability: Mapped[str | None] = mapped_column(String, nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_season: Mapped[str | None] = mapped_column(String, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    session: Mapped["Session"] = relationship(back_populates="farm_profile")


class ToolCallLog(Base):
    """Every tool invocation, for display in the frontend Agent Trace panel."""

    __tablename__ = "tool_call_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    tool_name: Mapped[str] = mapped_column(String)
    input_json: Mapped[dict] = mapped_column(JSON)
    output_json: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="success")  # success | error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship(back_populates="tool_calls")


class SeasonPlan(Base):
    """A recommended crop calendar produced for a session."""

    __tablename__ = "season_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    crop_name: Mapped[str] = mapped_column(String)

    land_preparation: Mapped[str | None] = mapped_column(Text, nullable=True)
    sowing: Mapped[str | None] = mapped_column(Text, nullable=True)
    fertilizer: Mapped[str | None] = mapped_column(Text, nullable=True)
    irrigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    pest_checks: Mapped[str | None] = mapped_column(Text, nullable=True)
    harvest: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship(back_populates="season_plans")


class FinancialProjection(Base):
    """Output of the financial calculator for a crop, tied to a session."""

    __tablename__ = "financial_projections"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    crop_name: Mapped[str] = mapped_column(String)

    seed_cost: Mapped[float] = mapped_column(Float)
    fertilizer_cost: Mapped[float] = mapped_column(Float)
    labor_cost: Mapped[float] = mapped_column(Float)
    water_cost: Mapped[float] = mapped_column(Float)
    total_cost: Mapped[float] = mapped_column(Float)
    revenue: Mapped[float] = mapped_column(Float)
    profit: Mapped[float] = mapped_column(Float)
    roi_percent: Mapped[float] = mapped_column(Float)
    break_even_days: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship(back_populates="financial_projections")


class CropReference(Base):
    """Per-acre cost/yield/price reference data for the financial calculator.

    Seeded at startup from app/tools/crop_data.py (see that module's
    docstring for full source citations: BBS Yearbook 2024, USDA GAIN,
    DAM price notice, BSFIC). Living in the DB rather than only in code
    means prices can be updated (e.g. via a future admin endpoint) without
    a redeploy, and stays consistent with the rest of the app's persistence.
    """

    __tablename__ = "crop_references"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    crop_name: Mapped[str] = mapped_column(String, unique=True, index=True)

    seed_cost_per_acre: Mapped[float] = mapped_column(Float)
    fertilizer_cost_per_acre: Mapped[float] = mapped_column(Float)
    labor_cost_per_acre: Mapped[float] = mapped_column(Float)
    water_cost_per_acre: Mapped[float] = mapped_column(Float)
    yield_per_acre_units: Mapped[float] = mapped_column(Float)
    price_per_unit: Mapped[float] = mapped_column(Float)
    duration_days: Mapped[int] = mapped_column()
    water_need: Mapped[str] = mapped_column(String)
    suitable_soils: Mapped[list] = mapped_column(JSON)
    cost_confidence: Mapped[str] = mapped_column(String, default="mixed")
    yield_source: Mapped[str] = mapped_column(Text, default="")
    price_source: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
