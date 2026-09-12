"""Connection Simulator page.

Version 1 compares pump-on and pump-off steady states. It does not control
chokes or other field equipment.
"""

from __future__ import annotations

import streamlit as st
from mpd_engine.units.conversions import kpa_to_pa, lpm_to_m3_s, pa_to_kpa

from components.api_client import APIError
from components.charts import connection_comparison_figure
from components.tables import show_assumptions, show_warnings
from components.ui import bootstrap_ui, fetch_selected_results

st.set_page_config(page_title="Connection Simulator", layout="wide")
st.title("Connection Simulator")
st.warning(
    "Steady-state comparison only. This page does not send commands to a choke "
    "or any field equipment."
)

client = bootstrap_ui()
results = fetch_selected_results(client)
if not results:
    st.info("Run a hydraulics case with circulating flow first.")
    st.stop()

show_assumptions(results.get("assumptions"))
connection = results.get("connection")
summary = results["summary"]

st.subheader("Current run (from API)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Pump-on BHP, kPa", f"{pa_to_kpa(summary['bottomhole_pressure_pa']):.0f}")
c2.metric("Friction lost on pump-off, kPa", f"{pa_to_kpa(summary['annular_friction_pressure_pa']):.0f}")
if connection:
    c3.metric("Required SBP pump-off, kPa", f"{pa_to_kpa(connection['required_sbp_pump_off_pa']):.0f}")
    c4.metric(
        "SBP limit exceeded",
        "Yes" if connection.get("sbp_limit_exceeded") else "No",
    )
    st.plotly_chart(connection_comparison_figure(connection), use_container_width=True)
    if connection.get("sbp_limit_exceeded"):
        st.error(
            "Required connection SBP exceeds the configured review limit. "
            "This is an engineering-review flag, not a control command."
        )
    st.subheader("Connection warnings")
    show_warnings(connection.get("warnings") or [])
else:
    st.info("This run has no connection comparison payload.")

st.subheader("What-if pump-on flow")
st.caption("Creates a new scenario on the selected well using the last inputs with a new flow.")
flow_lpm = st.number_input("Pump-on flow, L/min", min_value=0.0, value=400.0, step=10.0)
sbp_kpa = st.number_input("Pump-on SBP, kPa", min_value=0.0, value=0.0, step=50.0)

if st.button("Recalculate connection pair"):
    well_id = st.session_state.get("well_id")
    scenario_id = st.session_state.get("scenario_id")
    if not well_id or not scenario_id:
        st.error("Select a well and run a hydraulics case first.")
    else:
        try:
            base = client.get_scenario(scenario_id)
            inputs = dict(base["inputs"])
            inputs.pop("well", None)
            operating = dict(inputs["operating"])
            operating["flow_rate_m3_s"] = lpm_to_m3_s(float(flow_lpm))
            operating["surface_backpressure_pa"] = kpa_to_pa(float(sbp_kpa))
            operating["operating_mode"] = "pump_on"
            payload = {
                "name": f"connection-pump-on-{flow_lpm:.0f}lpm",
                "drillstring": inputs["drillstring"],
                "fluid": inputs["fluid"],
                "operating": operating,
                "pressure_window": inputs["pressure_window"],
                "target_bottomhole_pressure_pa": inputs.get("target_bottomhole_pressure_pa"),
                "depth_step_m": inputs.get("depth_step_m", 50.0),
            }
            scenario = client.create_scenario(well_id, payload)
            run = client.calculate(scenario["id"])
            st.session_state.scenario_id = scenario["id"]
            st.session_state.run_id = run["id"]
            st.success("Updated pump-on case from the API.")
            st.rerun()
        except APIError as exc:
            st.error(str(exc))
