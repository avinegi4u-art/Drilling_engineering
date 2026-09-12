"""HTTP client for the FastAPI backend.

All hydraulics run on the server via ``mpd_engine``. This module only
transports JSON and files.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")


class APIError(RuntimeError):
    """Raised when the API returns a non-success status."""


class MPDClient:
    """Small synchronous client used by Streamlit pages."""

    def __init__(self, base_url: str | None = None, timeout_s: float = 60.0) -> None:
        self.base_url = (base_url or DEFAULT_API_BASE_URL).rstrip("/")
        self.timeout_s = timeout_s

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.request(method, url, timeout=self.timeout_s, **kwargs)
        except httpx.HTTPError as exc:
            raise APIError(f"Cannot reach API at {url}: {exc}") from exc
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise APIError(f"API {response.status_code} for {path}: {payload}")
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.content

    def health(self) -> dict[str, str]:
        return self._request("GET", "/health")

    def create_well(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/wells", json=payload)

    def list_wells(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/wells")

    def get_well(self, well_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/wells/{well_id}")

    def create_scenario(self, well_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", f"/api/v1/wells/{well_id}/scenarios", json=payload)

    def list_scenarios(self, well_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/api/v1/wells/{well_id}/scenarios")

    def get_scenario(self, scenario_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/scenarios/{scenario_id}")

    def calculate(self, scenario_id: str) -> dict[str, Any]:
        return self._request("POST", f"/api/v1/scenarios/{scenario_id}/calculate", json={})

    def list_runs(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/runs")

    def get_run(self, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/runs/{run_id}")

    def get_results(self, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/runs/{run_id}/results")

    def export_csv(self, run_id: str) -> bytes:
        return self._request("POST", f"/api/v1/runs/{run_id}/export/csv")

    def export_excel(self, run_id: str) -> bytes:
        return self._request("POST", f"/api/v1/runs/{run_id}/export/excel")

    def export_pdf(self, run_id: str) -> bytes:
        return self._request("POST", f"/api/v1/runs/{run_id}/export/pdf")
