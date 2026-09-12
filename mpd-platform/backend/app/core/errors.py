"""Structured JSON error bodies and HTTP helpers."""

from __future__ import annotations

from typing import Any, NoReturn

from fastapi import HTTPException


def error_body(code: str, message: Any) -> dict[str, dict[str, Any]]:
    """Return the version-1 error envelope ``{"error": {"code", "message"}}``."""
    return {"error": {"code": code, "message": message}}


def raise_http(status_code: int, code: str, message: str) -> NoReturn:
    """Raise an HTTPException whose detail the app handler can unwrap."""
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})


def not_found(entity: str) -> NoReturn:
    raise_http(404, "NOT_FOUND", f"{entity} not found")


def conflict(message: str) -> NoReturn:
    raise_http(409, "CONFLICT", message)


def unprocessable(code: str, message: str) -> NoReturn:
    from app.core.http import UNPROCESSABLE

    raise_http(UNPROCESSABLE, code, message)
