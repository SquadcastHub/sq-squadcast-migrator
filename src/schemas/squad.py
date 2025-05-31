"""Squad models for Squadcast API."""
from typing import Optional, List
from pydantic import Field
from .base import BaseSchema


class BaseSquad(BaseSchema):
    """Base model for a squad."""

    name: str

class SquadMember(BaseSchema):
    """Model for a squad member."""

    user_id: str
    # role: str # Add this for OBAC Model

class CreateSquadRequest(BaseSquad):
    """Model for creating a squad."""

    owner_id: Optional[str] = None
    members: List[SquadMember] = Field(default_factory=list)

class Squad(BaseSquad):
    """Model for squad response from API."""

    id: str
    owner_id: Optional[str] = None
    members: List[SquadMember] = Field(default_factory=list)

class CreateSquadResponse(BaseSchema):
    """Model for creating a squad response."""
    squad: Squad