"""Client helpers that do not need a running Streamlit server."""

from __future__ import annotations

from components.api_client import format_api_error


def test_format_structured_error() -> None:
    message = format_api_error(
        404,
        "/api/v1/wells/x",
        {"error": {"code": "NOT_FOUND", "message": "Well not found"}},
    )
    assert message == "NOT_FOUND: Well not found"


def test_format_validation_list() -> None:
    message = format_api_error(
        422,
        "/api/v1/wells",
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": [{"loc": ["body", "name"], "msg": "Field required"}],
            }
        },
    )
    assert "VALIDATION_ERROR" in message
    assert "name" in message
    assert "Field required" in message
