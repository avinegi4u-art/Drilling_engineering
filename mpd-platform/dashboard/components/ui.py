"""UI-only session helpers.

Streamlit session state stores page selections and API connection settings.
Calculation results are always fetched from FastAPI; they are not cached here.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.api_client import DEFAULT_API_BASE_URL, DEFAULT_API_TIMEOUT_S, APIError, MPDClient


def bootstrap_ui() -> MPDClient:
    """Initialize UI session keys and return an API client."""
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL
    if "api_timeout_s" not in st.session_state:
        st.session_state.api_timeout_s = DEFAULT_API_TIMEOUT_S
    st.session_state.setdefault("well_id", None)
    st.session_state.setdefault("scenario_id", None)
    st.session_state.setdefault("run_id", None)
    return MPDClient(
        st.session_state.api_base_url,
        timeout_s=float(st.session_state.api_timeout_s),
    )


def fetch_selected_results(client: MPDClient) -> dict[str, Any] | None:
    """Load the currently selected run from the API, or None if unset."""
    run_id = st.session_state.get("run_id")
    if not run_id:
        return None
    try:
        return client.get_results(run_id)
    except APIError as exc:
        st.error(str(exc))
        return None
