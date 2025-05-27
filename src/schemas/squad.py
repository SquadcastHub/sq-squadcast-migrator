"""Squad models for Squadcast API."""
from typing import Optional, List
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class SquadBase(BaseSchema):
    """Base model for a squad."""

    name: str

class SquadMember(BaseSchema):
    """Model for a squad member."""

    user_id: str
    # role: str # Add this for OBAC Model

class SquadCreate(SquadBase):
    """Model for creating a squad."""

    owner_id: Optional[str] = None
    members: List[SquadMember] = Field(default_factory=list)


class SquadResponse(SquadBase):
    """Model for squad response from API."""

    id: str
    owner_id: Optional[str] = None
    members: List[SquadMember] = Field(default_factory=list)