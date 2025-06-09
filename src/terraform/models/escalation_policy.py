from typing import Optional
from pydantic import Field

from .base import TerraformResource
from .utils import generate_terraform_name


class SquadcastEscalationPolicy(TerraformResource):
    """Represents a Squadcast escalation policy resource in Terraform."""

    name: str = Field(..., description="Name of the escalation policy")
    team_id: str = Field(
        ..., description="ID of the team this escalation policy belongs to"
    )

    # Read-only fields
    id: Optional[str] = Field(
        None, description="Escalation policy ID (read-only)", readonly=True
    )

    def __init__(self, **data):
        """Initialize an escalation policy with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "display_name" in data:
            data["terraform_name"] = generate_terraform_name(data["display_name"])
        super().__init__(**data)

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast escalation policy"""
        return "squadcast_escalation_policy"

