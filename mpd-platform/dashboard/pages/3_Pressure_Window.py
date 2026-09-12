"""Pressure Window page."""

from __future__ import annotations

import streamlit as st

from components.api_client import APIError
from components.charts import pressure_window_figure
from components.tables import show_assumptions, show_warnings
from components.ui import bootstrap_ui, fetch_selected_results

st.set_page_config(page_title="Pressure Window", layout="wide")
st.title("Pressure Window")
st.caption("Depth increases downward. Overlay is for engineering review only.")

client = bootstrap_ui()
results = fetch_selected_results(client)

if not results:
    st.info("Run a hydraulics case first so a depth profile exists.")
    st.stop()

show_assumptions(results.get("assumptions"))
st.plotly_chart(pressure_window_figure(results["profile"]), width="stretch")
st.metric("Window status at TD", results["summary"]["window_status"])
st.subheader("Window warnings")
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

run_id = st.session_state.get("run_id")
if run_id:
    try:
        csv_bytes = client.export_csv(run_id)
        xlsx_bytes = client.export_excel(run_id)
    except APIError as exc:
        st.error(str(exc))
    else:
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("Download CSV", data=csv_bytes, file_name=f"{run_id}.csv")
        with d2:
            st.download_button("Download Excel", data=xlsx_bytes, file_name=f"{run_id}.xlsx")
