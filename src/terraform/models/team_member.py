from typing import Optional, Dict
from pydantic import Field, model_validator

from .base import TerraformResource, ReadOnlyField
from .utils import generate_terraform_name


class SquadcastTeamMember(TerraformResource):
    """Represents a Squadcast team member resource in Terraform.

    The team member resource manages user membership within a Squadcast team.
    Each member is associated with a specific role within the team.

    Examples:
        >>> team = SquadcastTeam(display_name="Engineering Team")
        >>> team.terraform_name
        'engineering_team'
    """

    team_id: str = Field(..., description="ID of the team this member belongs to")

    user_id: str = Field(..., description="ID of the user who is a member of the team")

    # Read-only fields
    id: Optional[str] = Field(None, description="ID (read-only)", readonly=True)

    def __init__(self, **data):
        """Initialize a team member with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "user_id" in data:
            data["terraform_name"] = generate_terraform_name(data["user_id"])
        super().__init__(**data)

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast team member"""
        return "squadcast_team_member"

    def model_dump(self, *args, **kwargs):
        """Override model_dump to convert user_id to id in output"""
        data = super().model_dump(*args, **kwargs)
        return data
