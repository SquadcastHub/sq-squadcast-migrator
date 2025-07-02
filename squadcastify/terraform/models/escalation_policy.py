from typing import Optional, List, Literal
from pydantic import BaseModel, Field

from .base import TerraformResource
from .common import EntityOwner
from .utils import generate_terraform_name


class Target(BaseModel):
    """Represents a target in the escalation policy rule"""

    id: str = Field(..., description="The ID of the target")
    type: Literal["user", "squad", "schedulev2"] = Field(
        ..., description="The type of the target (user, squad, or schedulev2)"
    )


class Repeat(BaseModel):
    """Represents a repeat block for escalation policy rules"""

    times: int = Field(..., description="Number of times to repeat the escalation")
    delay_minutes: int = Field(..., description="Minutes to wait before repeating the escalation")


class Rotation(BaseModel):
    """Represents a rotation block for round robin"""

    enabled: bool = Field(..., description="Whether rotation is enabled")
    delay_minutes: int = Field(..., description="Minutes to wait before rotating to the next target")


class RoundRobin(BaseModel):
    """Represents a round robin block for escalation policy rules"""

    enabled: bool = Field(..., description="Whether round robin is enabled")
    rotation: Optional[Rotation] = Field(None, description="Rotation configuration for round robin")


class Rule(BaseModel):
    """Represents a rule in the escalation policy"""

    delay_minutes: int = Field(..., description="Minutes to wait before escalating")
    targets: List[Target] = Field(..., description="Targets to notify")
    notification_channels: Optional[List[str]] = Field(None, description="Channels to use for notification")
    repeat: Optional[Repeat] = Field(None, description="Repeat configuration for the rule")
    round_robin: Optional[RoundRobin] = Field(None, description="Round robin configuration for the rule")


class SquadcastEscalationPolicy(TerraformResource):
    """Represents a Squadcast escalation policy resource in Terraform."""

    name: str = Field(..., description="Name of the escalation policy")
    team_id: str = Field(
        ..., description="ID of the team this escalation policy belongs to"
    )
    description: Optional[str] = Field(None, description="Description of the escalation policy")
    rules: List[Rule] = Field(..., description="List of escalation rules")
    repeat: Optional[Repeat] = Field(None, description="Global repeat configuration for the policy")
    entity_owner: EntityOwner = Field(..., description="Owner of the escalation policy")

    # Read-only fields
    id: Optional[str] = Field(
        None, description="Escalation policy ID (read-only)", readonly=True
    )

    def __init__(self, **data):
        """Initialize an escalation policy with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "name" in data:
            data["terraform_name"] = generate_terraform_name(data["name"])
        super().__init__(**data)

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast escalation policy"""
        return "squadcast_escalation_policy"
