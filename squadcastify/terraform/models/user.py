from typing import Optional, Set, Literal
from pydantic import Field, field_validator

from .base import TerraformResource
from .utils import generate_terraform_name

# Define valid abilities as literals
UserAbility = Literal[
    "manage-api-tokens",
    "manage-billing",
    "manage-extensions",
    "manage-teams",
    "manage-users",
    "manage-webhooks",
    "manage-organization-analytics",
    "manage-postmortem-templates",
]

# Define valid roles
UserRole = Literal["stakeholder", "user", "admin"]


class SquadcastUser(TerraformResource):
    """Represents a Squadcast user resource in Terraform.

    Manages user accounts with their roles and permissions within Squadcast.
    """

    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    email: str = Field(..., description="Email address of the user")
    role: UserRole = Field(..., description="User role (stakeholder, user, or admin)")

    # Optional fields
    abilities: Optional[Set[UserAbility]] = Field(
        default=None,
        description=(
            "Set of user abilities/permissions. Valid values: manage-api-tokens, "
            "manage-billing, manage-extensions, manage-teams, manage-users, "
            "manage-webhooks, manage-organization-analytics, manage-postmortem-templates"
        ),
    )

    # Read-only fields
    id: Optional[str] = Field(None, description="User ID (read-only)", readonly=True)

    def __init__(self, **data):
        """Initialize a user with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "email" in data:
            # Use the local part of the email as basis for terraform_name
            local_part = data["email"].split("@")[0]
            data["terraform_name"] = generate_terraform_name(local_part)
        super().__init__(**data)

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast user"""
        return "squadcast_user"
