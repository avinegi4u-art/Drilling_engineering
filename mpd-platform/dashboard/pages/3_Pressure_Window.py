"""Pressure Window page."""

from __future__ import annotations

import streamlit as st

from components.api_client import APIError, MPDClient
from components.charts import pressure_window_figure
from components.tables import show_warnings

st.set_page_config(page_title="Pressure Window", layout="wide")
st.title("Pressure Window")
st.caption("Depth increases downward. Overlay is for engineering review only.")

client = MPDClient(st.session_state.get("api_base_url"))
results = st.session_state.get("results")
run_id = st.session_state.get("run_id")

if results is None and run_id:
    try:
        results = client.get_results(run_id)
        st.session_state.results = results
    except APIError as exc:
        st.error(str(exc))

if not results:
    st.info("Run a hydraulics case first so a depth profile exists.")
    st.stop()

st.plotly_chart(pressure_window_figure(results["profile"]), use_container_width=True)
st.metric("Window status at TD", results["summary"]["window_status"])
show_warnings(
    [
        item
        for item in results["warnings"]
        if item.get("code")
        in {
            "BELOW_PORE_PRESSURE",
            "ABOVE_FRACTURE_PRESSURE",
            "ABOVE_COLLAPSE_LIMIT",
            "WINDOW_TVD_OUT_OF_RANGE",
        }
    ]
)
