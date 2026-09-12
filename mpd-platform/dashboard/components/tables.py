"""Table helpers for results and warnings."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from mpd_engine.units.conversions import pa_to_kpa


def show_assumptions(assumptions: list[str] | None) -> None:
    """Show version-1 engineering assumptions from the API result payload."""
    items = assumptions or []
    with st.expander("Calculation assumptions", expanded=True):
        if not items:
            st.info("No assumptions were returned for this run.")
            return
        for item in items:
            st.markdown(f"- {item}")
        st.caption("These assumptions come from the calculation engine via the API.")


def show_warnings(warnings: list[dict[str, Any]]) -> None:
    if not warnings:
        st.success("No calculation warnings.")
        return
    rows = []
    for item in warnings:
        rows.append(
            {
                "code": item.get("code"),
                "severity": item.get("severity"),
                "depth_m": item.get("depth_m"),
                "actual_kpa": pa_to_kpa(item["actual_pressure_pa"])
                if item.get("actual_pressure_pa") is not None
                else None,
                "limit_kpa": pa_to_kpa(item["limit_pressure_pa"])
                if item.get("limit_pressure_pa") is not None
                else None,
                "explanation": item.get("explanation"),
                "review": item.get("recommended_engineering_review"),
            }
        )
    st.warning("Warnings are engineering-review notices, not operational commands.")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def show_profile(profile: list[dict[str, Any]]) -> None:
    frame = pd.DataFrame(profile)
    if "annular_pressure_pa" in frame.columns:
        frame["annular_pressure_kpa"] = frame["annular_pressure_pa"].map(pa_to_kpa)
        frame["hydrostatic_kpa"] = frame["hydrostatic_pressure_pa"].map(pa_to_kpa)
        frame["friction_kpa"] = frame["annular_friction_to_surface_pa"].map(pa_to_kpa)
    st.dataframe(frame, use_container_width=True)
