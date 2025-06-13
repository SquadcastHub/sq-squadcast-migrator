"""User resource client."""

from typing import List

from .base import BaseResource
from ..models.user import OpsGenieUser


class UsersClient(BaseResource[OpsGenieUser]):
    """Client for user operations."""

    def __init__(self, http_client):
        """Initialize users client."""
        super().__init__(http_client, OpsGenieUser)

    def list_users(self) -> List[OpsGenieUser]:
        """
        Get all users.

        Returns:
            List of OpsGenieUser objects
        """
        params = {"sort": "username", "order": "ASC"}
        return self._get_all("users", params=params)

    def get_user(self, user_id: str) -> OpsGenieUser:
        """
        Get a specific user by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            OpsGenieUser object
        """
        return self._get_single(f"users/{user_id}")
