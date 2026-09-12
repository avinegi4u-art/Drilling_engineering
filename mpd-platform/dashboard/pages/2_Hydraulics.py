"""Hydraulics page."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from mpd_engine.units.conversions import kpa_to_pa, m3_s_to_lpm, pa_to_kpa

from components.api_client import APIError, MPDClient
from components.charts import ecd_figure, friction_profile_figure, pressure_profile_figure
from components.forms import drillstring_form, fluid_form, operating_form, pressure_window_form
from components.tables import show_profile, show_warnings

st.set_page_config(page_title="Hydraulics", layout="wide")
st.title("Hydraulics")
st.caption("Calculations run through FastAPI and `mpd_engine`. Equations are not in this page.")

client = MPDClient(st.session_state.get("api_base_url"))

try:
    wells = client.list_wells()
except APIError as exc:
    st.error(str(exc))
    st.stop()

if not wells:
    st.warning("Create a well on the Well Setup page first.")
    st.stop()

labels = {f"{item['name']} ({item['id'][:8]})": item["id"] for item in wells}
well_label = st.selectbox("Well", list(labels))
well_id = labels[well_label]
well = client.get_well(well_id)
td_m = float(well["well"]["sections"][-1]["md_bottom_m"])
st.session_state.well_id = well_id

col_left, col_right = st.columns(2)
with col_left:
    scenario_name = st.text_input("Scenario name", value="drilling-case")
    drillstring = drillstring_form(td_m)
    fluid = fluid_form()
with col_right:
    operating = operating_form()
    target_kpa = st.number_input("Target BHP, kPa (optional, 0 = unused)", min_value=0.0, value=0.0)
    uploaded = st.file_uploader("Optional pressure-window CSV", type=["csv"])
    window_df = pd.read_csv(uploaded) if uploaded is not None else None
    window = pressure_window_form(window_df)

if st.button("Run calculation", type="primary"):
    payload = {
        "name": scenario_name,
        "drillstring": drillstring,
        "fluid": fluid,
        "operating": operating,
        "pressure_window": window,
        "depth_step_m": 50.0,
    }
    if target_kpa > 0:
        payload["target_bottomhole_pressure_pa"] = kpa_to_pa(float(target_kpa))
    try:
        scenario = client.create_scenario(well_id, payload)
        run = client.calculate(scenario["id"])
        results = client.get_results(run["id"])
    except APIError as exc:
        st.error(str(exc))
    else:
        st.session_state.scenario_id = scenario["id"]
        st.session_state.run_id = run["id"]
        st.session_state.results = results
        st.success(f"Run {run['id']} completed ({run['calculation_version']})")

results = st.session_state.get("results")
if not results:
    st.info("Run a calculation to see metrics and charts.")
    st.stop()

summary = results["summary"]
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("BHP, kPa", f"{pa_to_kpa(summary['bottomhole_pressure_pa']):.0f}")
m2.metric("Hydrostatic, kPa", f"{pa_to_kpa(summary['hydrostatic_pressure_pa']):.0f}")
m3.metric("Friction, kPa", f"{pa_to_kpa(summary['annular_friction_pressure_pa']):.0f}")
m4.metric("SBP, kPa", f"{pa_to_kpa(summary['surface_backpressure_pa']):.0f}")
ecd = summary.get("ecd_kg_m3")
m5.metric("ECD, kg/m³", "n/a" if ecd is None else f"{ecd:.1f}")
st.caption(
    f"Mode {summary['operating_mode']} · flow {m3_s_to_lpm(summary['flow_rate_m3_s']):.0f} L/min · "
    f"window {summary['window_status']}"
)

profile = results["profile"]
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(pressure_profile_figure(profile), use_container_width=True)
with c2:
    st.plotly_chart(friction_profile_figure(profile), use_container_width=True)
st.plotly_chart(ecd_figure(profile), use_container_width=True)

st.subheader("Warnings")
show_warnings(results["warnings"])
st.subheader("Profile")
show_profile(profile)

run_id = st.session_state.get("run_id")
if run_id:
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Download CSV", data=client.export_csv(run_id), file_name=f"{run_id}.csv")
    with d2:
        st.download_button(
            "Download Excel",
            data=client.export_excel(run_id),
            file_name=f"{run_id}.xlsx",
        )
