from typing import Optional
from pydantic import Field

from .base import TerraformDataSource
from .utils import generate_terraform_name


class SquadcastTeamRole(TerraformDataSource):
    """Represents a Squadcast team role data source in Terraform.

    This data source allows you to look up team roles by name within a specific team.
    Team roles define permissions and access levels for team members.

    Examples:
        >>> role = SquadcastTeamRole(name="User", team_id="team_id")
        >>> role.terraform_name
        'user_role'
    """

    name: str = Field(..., description="Name of the team role (e.g., 'User', 'Admin')")
    team_id: str = Field(..., description="ID of the team to look up the role in")
    
    # Read-only fields that will be populated by Terraform
    id: Optional[str] = Field(None, description="ID of the role (read-only)")
    description: Optional[str] = Field(None, description="Description of the role (read-only)")

    def __init__(self, **data):
        """Initialize a team role data source with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "name" in data:
            # Generate terraform name based on role name
            role_name = data["name"].lower().replace(" ", "_")
            data["terraform_name"] = f"{role_name}_role"
        super().__init__(**data)

    @property
    def terraform_data_source_type(self) -> str:
        """Return the Terraform data source type for Squadcast team role"""
        return "squadcast_team_role"
