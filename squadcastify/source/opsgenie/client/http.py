"""HTTP client for the OpsGenie API."""

import logging
from typing import Dict, Optional, Any
import requests
from requests.exceptions import RequestException
from requests import Session, Response
from .errors import OpsGenieAPIError, ERROR_STATUS_MAP

logger = logging.getLogger(__name__)


class HTTPClient:
    """Makes HTTP requests to OpsGenie API."""

    def __init__(self, api_key: str, api_url: str):
        """
        Initialize HTTP client.

        Args:
            api_key: OpsGenie API key
            api_url: OpsGenie API URL
        """
        self.api_url = api_url.rstrip("/")
        self.session = Session()
        self.session.headers.update(
            {"Authorization": f"GenieKey {api_key}", "Content-Type": "application/json"}
        )

    def _handle_error_response(self, response: Response) -> None:
        """
        Handle error responses from the API.

        Args:
            response: Response object from requests

        Raises:
            OpsGenieAPIError: When the API returns an error
        """
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        message = error_data.get("message", "Unknown error")

        # Get specific error type based on status code or default to base error
        error_cls = ERROR_STATUS_MAP.get(response.status_code, OpsGenieAPIError)

        raise error_cls(
            status_code=response.status_code, message=message, response_data=error_data
        )

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the OpsGenie API.

        Args:
            method: HTTP method
            endpoint: API endpoint (without leading slash)
            params: Query parameters
            json: JSON body data

        Returns:
            Response data as dictionary

        Raises:
            OpsGenieAPIError: When the API returns an error
            RequestException: For network/connection errors
        """
        url = f"{self.api_url}/{endpoint}"

        logger.debug(
            "Making request: %s %s (params=%s, json=%s)", method, url, params, json
        )

        try:
            response = self.session.request(
                method=method, url=url, params=params, json=json
            )

            if not response.ok:
                self._handle_error_response(response)

            if response.status_code == 204:  # No content
                return {}

            return response.json()

        except RequestException as e:
            logger.error("Request failed: %s", str(e))
            raise

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
