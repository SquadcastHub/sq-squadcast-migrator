"""Authentication models for Squadcast API."""
from typing import Optional
from pydantic import BaseModel

from src.schemas.base import BaseSchema


class AuthResponse(BaseSchema):
    """Authentication response model."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
