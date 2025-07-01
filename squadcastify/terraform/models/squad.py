from typing import Optional
from pydantic import Field

from .base import TerraformResource
from .utils import generate_terraform_name


class SquadcastSquad(TerraformResource):
    """Represents a Squadcast squad resource in Terraform.

    Squads are smaller groups of members within Teams.
    """
    name: str = Field(..., description="Name of the squad")

    team_id: str = Field(..., description="ID of the team this squad belongs to")

    members: Optional[list[str]] = Field(
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
    
    def to_hcl(self) -> str:
        """Convert the resource to HCL format with special handling for certain blocks
        
        This method serializes the squad resource to Terraform HCL format,
        handling the members list as individual blocks with user_id fields
        as required by the Squadcast Terraform provider.
        
        Returns:
            str: HCL representation of the squad resource
        
        Example:
            ```
            resource "squadcast_squad" "myteam_mysquad" {
              name = "My Squad"
              team_id = "team123"
              members {
                user_id = "user456"
              }
              members {
                user_id = "user789"
              }
            }
            ```
        """
        # Convert model to dict, excluding None values
        try:
            data = self.model_dump(exclude_none=True, exclude={"terraform_name"})
        except AttributeError:
            data = self.dict(exclude_none=True, exclude={"terraform_name"})

        hcl = [f'resource "{self.terraform_resource_type}" "{self.terraform_name}" {{']

        # Add fields
        for key, value in data.items():                
            if key == "members":
                # Format each member as an individual block with user_id field
                if value:
                    for member_id in value:
                        hcl.append(f"  members {{\n    user_id = {self._format_hcl_value(member_id)}\n  }}")
                
            else:
                formatted_value = self._format_hcl_value(value)
                hcl.append(f"  {key} = {formatted_value}")
                
        hcl.append("}")
        return "\n".join(hcl)
