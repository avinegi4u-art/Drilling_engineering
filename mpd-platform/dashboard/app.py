"""MPD Hydraulics Dashboard.

Engineering decision support only. This UI does not control field equipment.
"""

from __future__ import annotations

import streamlit as st
from mpd_engine.constants import VERSION_1_ASSUMPTIONS

from components.api_client import APIError
from components.ui import bootstrap_ui

st.set_page_config(
    page_title="MPD Hydraulics Dashboard",
    page_icon="🛢️",
    layout="wide",
)

client = bootstrap_ui()

st.title("MPD Hydraulics Dashboard")
st.caption(
    "Steady-state, single-phase Bingham Plastic screening model. "
    "Not an automated choke controller."
)

try:
    health = client.health()
    st.success(f"API {st.session_state.api_base_url} — {health.get('status', 'ok')}")
except APIError as exc:
    st.error(str(exc))
    st.info("Start the API with `make api` or Docker Compose, then set the URL on the Settings page.")

st.header("Version 1 assumptions")
for item in VERSION_1_ASSUMPTIONS:
    st.markdown(f"- {item}")

st.header("How to use")
st.markdown(
    """
1. **Well Setup** — create or select a well and enter geometry.
2. **Hydraulics** — enter mud and operating conditions, run the calculation, inspect ECD and warnings.
3. **Pressure Window** — overlay pore, collapse, static, dynamic, fracture, and ECD.
4. **Connection Simulator** — compare pump-on and pump-off surface backpressure.
5. **Reports** — download CSV, Excel, and PDF for a completed run.

Use the sidebar to open those pages. All calculations execute in the FastAPI
service, which calls the standalone `mpd_engine` package. This UI only
converts display units and does not re-implement hydraulics.
"""
)
