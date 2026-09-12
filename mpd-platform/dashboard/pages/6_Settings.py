"""Settings page."""

from __future__ import annotations

import streamlit as st

from components.api_client import APIError, DEFAULT_API_BASE_URL, MPDClient

st.set_page_config(page_title="Settings", layout="wide")
st.title("Settings")

url = st.text_input("API base URL", value=st.session_state.get("api_base_url", DEFAULT_API_BASE_URL))
if st.button("Save API URL"):
    st.session_state.api_base_url = url.rstrip("/")
    st.success(f"Saved {st.session_state.api_base_url}")

client = MPDClient(st.session_state.get("api_base_url", url))
try:
    health = client.health()
    st.success(f"Health: {health}")
except APIError as exc:
    st.error(str(exc))

st.markdown(
    """
Version 1 does not implement authentication, WITSML, background queues, or
equipment control. Failed calculations return API errors instead of default
numeric results.
"""
)
