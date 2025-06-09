from typing import Optional, Dict
from pydantic import Field, model_validator

from .base import TerraformResource, ReadOnlyField
from .utils import generate_terraform_name


class SquadcastTeam(TerraformResource):
    """Represents a Squadcast team resource in Terraform.

    The team resource manages team metadata like name and description.
    Team names must be unique within an organization.

    Examples:
        >>> team = SquadcastTeam(display_name="Engineering Team")
        >>> team.terraform_name
        'engineering_team'
    """

    name: str = Field(..., description="Name of the team")

    # Optional fields
    description: Optional[str] = Field(None, description="Description of the team")

    # Read-only fields
    id: Optional[str] = Field(None, description="Team ID (read-only)", readonly=True)
    default: Optional[bool] = Field(
        None,
        description="Indicates if this is the default team (read-only)",
        readonly=True,
    )
    default_role_ids: Optional[Dict[str, str]] = Field(
        None, description="Map of default role IDs (read-only)", readonly=True
    )

    def __init__(self, **data):
        """Initialize a team with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "name" in data:
            data["terraform_name"] = generate_terraform_name(data["name"])
        super().__init__(**data)

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast team"""
        return "squadcast_team"

