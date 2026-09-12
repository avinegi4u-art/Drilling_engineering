"""Shared Streamlit input helpers. Convert field units to SI before API calls."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from mpd_engine.units.conversions import (
    cp_to_pa_s,
    kpa_to_pa,
    lpm_to_m3_s,
    mm_to_m,
)


def well_geometry_form() -> dict[str, Any]:
    st.subheader("Vertical well geometry")
    name = st.text_input("Well name", value="EXAMPLE-1")
    td_m = st.number_input("TD (MD = TVD), m", min_value=1.0, value=3000.0, step=10.0)
    hole_id_mm = st.number_input("Hole / casing ID, mm", min_value=1.0, value=311.15, step=0.1)
    section = st.selectbox("Annular section type", ["open_hole", "casing"])
    casing_id_mm = None
    if section == "casing":
        casing_id_mm = st.number_input("Casing ID, mm", min_value=1.0, value=220.5, step=0.1)
    payload: dict[str, Any] = {
        "name": name,
        "td_m": float(td_m),
        "hole_id_m": mm_to_m(float(hole_id_mm if section == "open_hole" else casing_id_mm or hole_id_mm)),
        "annular_section_type": section,
    }
    if section == "casing" and casing_id_mm is not None:
        payload["casing_id_m"] = mm_to_m(float(casing_id_mm))
        payload["hole_id_m"] = payload["casing_id_m"]
    return payload


def drillstring_form(default_length_m: float) -> dict[str, Any]:
    st.subheader("Drillstring")
    od_mm = st.number_input("Drillpipe OD, mm", min_value=1.0, value=127.0, step=0.1)
    id_mm = st.number_input("Drillpipe ID, mm", min_value=1.0, value=108.61, step=0.1)
    length_m = st.number_input("String length, m", min_value=1.0, value=default_length_m, step=1.0)
    return {
        "components": [
            {
                "name": "drillpipe",
                "component_type": "drillpipe",
                "od_m": mm_to_m(float(od_mm)),
                "id_m": mm_to_m(float(id_mm)),
                "length_m": float(length_m),
            }
        ]
    }


def fluid_form() -> dict[str, Any]:
    st.subheader("Mud")
    density = st.number_input("Mud density, kg/m³", min_value=500.0, value=1200.0, step=10.0)
    pv_cp = st.number_input("Plastic viscosity, cP", min_value=0.0, value=20.0, step=0.5)
    yp_pa = st.number_input("Yield point, Pa", min_value=0.0, value=9.576, step=0.1)
    temp_c = st.number_input("Temperature, °C", value=50.0, step=1.0)
    return {
        "mud_density_kg_m3": float(density),
        "plastic_viscosity_pa_s": cp_to_pa_s(float(pv_cp)),
        "yield_stress_pa": float(yp_pa),
        "temperature_c": float(temp_c),
        "rheology_model": "bingham_plastic",
    }


def operating_form() -> dict[str, Any]:
    st.subheader("Operating conditions")
    mode = st.selectbox(
        "Operating mode",
        ["drilling", "circulation", "pump_on", "connection", "pump_off"],
    )
    flow_lpm = st.number_input("Flow rate, L/min", min_value=0.0, value=400.0, step=10.0)
    sbp_kpa = st.number_input("Surface backpressure, kPa", min_value=0.0, value=0.0, step=50.0)
    max_sbp_kpa = st.number_input("SBP review limit, kPa", min_value=1.0, value=3447.4, step=50.0)
    if mode in {"connection", "pump_off"}:
        flow_lpm = 0.0
        st.info("Connection and pump-off cases require zero flow in version 1.")
    return {
        "flow_rate_m3_s": lpm_to_m3_s(float(flow_lpm)),
        "surface_backpressure_pa": kpa_to_pa(float(sbp_kpa)),
        "operating_mode": mode,
        "max_surface_backpressure_pa": kpa_to_pa(float(max_sbp_kpa)),
    }


def pressure_window_form(uploaded: pd.DataFrame | None) -> dict[str, Any]:
    st.subheader("Pressure window")
    st.caption("Pressures in the table are kPa. TVD is metres. CSV columns: tvd_m, pore_kpa, collapse_kpa, fracture_kpa.")
    if uploaded is not None:
        points = []
        for _, row in uploaded.iterrows():
            points.append(
                {
                    "tvd_m": float(row["tvd_m"]),
                    "pore_pressure_pa": kpa_to_pa(float(row["pore_kpa"])),
                    "collapse_pressure_pa": kpa_to_pa(float(row["collapse_kpa"]))
                    if "collapse_kpa" in uploaded.columns and pd.notna(row.get("collapse_kpa"))
                    else None,
                    "fracture_pressure_pa": kpa_to_pa(float(row["fracture_kpa"])),
                }
            )
        return {"points": points}
    col_a, col_b = st.columns(2)
    with col_a:
        tvd_1 = st.number_input("Point 1 TVD, m", min_value=0.1, value=100.0)
        pore_1 = st.number_input("Point 1 pore, kPa", min_value=0.1, value=1200.0)
        coll_1 = st.number_input("Point 1 collapse, kPa", min_value=0.1, value=1300.0)
        frac_1 = st.number_input("Point 1 fracture, kPa", min_value=0.1, value=1800.0)
    with col_b:
        tvd_2 = st.number_input("Point 2 TVD, m", min_value=0.1, value=3000.0)
        pore_2 = st.number_input("Point 2 pore, kPa", min_value=0.1, value=36000.0)
        coll_2 = st.number_input("Point 2 collapse, kPa", min_value=0.1, value=38000.0)
        frac_2 = st.number_input("Point 2 fracture, kPa", min_value=0.1, value=54000.0)
    return {
        "points": [
            {
                "tvd_m": float(tvd_1),
                "pore_pressure_pa": kpa_to_pa(float(pore_1)),
                "collapse_pressure_pa": kpa_to_pa(float(coll_1)),
                "fracture_pressure_pa": kpa_to_pa(float(frac_1)),
            },
            {
                "tvd_m": float(tvd_2),
                "pore_pressure_pa": kpa_to_pa(float(pore_2)),
                "collapse_pressure_pa": kpa_to_pa(float(coll_2)),
                "fracture_pressure_pa": kpa_to_pa(float(frac_2)),
            },
        ]
    }
