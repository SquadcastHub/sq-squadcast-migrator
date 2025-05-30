import requests
from typing import Dict, Optional, List
import logging
from config.config import settings
from src.schemas.auth import OauthResponse
from src.schemas.user import CreateUserRequest, CreateUserResponse
from src.schemas.team import CreateTeamRequest, CreateTeamResponse, Team
from src.schemas.squad import CreateSquadRequest, CreateSquadResponse
from src.schemas.api import ErrorResponse

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
            auth_response = OauthResponse(**auth_data)

            if not auth_response.access_token:
                raise ValueError("Access token not found in the response")

            logger.debug("Successfully obtained access token")
            return auth_response.access_token

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

        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer 1{self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                method=method, url=url, headers=headers, params=params, json=json_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            error_response = ErrorResponse(**e.response.json())
            logger.error(f"Squadcast API error (status: {error_response.meta.status}): {error_response.meta.error_message}")
            raise e
        except ValueError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            return {}

    # Define methods for creating users, teams, escalation policies, etc.
    def create_user(self, user_data: CreateUserRequest) -> CreateUserResponse:
        logger.info(
            f"Creating user in Squadcast: {user_data.first_name} {user_data.last_name} - ({user_data.email})"
        )
        if settings.dry_run:
            logger.info("DRY RUN: Would create user in Squadcast")
            return CreateUserResponse(
                id="mock_id",
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role
            )

        try:
            response = self._make_request("POST", "/v3/users", json_data=user_data)
            return CreateUserResponse(**response.get("data", {}))
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_all_teams(self) -> List[Team]:
        logger.info("Fetching all teams from Squadcast")
        try:
            response = self._make_request("GET", "/v3/teams")
            teams_data = response.get("data", [])
            return [Team(**team) for team in teams_data]
        except Exception as e:
            logger.error(f"Failed to fetch teams: {e}")
            raise e

    def create_team(self, team_data: CreateTeamRequest) -> CreateTeamResponse:
        logger.info(f"Creating team in Squadcast: {team_data.name}")
        if settings.dry_run:
            logger.info("DRY RUN: Would create team in Squadcast")
            return CreateTeamResponse(
                id="mock_team_id",
                name=team_data.name,
                description=team_data.description,
                dry_run=True,
            )

        try:
            response = self._make_request("POST", "/v3/teams", json_data=team_data)
            return CreateTeamResponse(**response.get("data", {}))
        except Exception as e:
            logger.error(f"Failed to create team: {e}")
            raise e

    def create_squad(
        self, team: Team, squad_data: CreateSquadRequest
    ) -> CreateSquadResponse:
        squad_data.owner_id = team.id
        logger.info(
            f"Creating squad '{squad_data.name}' in {team.name} {squad_data}"
        )
        if settings.dry_run:
            logger.info("DRY RUN: Would create squad in team")
            return CreateSquadResponse(
                id="mock_squad_id",
                name=squad_data.name,
                owner_id=team.id,
                members=squad_data.members,
                dry_run=True,
            )

        try:
            response = self._make_request("POST", "/v4/squads", json_data=squad_data)
            return CreateSquadResponse(**response.get("data", {}))
        except Exception as e:
            logger.error(f"Failed to create squad: {e}")
            raise e

    # Add other methods as needed
