"""Plotly chart helpers. Depth increases downward."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
from mpd_engine.units.conversions import pa_to_kpa


def _depth_axis() -> dict[str, Any]:
    return {"title": "TVD, m", "autorange": "reversed"}


def pressure_profile_figure(profile: list[dict[str, Any]]) -> go.Figure:
    tvd = [row["tvd_m"] for row in profile]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[pa_to_kpa(row["hydrostatic_pressure_pa"]) for row in profile],
            y=tvd,
            name="Hydrostatic",
            mode="lines",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[pa_to_kpa(row["annular_pressure_pa"]) for row in profile],
            y=tvd,
            name="Annular / dynamic BHP",
            mode="lines",
        )
    )
    fig.update_layout(
        title="Pressure vs TVD",
        xaxis_title="Pressure, kPa",
        yaxis=_depth_axis(),
        template="plotly_white",
        legend={"orientation": "h"},
    )
    return fig


def friction_profile_figure(profile: list[dict[str, Any]]) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[pa_to_kpa(row["annular_friction_to_surface_pa"]) for row in profile],
            y=[row["tvd_m"] for row in profile],
            name="Annular friction to surface",
            mode="lines",
        )
    )
    fig.update_layout(
        title="Annular friction vs TVD",
        xaxis_title="Friction pressure, kPa",
        yaxis=_depth_axis(),
        template="plotly_white",
    )
    return fig


def ecd_figure(profile: list[dict[str, Any]]) -> go.Figure:
    rows = [row for row in profile if row.get("ecd_kg_m3") is not None]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[row["ecd_kg_m3"] for row in rows],
            y=[row["tvd_m"] for row in rows],
            name="ECD",
            mode="lines",
        )
    )
    fig.update_layout(
        title="ECD vs TVD",
        xaxis_title="ECD, kg/m³",
        yaxis=_depth_axis(),
        template="plotly_white",
    )
    return fig


def connection_comparison_figure(connection: dict[str, Any]) -> go.Figure:
    """Bar comparison of API connection fields. No hydraulics are recomputed here."""
    labels = [
        "Pump-on BHP",
        "Pump-off BHP (same SBP)",
        "Required SBP, pump-off",
        "Pump-on SBP",
    ]
    values = [
        pa_to_kpa(connection["pump_on_bhp_pa"]),
        pa_to_kpa(connection["pump_off_sbp_same_as_pump_on_bhp_pa"]),
        pa_to_kpa(connection["required_sbp_pump_off_pa"]),
        pa_to_kpa(connection["pump_on_sbp_pa"]),
    ]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", name="kPa"))
    fig.update_layout(
        title="Connection comparison (steady-state, from API)",
        xaxis_title="Pressure, kPa",
        yaxis={"autorange": "reversed"},
        template="plotly_white",
    )
    return fig


def pressure_window_figure(profile: list[dict[str, Any]]) -> go.Figure:
    tvd = [row["tvd_m"] for row in profile]
    fig = go.Figure()
    traces = [
        ("pore_pressure_pa", "Pore pressure"),
        ("collapse_pressure_pa", "Collapse pressure"),
        ("hydrostatic_pressure_pa", "Static pressure"),
        ("annular_pressure_pa", "Dynamic BHP"),
        ("fracture_pressure_pa", "Fracture pressure"),
    ]
    for key, name in traces:
        xs = [pa_to_kpa(row[key]) if row.get(key) is not None else None for row in profile]
        fig.add_trace(go.Scatter(x=xs, y=tvd, name=name, mode="lines"))
    ecd_rows = [row for row in profile if row.get("ecd_kg_m3") is not None]
    fig.add_trace(
        go.Scatter(
            x=[row["ecd_kg_m3"] for row in ecd_rows],
            y=[row["tvd_m"] for row in ecd_rows],
            name="ECD, kg/m³ (top axis scale differs)",
            mode="lines",
            yaxis="y",
            xaxis="x2",
        )
    )
    fig.update_layout(
        title="Pressure window (depth down)",
        xaxis=dict(title="Pressure, kPa"),
        xaxis2=dict(title="ECD, kg/m³", overlaying="x", side="top"),
        yaxis=_depth_axis(),
        template="plotly_white",
        legend={"orientation": "h", "y": -0.15},
    )
    return fig
