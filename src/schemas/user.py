from typing import Optional
from pydantic import EmailStr

from src.schemas.base import BaseSchema


class UserBase(BaseSchema):
    """Base model for a user."""

    first_name: str
    last_name: str
    email: EmailStr
    role: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a user."""
    pass


class UserResponse(UserBase):
    """Model for user response from API."""

    id: str


class UserMigration(BaseSchema):
    """Model for tracking user migration."""

    source_id: str
    target_id: str
    email: EmailStr
