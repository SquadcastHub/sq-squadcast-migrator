from typing import Optional, List
from pydantic import Field
from pydantic import BaseModel

from .base import TerraformResource
from .utils import generate_terraform_name

class SquadMember(BaseModel):
    user_id: str = Field(..., description="ID of the user in the squad")

class SquadcastSquad(TerraformResource):
    """Represents a Squadcast squad resource in Terraform.

    Squads are smaller groups of members within Teams.
    """
    name: str = Field(..., description="Name of the squad")

    team_id: str = Field(..., description="ID of the team this squad belongs to")

    members: Optional[List[SquadMember]] = Field(
        [], description="List of member IDs in the squad"
    )

    # Read-only fields
    id: Optional[str] = Field(None, description="ID (read-only)", readonly=True)

    def __init__(self, **data):
        """Initialize a squad with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "name" in data and "team_id" in data:
            data["terraform_name"] = generate_terraform_name(
                data["name"]
            )
        super().__init__(**data)

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast squad"""
        return "squadcast_squad"
