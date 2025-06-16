"""Team resource client."""

from typing import List

from .base import BaseResource
from ..models.team import OpsGenieTeam


class TeamsClient(BaseResource[OpsGenieTeam]):
    """Client for team operations."""

    def __init__(self, http_client):
        """Initialize teams client."""
        super().__init__(http_client, OpsGenieTeam)

    def list_teams(self) -> List[OpsGenieTeam]:
        """
        Get all teams.

        Returns:
            List of OpsGenieTeam objects
        """
        params = {"sort": "name", "order": "ASC"}
        return self._get_all("teams", params=params)

    def get_team(self, team_id: str) -> OpsGenieTeam:
        """
        Get a specific team by ID.

        Args:
            team_id: ID of the team to retrieve

        Returns:
            OpsGenieTeam object with complete details including members
        """
        return self._get_single(f"teams/{team_id}")
