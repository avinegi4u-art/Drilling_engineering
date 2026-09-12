"""Initial wells, scenarios, and calculation tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wells",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("well_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "well_sections",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("well_id", sa.String(length=36), sa.ForeignKey("wells.id"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("md_top_m", sa.Float(), nullable=False),
        sa.Column("md_bottom_m", sa.Float(), nullable=False),
        sa.Column("tvd_top_m", sa.Float(), nullable=False),
        sa.Column("tvd_bottom_m", sa.Float(), nullable=False),
        sa.Column("hole_id_m", sa.Float(), nullable=False),
        sa.Column("annular_section_type", sa.String(length=32), nullable=False),
        sa.Column("casing_id_m", sa.Float(), nullable=True),
    )
    op.create_table(
        "fluid_programs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("well_id", sa.String(length=36), sa.ForeignKey("wells.id"), nullable=False),
        sa.Column("mud_density_kg_m3", sa.Float(), nullable=False),
        sa.Column("plastic_viscosity_pa_s", sa.Float(), nullable=False),
        sa.Column("yield_stress_pa", sa.Float(), nullable=False),
        sa.Column("temperature_c", sa.Float(), nullable=False),
        sa.Column("rheology_model", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "pressure_windows",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("well_id", sa.String(length=36), sa.ForeignKey("wells.id"), nullable=False),
        sa.Column("points_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("well_id", sa.String(length=36), sa.ForeignKey("wells.id"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("inputs_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "calculation_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("scenario_id", sa.String(length=36), sa.ForeignKey("scenarios.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("calculation_version", sa.String(length=100), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("assumptions_json", sa.JSON(), nullable=False),
        sa.Column("inputs_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "calculation_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(length=36),
            sa.ForeignKey("calculation_runs.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("profile_json", sa.JSON(), nullable=False),
        sa.Column("warnings_json", sa.JSON(), nullable=False),
        sa.Column("connection_json", sa.JSON(), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("calculation_results")
    op.drop_table("calculation_runs")
    op.drop_table("scenarios")
    op.drop_table("pressure_windows")
    op.drop_table("fluid_programs")
    op.drop_table("well_sections")
    op.drop_table("wells")
