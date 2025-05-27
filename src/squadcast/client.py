import requests
from typing import Dict, Any, Optional, List
import logging
from config.config import settings

logger = logging.getLogger(__name__)


class SquadcastClient:
    """Client for the Squadcast API."""

    def __init__(
        self, refresh_token: Optional[str] = None, api_url: Optional[str] = None
    ):
        """
        Initialize Squadcast client.

        Args:
            refresh_token: Squadcast refresh token. If not provided, will use from settings.
            api_url: Squadcast API URL. If not provided, will use from settings.
        """
        self.refresh_token = refresh_token or settings.squadcast_refresh_token
        self.api_url = api_url or settings.squadcast_api_url
        self.auth_url = settings.squadcast_auth_url
        self.access_token = None

        if not self.refresh_token:
            logger.error("Squadcast refresh token not provided")
            raise ValueError("Squadcast refresh token is required")

    def _get_access_token(self) -> str:
        logger.info("Getting Squadcast access token")

        try:
            headers = {
                "X-Refresh-Token": self.refresh_token,
                "Content-Type": "application/json",
            }

            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()

            auth_data = response.json().get("data", {})
            access_token = auth_data.get("access_token")

            if not access_token:
                raise ValueError("Access token not found in the response")

            logger.debug("Successfully obtained access token")
            return access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing token response: {str(e)}")
            raise

    def _make_request(
        self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None
    ) -> Dict:
        if not self.access_token:
            self.access_token = self._get_access_token()

        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method, url=url, headers=headers, params=params, json=json_data
        )

        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise

    # Define methods for creating users, teams, escalation policies, etc.
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(
            f"Creating user in Squadcast: {user_data.get('first_name', 'Unknown')} {user_data.get('last_name', 'Unknown')} - ({user_data.get('email', 'Unknown')})"
        )
        if settings.dry_run:
            logger.info("DRY RUN: Would create user in Squadcast")
            return {
                "id": "mock_user_id",
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "email": user_data.get("email"),
                "dry_run": True,
            }

        response = self._make_request("POST", "/v3/users", json_data=user_data)
        return response.get("data", {})

    def get_all_teams(self) -> List[Dict[str, Any]]:
        logger.info("Fetching all teams from Squadcast")
        response = self._make_request("GET", "teams")
        return response.get("data", [])

    def create_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Creating team in Squadcast: {team_data.get('name', 'Unknown')}")
        if settings.dry_run:
            logger.info("DRY RUN: Would create team in Squadcast")
            return {
                "id": "mock_team_id",
                "name": team_data.get("name"),
                "description": team_data.get("description"),
                "members": team_data.get("members", []),
                "dry_run": True,
            }

        response = self._make_request("POST", "/v3/teams", json_data=team_data)
        return response.get("data", {})

    def create_squad(
        self, team: Dict[str, Any], squad_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        squad_data["owner_id"] = team.get("id")
        logger.info(
            f"Creating squad '{squad_data.get('name', 'Unknown')}' in {team.get('name', 'Unknown')} {squad_data}"
        )
        if settings.dry_run:
            logger.info("DRY RUN: Would create squad in team")
            return {
                "id": "mock_squad_id",
                "name": squad_data.get("name"),
                "dry_run": True,
            }

        response = self._make_request("POST", "/v4/squads", json_data=squad_data)
        return response.get("data", {})

    # Add other methods as needed
