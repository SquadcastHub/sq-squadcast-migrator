"""Main OpsGenie API client."""

from typing import Optional

from .http import HTTPClient
from .resources.users import UsersClient
from .resources.teams import TeamsClient
from .resources.schedules import SchedulesClient
from .resources.escalation_policies import EscalationPoliciesClient


class OpsgenieAPIClient:
    """Client for the OpsGenie API."""

    DEFAULT_API_URL = "https://api.opsgenie.com/v2"

    def __init__(self, api_key: str, api_url: Optional[str] = None):
        """
        Initialize OpsGenie API client.

        Args:
            api_key: OpsGenie API key
            api_url: Optional API URL (defaults to production API)
        """
        self.http = HTTPClient(api_key=api_key, api_url=api_url or self.DEFAULT_API_URL)

        # Initialize resource clients
        self.users = UsersClient(self.http)
        self.teams = TeamsClient(self.http)
        self.schedules = SchedulesClient(self.http)
        self.escalation_policies = EscalationPoliciesClient(self.http)

    def __enter__(self) -> "OpsgenieAPIClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the client and its underlying HTTP session."""
        self.http.close()
