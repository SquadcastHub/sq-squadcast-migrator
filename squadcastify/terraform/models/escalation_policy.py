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

    def to_hcl(self) -> str:
        """
        Convert the escalation policy resource to HCL format.
        
        This method handles the complex nested structure of escalation policies including:
        - Multiple rules with targets
        - Round robin configurations
        - Repeat settings
        - Entity ownership information
        
        Returns:
            str: A valid HCL string representation of the escalation policy that can be used in Terraform.
        
        Example:
            An escalation policy with a rule might convert to:
            
            resource "squadcast_escalation_policy" "my_policy" {
              name = "Critical Services EP"
              team_id = "12345"
              rules {
                delay_minutes = 5
                targets {
                  id = "user123"
                  type = "user"
                }
              }
              entity_owner {
                id = "user456"
                type = "user"
              }
            }
        """
        # Convert model to dict, excluding None values
        try:
            data = self.model_dump(exclude_none=True, exclude={"terraform_name"})
        except AttributeError:
            data = self.dict(exclude_none=True, exclude={"terraform_name"})

        hcl = [f'resource "{self.terraform_resource_type}" "{self.terraform_name}" {{']

        # Add fields
        for key, value in data.items():
            if key == "rules":
                # Format each rule as a separate block
                if value:
                    for rule in value:
                        try:
                            try:
                                rule_data = rule.model_dump(exclude_none=True)
                            except AttributeError:
                                rule_data = rule.dict(exclude_none=True)
                        except AttributeError:
                            rule_data = rule
                            
                        rule_content = []
                        
                        # Handle special nested fields
                        for k, v in rule_data.items():
                            if k == "targets":
                                # Format each target as a separate block 
                                for target in v:
                                    try:
                                        try:
                                            target_data = target.model_dump(exclude_none=True)
                                        except AttributeError:
                                            target_data = target.dict(exclude_none=True)
                                    except AttributeError:
                                        target_data = target
                                    
                                    target_content = []
                                    for tk, tv in target_data.items():
                                        formatted_tv = self._format_hcl_value(tv)
                                        target_content.append(f"{tk} = {formatted_tv}")
                                    
                                    rule_content.append(f"targets {{\n      " + "\n      ".join(target_content) + "\n    }")
                            elif k == "notification_channels":
                                channels_str = self._format_hcl_value(v)
                                rule_content.append(f"notification_channels = {channels_str}")
                            elif k == "round_robin":
                                # Format round_robin as a block
                                if v:
                                    try:
                                        try:
                                            round_robin_data = v.model_dump(exclude_none=True)
                                        except AttributeError:
                                            round_robin_data = v.dict(exclude_none=True)
                                    except AttributeError:
                                        round_robin_data = v
                                        
                                    rr_content = []
                                    for rr_k, rr_v in round_robin_data.items():
                                        formatted_rr_v = self._format_hcl_value(rr_v)
                                        rr_content.append(f"{rr_k} = {formatted_rr_v}")
                                    rule_content.append(f"round_robin {{\n      " + "\n      ".join(rr_content) + "\n    }")
                            elif k == "repeat":
                                # Format repeat as a block
                                if v:
                                    try:
                                        try:
                                            repeat_data = v.model_dump(exclude_none=True)
                                        except AttributeError:
                                            repeat_data = v.dict(exclude_none=True)
                                    except AttributeError:
                                        repeat_data = v
                                        
                                    repeat_content = []
                                    for r_k, r_v in repeat_data.items():
                                        formatted_r_v = self._format_hcl_value(r_v)
                                        repeat_content.append(f"{r_k} = {formatted_r_v}")
                                    rule_content.append(f"repeat {{\n      " + "\n      ".join(repeat_content) + "\n    }")
                            else:
                                formatted_v = self._format_hcl_value(v)
                                rule_content.append(f"{k} = {formatted_v}")
                                
                        hcl.append(f"  rules {{\n    " + "\n    ".join(rule_content) + "\n  }")
            
            elif key == "repeat" and value is not None:
                # Format repeat as a block
                try:
                    try:
                        repeat_data = value.model_dump(exclude_none=True)
                    except AttributeError:
                        repeat_data = value.dict(exclude_none=True)
                except AttributeError:
                    repeat_data = value
                    
                repeat_content = []
                for k, v in repeat_data.items():
                    formatted_v = self._format_hcl_value(v)
                    repeat_content.append(f"{k} = {formatted_v}")
                hcl.append(f"  repeat {{\n    " + "\n    ".join(repeat_content) + "\n  }")
            
            elif key == "entity_owner":
                # Format entity_owner as a block
                try:
                    try:
                        owner_data = value.model_dump(exclude_none=True)
                    except AttributeError:
                        owner_data = value.dict(exclude_none=True)
                except AttributeError:
                    owner_data = value
                    
                owner_content = []
                for k, v in owner_data.items():
                    formatted_v = self._format_hcl_value(v)
                    owner_content.append(f"{k} = {formatted_v}")
                hcl.append(f"  entity_owner {{\n    " + "\n    ".join(owner_content) + "\n  }")
                
            else:
                formatted_value = self._format_hcl_value(value)
                hcl.append(f"  {key} = {formatted_value}")

        hcl.append("}")
        return "\n".join(hcl)
