"""MPD Hydraulics Dashboard. Streamlit UI is implemented in Phase 5."""

import streamlit as st

st.set_page_config(page_title="MPD Hydraulics Dashboard", layout="wide")
st.title("MPD Hydraulics Dashboard")
st.info(
    "Phase 1 is in progress: domain models and unit conversions are available "
    "in the calculation engine. The interactive dashboard is added in Phase 5."
)
st.caption("Engineering decision support only. This application does not control field equipment.")
