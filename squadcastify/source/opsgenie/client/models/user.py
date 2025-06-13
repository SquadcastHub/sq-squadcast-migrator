"""User model for OpsGenie API."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from .base import OpsGenieModel


@dataclass
class OpsGenieUser(OpsGenieModel):
    """Represents a user in OpsGenie."""

    username: str
    full_name: str
    role: Optional[str] = None
    time_zone: Optional[str] = None
    locale: Optional[str] = None
    user_address: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    blocked: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpsGenieUser":
        """
        Create a user instance from API response data.

        Args:
            data: Dictionary containing user data from API

        Returns:
            OpsGenieUser instance
        """
        return cls(
            id=data["id"],
            username=data["username"],
            full_name=data.get("fullName", ""),
            role=data.get("role", {}).get("name"),
            time_zone=data.get("timeZone"),
            locale=data.get("locale"),
            user_address=data.get("userAddress"),
            created_at=data.get("createdAt"),
            blocked=data.get("blocked", False),
        )
