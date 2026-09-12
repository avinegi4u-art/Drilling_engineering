"""SQLAlchemy persistence models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Well(Base):
    __tablename__ = "wells"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="engineer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    well_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    sections: Mapped[list[WellSection]] = relationship(
        back_populates="well", cascade="all, delete-orphan"
    )
    fluid_programs: Mapped[list[FluidProgram]] = relationship(
        back_populates="well", cascade="all, delete-orphan"
    )
    pressure_windows: Mapped[list[PressureWindow]] = relationship(
        back_populates="well", cascade="all, delete-orphan"
    )
    scenarios: Mapped[list[Scenario]] = relationship(
        back_populates="well", cascade="all, delete-orphan"
    )


class WellSection(Base):
    __tablename__ = "well_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    md_top_m: Mapped[float] = mapped_column(Float, nullable=False)
    md_bottom_m: Mapped[float] = mapped_column(Float, nullable=False)
    tvd_top_m: Mapped[float] = mapped_column(Float, nullable=False)
    tvd_bottom_m: Mapped[float] = mapped_column(Float, nullable=False)
    hole_id_m: Mapped[float] = mapped_column(Float, nullable=False)
    annular_section_type: Mapped[str] = mapped_column(String(32), nullable=False)
    casing_id_m: Mapped[float | None] = mapped_column(Float, nullable=True)

    well: Mapped[Well] = relationship(back_populates="sections")


class FluidProgram(Base):
    __tablename__ = "fluid_programs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id"), nullable=False)
    mud_density_kg_m3: Mapped[float] = mapped_column(Float, nullable=False)
    plastic_viscosity_pa_s: Mapped[float] = mapped_column(Float, nullable=False)
    yield_stress_pa: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    rheology_model: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    well: Mapped[Well] = relationship(back_populates="fluid_programs")


class PressureWindow(Base):
    __tablename__ = "pressure_windows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id"), nullable=False)
    points_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)

    well: Mapped[Well] = relationship(back_populates="pressure_windows")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="engineer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    inputs_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    well: Mapped[Well] = relationship(back_populates="scenarios")
    runs: Mapped[list[CalculationRun]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )


class CalculationRun(Base):
    __tablename__ = "calculation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    calculation_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="engineer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    assumptions_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    inputs_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    scenario: Mapped[Scenario] = relationship(back_populates="runs")
    result: Mapped[CalculationResultRow | None] = relationship(
        back_populates="run", cascade="all, delete-orphan", uselist=False
    )


class CalculationResultRow(Base):
    __tablename__ = "calculation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("calculation_runs.id"), nullable=False, unique=True
    )
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    profile_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    warnings_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    connection_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    run: Mapped[CalculationRun] = relationship(back_populates="result")
