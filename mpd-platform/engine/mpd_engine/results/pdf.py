"""Basic PDF report for a calculation result.

The report is an engineering-review document. It does not contain
equipment-control commands.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import mm  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from mpd_engine.results.result_models import CalculationResult
from mpd_engine.units.conversions import pa_to_kpa


def result_to_pdf_bytes(result: CalculationResult) -> bytes:
    """Return a simple multi-page PDF report as bytes."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="MPD hydraulics calculation report",
        author="MPD Platform",
    )
    styles = getSampleStyleSheet()
    story: list[object] = [
        Paragraph("MPD Hydraulics Calculation Report", styles["Title"]),
        Paragraph(
            "Engineering decision support only. Not a choke or equipment-control command.",
            styles["Italic"],
        ),
        Spacer(1, 6 * mm),
        Paragraph(
            f"Calculation version: {result.calculation_version}<br/>"
            f"Timestamp (UTC): {result.timestamp_utc.astimezone(UTC).isoformat()}<br/>"
            f"Generated: {datetime.now(UTC).isoformat()}",
            styles["Normal"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Assumptions", styles["Heading2"]),
    ]
    for assumption in result.assumptions:
        story.append(Paragraph(f"• {assumption}", styles["Normal"]))

    summary = result.summary
    story.extend(
        [
            Spacer(1, 4 * mm),
            Paragraph("Summary (SI internally; kPa shown for review)", styles["Heading2"]),
        ]
    )
    summary_table = Table(
        [
            ["Quantity", "Value"],
            ["TVD, m", f"{summary.tvd_m:.2f}"],
            ["Flow rate, m³/s", f"{summary.flow_rate_m3_s:.6f}"],
            ["Operating mode", summary.operating_mode],
            ["Hydrostatic, kPa", f"{pa_to_kpa(summary.hydrostatic_pressure_pa):.1f}"],
            ["Annular friction, kPa", f"{pa_to_kpa(summary.annular_friction_pressure_pa):.1f}"],
            ["Applied SBP, kPa", f"{pa_to_kpa(summary.surface_backpressure_pa):.1f}"],
            ["Bottomhole pressure, kPa", f"{pa_to_kpa(summary.bottomhole_pressure_pa):.1f}"],
            [
                "ECD, kg/m³",
                "n/a" if summary.ecd_kg_m3 is None else f"{summary.ecd_kg_m3:.1f}",
            ],
            ["Window status at TD", summary.window_status.value],
        ],
        colWidths=[90 * mm, 80 * mm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f9fc")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Warnings", styles["Heading2"]))
    if not result.warnings:
        story.append(Paragraph("No warnings were recorded.", styles["Normal"]))
    else:
        for warning in result.warnings:
            story.append(
                Paragraph(
                    f"<b>{warning.code}</b> ({warning.severity.value})"
                    f"{'' if warning.depth_m is None else f' at {warning.depth_m:.1f} m'}"
                    f"<br/>{warning.explanation}<br/>"
                    f"<i>Review: {warning.recommended_engineering_review}</i>",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 2 * mm))

    document.build(story)
    return buffer.getvalue()
