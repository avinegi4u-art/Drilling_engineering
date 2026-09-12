"""Reports page."""

from __future__ import annotations

import streamlit as st
from mpd_engine.units.conversions import pa_to_kpa

from components.api_client import APIError, MPDClient
from components.tables import show_warnings

st.set_page_config(page_title="Reports", layout="wide")
st.title("Reports")
st.caption("Download engineering-review files for a completed calculation.")

client = MPDClient(st.session_state.get("api_base_url"))
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
choice = st.selectbox("Completed calculation", list(labels))
run_id = labels[choice]
run = client.get_run(run_id)
results = client.get_results(run_id)

st.subheader("Assumptions")
for item in results["assumptions"]:
    st.markdown(f"- {item}")

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

st.download_button("CSV", data=client.export_csv(run_id), file_name=f"{run_id}.csv")
st.download_button("Excel", data=client.export_excel(run_id), file_name=f"{run_id}.xlsx")
st.download_button("PDF report", data=client.export_pdf(run_id), file_name=f"{run_id}.pdf")
