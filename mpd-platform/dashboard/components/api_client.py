"""HTTP client for the FastAPI backend.

All hydraulics run on the server via ``mpd_engine``. This module only
transports JSON and files. It does not implement engineering equations.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_API_TIMEOUT_S = float(os.environ.get("API_TIMEOUT_S", "60"))


class APIError(RuntimeError):
    """Raised when the API is unreachable or returns a non-success status."""


def format_api_error(status_code: int, path: str, payload: Any) -> str:
    """Turn a structured FastAPI error envelope into a readable message."""
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            code = str(err.get("code") or "HTTP_ERROR")
            message = err.get("message", "")
            if isinstance(message, list):
                parts = []
                for item in message:
                    if isinstance(item, dict):
                        loc = ".".join(str(part) for part in item.get("loc", ()))
                        parts.append(f"{loc}: {item.get('msg', item)}" if loc else str(item.get("msg", item)))
                    else:
                        parts.append(str(item))
                message = "; ".join(parts)
            return f"{code}: {message}"
    return f"API {status_code} for {path}: {payload}"


class MPDClient:
    """Small synchronous client used by Streamlit pages."""

    def __init__(self, base_url: str | None = None, timeout_s: float = DEFAULT_API_TIMEOUT_S) -> None:
        self.base_url = (base_url or DEFAULT_API_BASE_URL).rstrip("/")
        self.timeout_s = timeout_s

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.request(method, url, timeout=self.timeout_s, **kwargs)
        except httpx.TimeoutException as exc:
            raise APIError(
                f"API timed out after {self.timeout_s:.0f}s at {url}. "
                "Check that the FastAPI service is running."
            ) from exc
        except httpx.HTTPError as exc:
            raise APIError(f"Cannot reach API at {url}: {exc}") from exc
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise APIError(format_api_error(response.status_code, path, payload))
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
