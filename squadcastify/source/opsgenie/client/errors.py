"""Exceptions for the OpsGenie client."""

from typing import Dict, Any, Optional


class OpsGenieError(Exception):
    """Base error for OpsGenie client."""

    pass


class OpsGenieAPIError(OpsGenieError):
    """API returned an error response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(f"API Error {status_code}: {message}")


class OpsGenieNotFoundError(OpsGenieAPIError):
    """Resource not found."""

    pass


class OpsGenieAuthenticationError(OpsGenieAPIError):
    """Authentication failed."""

    pass


class OpsGenieRateLimitError(OpsGenieAPIError):
    """Rate limit exceeded."""

    pass


class OpsGenieValidationError(OpsGenieAPIError):
    """Request validation failed."""

    pass


# Mapping of HTTP status codes to specific error types
ERROR_STATUS_MAP = {
    400: OpsGenieValidationError,
    401: OpsGenieAuthenticationError,
    404: OpsGenieNotFoundError,
    429: OpsGenieRateLimitError,
}
