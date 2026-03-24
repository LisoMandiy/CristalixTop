from __future__ import annotations

from typing import Any


class CristalixError(Exception):
    """Base exception for all Cristalix API errors."""


class CristalixValidationError(CristalixError):
    """Raised when client-side validation fails."""


class CristalixProtocolError(CristalixError):
    """Raised when server responds with an unsupported HTTP protocol."""


class CristalixHTTPError(CristalixError):
    def __init__(self, message: str, *, status_code: int, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class CristalixRateLimitError(CristalixHTTPError):
    """Raised on HTTP 429."""
