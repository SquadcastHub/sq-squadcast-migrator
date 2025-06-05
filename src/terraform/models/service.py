from typing import Optional, List, Set, Dict, Literal, ForwardRef, Any
from pydantic import BaseModel, Field

from .base import TerraformResource
from .team import SquadcastTeam
from .escalation_policy import SquadcastEscalationPolicy
from .utils import generate_terraform_name


class ServiceTag(BaseModel):
    """Represents a key-value tag for a Squadcast service"""
    key: str = Field(..., description="Tag key")
    value: str = Field(..., description="Tag value")


class ServiceMaintainer(BaseModel):
    """Represents a maintainer (owner) of a Squadcast service"""
    id: str = Field(..., description="The ID of the maintainer")
    type: Literal["user", "squad"] = Field(
        ...,
        description="The type of the maintainer (user or squad)"
    )


class SquadcastService(TerraformResource):
    """Represents a Squadcast service resource in Terraform.
    
    Services are core components of infrastructure/application for which alerts 
    are generated. They represent specific systems, applications, components,
    products, or teams for which incidents are created.
    """
    display_name: str = Field(
        ...,
        description="Display name of the service"
    )
    team_id: str = Field(
        ...,
        description="ID of the team this service belongs to"
    )
    escalation_policy_id: str = Field(
        ...,
        description="ID of the escalation policy to use for this service"
    )
    def __init__(self, **data):
        """Initialize a service with auto-generated terraform_name if not provided."""
        # Convert team/escalation_policy objects to their IDs if provided
        if 'team' in data and isinstance(data['team'], TerraformResource):
            data['team_id'] = data['team'].terraform_id_reference
            del data['team']
        
        if 'escalation_policy' in data and isinstance(data['escalation_policy'], TerraformResource):
            data['escalation_policy_id'] = data['escalation_policy'].terraform_id_reference
            del data['escalation_policy']
            
        if 'terraform_name' not in data and 'display_name' in data:
            data['terraform_name'] = generate_terraform_name(data['display_name'])
        
        super().__init__(**data)
    
    email_prefix: str = Field(
        ...,
        description="Email prefix for the service"
    )
    maintainer: ServiceMaintainer = Field(
        ...,
        description="Service owner configuration"
    )
    
    # Optional fields
    description: Optional[str] = Field(
        None,
        description="Detailed description about this service"
    )
    alert_sources: Optional[List[str]] = Field(
        None,
        description="List of active alert source names"
    )
    dependencies: Optional[Set[str]] = Field(
        None,
        description="Set of service IDs that this service depends on"
    )
    slack_channel_id: Optional[str] = Field(
        None,
        description=(
            "ID of the Slack channel associated with the service. "
            "Once set, it can be changed but not removed."
        )
    )
    tags: Optional[List[ServiceTag]] = Field(
        None,
        description="List of key-value tags for the service"
    )
    
    # Read-only fields
    id: Optional[str] = Field(
        None,
        description="Service ID (read-only)",
        readonly=True
    )
    api_key: Optional[str] = Field(
        None,
        description="Unique API key of this service (read-only)",
        readonly=True
    )
    email: Optional[str] = Field(
        None,
        description="Service email (read-only)",
        readonly=True
    )
    active_alert_source_endpoints: Optional[Dict[str, str]] = Field(
        None,
        description="Active alert source endpoints (read-only)",
        readonly=True
    )
    alert_source_endpoints: Optional[Dict[str, str]] = Field(
        None,
        description="All available alert source endpoints (read-only)",
        readonly=True
    )

    def __init__(self, **data):
        """Initialize a service with auto-generated terraform_name if not provided."""
        if 'terraform_name' not in data and 'display_name' in data:
            data['terraform_name'] = generate_terraform_name(data['display_name'])
        super().__init__(**data)

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast service"""
        return "squadcast_service"
    
    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to convert display_name to name"""
        data = super(SquadcastService, self).model_dump(*args, **kwargs)
        if 'display_name' in data:
            data['name'] = data.pop('display_name')
        return dict(data)  # Ensure we always return a dict