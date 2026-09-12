"""Export calculation results at the application boundary.

Pandas is used here only to write CSV and Excel. Internal engine state
remains typed models.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from mpd_engine.results.result_models import CalculationResult
from mpd_engine.units.conversions import pa_to_kpa


def profile_rows(result: CalculationResult) -> list[dict[str, float | str | None]]:
    """Return JSON-serialisable profile rows with SI plus kPa display columns."""
    rows: list[dict[str, float | str | None]] = []
    for point in result.profile:
        rows.append(
            {
                "md_m": point.md_m,
                "tvd_m": point.tvd_m,
                "hydrostatic_pressure_pa": point.hydrostatic_pressure_pa,
                "hydrostatic_pressure_kpa": pa_to_kpa(point.hydrostatic_pressure_pa),
                "annular_friction_to_surface_pa": point.annular_friction_to_surface_pa,
                "annular_friction_to_surface_kpa": pa_to_kpa(
                    point.annular_friction_to_surface_pa
                ),
                "surface_backpressure_pa": point.surface_backpressure_pa,
                "annular_pressure_pa": point.annular_pressure_pa,
                "annular_pressure_kpa": pa_to_kpa(point.annular_pressure_pa),
                "ecd_kg_m3": point.ecd_kg_m3,
                "pore_pressure_pa": point.pore_pressure_pa,
                "collapse_pressure_pa": point.collapse_pressure_pa,
                "fracture_pressure_pa": point.fracture_pressure_pa,
                "window_status": point.window_status.value,
            }
        )
    return rows


def result_to_csv(result: CalculationResult) -> str:
    """Return a CSV document for the depth profile."""
    rows = profile_rows(result)
    if not rows:
        raise ValueError("Calculation result has no profile rows to export")
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def write_result_csv(result: CalculationResult, path: str | Path) -> Path:
    """Write the profile CSV to *path* and return the path."""
    target = Path(path)
    target.write_text(result_to_csv(result), encoding="utf-8")
    return target


def result_to_excel_bytes(result: CalculationResult) -> bytes:
    """Return an .xlsx workbook with profile, summary, warnings, and assumptions.

    Requires pandas and openpyxl. Used at the export boundary only.
    """
    import pandas as pd  # type: ignore[import-untyped]

    profile = pd.DataFrame(profile_rows(result))
    summary = pd.DataFrame([result.summary.model_dump(mode="json")])
    warnings = pd.DataFrame([warning.model_dump(mode="json") for warning in result.warnings])
    assumptions = pd.DataFrame({"assumption": list(result.assumptions)})
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        profile.to_excel(writer, sheet_name="profile", index=False)
        summary.to_excel(writer, sheet_name="summary", index=False)
        warnings.to_excel(writer, sheet_name="warnings", index=False)
        assumptions.to_excel(writer, sheet_name="assumptions", index=False)
    return buffer.getvalue()
