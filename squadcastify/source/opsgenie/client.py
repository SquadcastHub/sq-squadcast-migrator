import logging
from typing import Any, Dict, List, Optional, Union

import requests

from source.schema.squad import CreateSquadRequest, SquadMember
from source.alerting_client import AlertingClient
from terraform.models import SquadcastTeam

logger = logging.getLogger(__name__)


def get_services() -> List[Dict[str, Any]]:
    logger.warning("Services feature is not supported in OpsGenie")
    return []


class OpsGenieClient(AlertingClient):
    """Client for the OpsGenie API."""

    def __init__(self, api_key: Optional[str], api_url: Optional[str]):
        """
        Initialize OpsGenie client.

        Args:
            api_key: OpsGenie API key. If not provided, will use from settings.
            api_url: OpsGenie API URL. If not provided, will use from settings.
        """
        self.__api_key = api_key
        self.__api_url = api_url
        self.__headers = {
            "Authorization": f"GenieKey {self.__api_key}",
            "Content-Type": "application/json",
        }

        if not self.__api_key:
            logger.error("OpsGenie API key not provided")
            raise ValueError("OpsGenie API key is required")

    def _make_request(
        self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None
    ) -> Dict:
        url = f"{self.__api_url}/{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.__headers,
            params=params,
            json=json_data,
        )

        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response content: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise

    def get_users(self) -> List[Dict[str, Any]]:
        logger.info("Fetching users from OpsGenie")
        all_users = []
        limit = 100
        offset = 0

        while True:
            params = {
                "limit": limit,
                "offset": offset,
                "order": "ASC",
                "sort": "username",
            }
            response = self._make_request("GET", "users", params=params)
            users = response.get("data", [])
            all_users.extend(users)

            if len(users) < limit:
                break

            offset += limit

        return all_users

    def transform_team(
        self,
        og_team: Dict[str, Any],
        user_migration_map: Dict[str, str] = None,
        migration_mode: str = "separate_teams",
    ) -> Union[SquadcastTeam, CreateSquadRequest]:
        sq_members = []

        if og_team.get("members") and user_migration_map:
            for og_member in og_team.get("members", []):
                og_user_id = og_member.get("user", {}).get("id")
                if not og_user_id or og_user_id not in user_migration_map:
                    logger.warning(
                        f"User {og_member.get('user', {}).get('username')} not found in migration map, skipping"
                    )
                    continue

                if migration_mode == "separate_teams":
                    sq_members.append(user_migration_map[og_user_id])
                elif migration_mode == "squads_in_team":
                    sq_members.append(
                        SquadMember(user_id=user_migration_map[og_user_id])
                    )

        name = og_team.get("name", "")

        if migration_mode == "separate_teams":
            return SquadcastTeam(
                name=name,
                description=og_team.get("description", ""),
                members=sq_members,
            )
        elif migration_mode == "squads_in_team":
            return CreateSquadRequest(name=name, members=sq_members)
        raise ValueError(f"Unknown migration mode: {migration_mode}")

    def get_teams(self) -> List[Dict[str, Any]]:
        logger.info("Fetching teams from OpsGenie")
        response = self._make_request("GET", "teams")
        return response.get("data", [])

    def get_team_details(self, team_id: str) -> Dict[str, Any]:
        logger.info(f"Fetching details for team ID: {team_id}")
        response = self._make_request("GET", f"teams/{team_id}")
        team_data = response.get("data", {})
        return team_data

    def get_escalation_policies(self) -> List[Dict[str, Any]]:
        logger.info("Fetching escalation policies from OpsGenie")
        return []

    def get_schedules(self) -> List[Dict[str, Any]]:
        logger.info("Fetching schedules from OpsGenie")
        return []

    # Add more methods as needed
