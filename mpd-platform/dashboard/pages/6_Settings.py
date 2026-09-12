"""Settings page."""

from __future__ import annotations

import streamlit as st

from components.api_client import APIError, DEFAULT_API_BASE_URL, DEFAULT_API_TIMEOUT_S
from components.ui import bootstrap_ui

st.set_page_config(page_title="Settings", layout="wide")
st.title("Settings")

bootstrap_ui()

url = st.text_input("API base URL", value=st.session_state.get("api_base_url", DEFAULT_API_BASE_URL))
timeout_s = st.number_input(
    "API timeout, s",
    min_value=1.0,
    max_value=300.0,
    value=float(st.session_state.get("api_timeout_s", DEFAULT_API_TIMEOUT_S)),
    step=5.0,
)
if st.button("Save API connection"):
    st.session_state.api_base_url = url.rstrip("/")
    st.session_state.api_timeout_s = float(timeout_s)
    st.success(f"Saved {st.session_state.api_base_url} (timeout {timeout_s:.0f} s)")
    st.rerun()

client = bootstrap_ui()
try:
    health = client.health()
    st.success(f"Health: {health}")
except APIError as exc:
    st.error(str(exc))

st.markdown(
    """
Version 1 does not implement authentication, WITSML, background queues, real-time
streaming, or equipment control. Failed calculations return API errors instead of
default numeric results. Session state stores only UI selections (well, scenario,
run, API URL, timeout).
"""
)
