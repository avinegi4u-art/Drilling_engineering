"""Reports page."""

from __future__ import annotations

import streamlit as st
from mpd_engine.units.conversions import pa_to_kpa

from components.api_client import APIError
from components.tables import show_assumptions, show_warnings
from components.ui import bootstrap_ui

st.set_page_config(page_title="Reports", layout="wide")
st.title("Reports")
st.caption("Download engineering-review files for a completed calculation.")

client = bootstrap_ui()
try:
    runs = client.list_runs()
except APIError as exc:
    st.error(str(exc))
    st.stop()

completed = [run for run in runs if run["status"] == "completed"]
if not completed:
    st.info("No completed runs yet.")
    st.stop()

labels = {
    f"{item['id'][:8]} · {item['calculation_version']} · {item['status']}": item["id"]
    for item in completed
}
keys = list(labels)
default_index = 0
current = st.session_state.get("run_id")
if current in labels.values():
    default_index = keys.index(next(key for key, value in labels.items() if value == current))
choice = st.selectbox("Completed calculation", keys, index=default_index)
run_id = labels[choice]
st.session_state.run_id = run_id

try:
    results = client.get_results(run_id)
except APIError as exc:
    st.error(str(exc))
    st.stop()

show_assumptions(results.get("assumptions"))

st.subheader("Summary")
summary = results["summary"]
st.json(
    {
        "tvd_m": summary["tvd_m"],
        "bhp_kpa": pa_to_kpa(summary["bottomhole_pressure_pa"]),
        "hydrostatic_kpa": pa_to_kpa(summary["hydrostatic_pressure_pa"]),
        "friction_kpa": pa_to_kpa(summary["annular_friction_pressure_pa"]),
        "sbp_kpa": pa_to_kpa(summary["surface_backpressure_pa"]),
        "ecd_kg_m3": summary.get("ecd_kg_m3"),
        "window_status": summary["window_status"],
        "mode": summary["operating_mode"],
    }
)

st.subheader("Warnings")
show_warnings(results["warnings"])

try:
    csv_bytes = client.export_csv(run_id)
    xlsx_bytes = client.export_excel(run_id)
    pdf_bytes = client.export_pdf(run_id)
except APIError as exc:
    st.error(str(exc))
else:
    st.download_button("CSV", data=csv_bytes, file_name=f"{run_id}.csv")
    st.download_button("Excel", data=xlsx_bytes, file_name=f"{run_id}.xlsx")
    st.download_button("PDF report", data=pdf_bytes, file_name=f"{run_id}.pdf")
