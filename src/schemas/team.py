"""Team models for Squadcast API."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class TeamBase(BaseSchema):
    """Base model for a team."""

    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    """Model for creating a team."""

    members: Optional[List[str]] = Field(default_factory=list)
    
class TeamMember(BaseSchema):
    """Model for a team member."""

    user_id: str
    role_ids: List[str] = Field(default_factory=list)
    abilities: Dict[str, Any] = Field(default_factory=dict)

class Role(BaseModel):
    id: str
    name: str
    slug: str
    default: bool
    abilities: Dict[str, Dict[str, bool]]

class TeamResponse(TeamBase):
    """Model for team response from API."""

    id: str
    members: Optional[List[TeamMember]] = Field(default_factory=list)
    roles: List[Role] = Field(default_factory=list)