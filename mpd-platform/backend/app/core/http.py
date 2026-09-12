"""HTTP status aliases used by the API."""

from fastapi import status

# Starlette renamed 422; getattr default args are eager, so branch explicitly.
if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT"):
    UNPROCESSABLE = status.HTTP_422_UNPROCESSABLE_CONTENT
else:
    UNPROCESSABLE = status.HTTP_422_UNPROCESSABLE_ENTITY
