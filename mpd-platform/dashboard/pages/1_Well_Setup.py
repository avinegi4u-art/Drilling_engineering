"""Well Setup page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.api_client import APIError
from components.forms import well_geometry_form
from components.ui import bootstrap_ui

st.set_page_config(page_title="Well Setup", layout="wide")
st.title("Well Setup")
st.caption("Create a vertical well. Geometry is stored in SI metres on the server.")

client = bootstrap_ui()

try:
    wells = client.list_wells()
except APIError as exc:
    st.error(str(exc))
    wells = []

if wells:
    labels = {f"{item['name']} ({item['id'][:8]})": item["id"] for item in wells}
    default_index = 0
    current = st.session_state.get("well_id")
    keys = list(labels)
    if current in labels.values():
        default_index = keys.index(next(key for key, value in labels.items() if value == current))
    selected = st.selectbox("Existing wells", keys, index=default_index)
    st.session_state.well_id = labels[selected]
    try:
        detail = client.get_well(st.session_state.well_id)
        st.json(detail["well"])
    except APIError as exc:
        st.error(str(exc))
else:
    st.info("No wells yet. Create one below.")

st.divider()
payload = well_geometry_form()
uploaded = st.file_uploader(
    "Optional trajectory CSV (columns: md_m, tvd_m). Version 1 still uses a vertical well if omitted.",
    type=["csv"],
)
if uploaded is not None:
    frame = pd.read_csv(uploaded)
    st.dataframe(frame)
    if {"md_m", "tvd_m"}.issubset(frame.columns):
        payload["trajectory"] = [
            {"md_m": float(row.md_m), "tvd_m": float(row.tvd_m), "inclination_deg": 0.0}
            for row in frame.itertuples()
        ]

if st.button("Create well", type="primary"):
    try:
        created = client.create_well(payload)
    except APIError as exc:
        st.error(str(exc))
    else:
        st.session_state.well_id = created["id"]
        st.success(f"Created well {created['name']} ({created['id']})")
        st.json(created["well"])
        st.rerun()
