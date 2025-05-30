"""Authentication models for Squadcast API."""
from typing import Optional
from .base import BaseSchema


class OauthResponse(BaseSchema):
    """Authentication response model."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
