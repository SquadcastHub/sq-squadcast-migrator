"""Team models for OpsGenie API."""

from dataclasses import dataclass, field
from typing import Optional, List

from .base import OpsGenieModel


@dataclass
class OpsGenieTeamMember(OpsGenieModel):
    """Represents a member of an OpsGenie team."""

    username: str
    role: str

    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieTeamMember":
        """
        Create a team member instance from API response data.

        Args:
            data: Dictionary containing team member data

        Returns:
            OpsGenieTeamMember instance
        """
        user = data.get("user", {})
        return cls(
            id=user.get("id", ""),
            username=user.get("username", ""),
            role=data.get("role", ""),
        )


@dataclass
class OpsGenieTeam(OpsGenieModel):
    """Represents a team in OpsGenie."""

    name: str
    description: Optional[str] = None
    members: List[OpsGenieTeamMember] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieTeam":
        """
        Create a team instance from API response data.

        Args:
            data: Dictionary containing team data

        Returns:
            OpsGenieTeam instance
        """
        members = [
            OpsGenieTeamMember.from_dict(member) for member in data.get("members", [])
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            members=members,
        )
