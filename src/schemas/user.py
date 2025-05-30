from typing import Optional
from pydantic import EmailStr
from .base import BaseSchema

class BaseUser(BaseSchema):
    """Base model for a user."""

    first_name: str
    last_name: str
    email: EmailStr
    role: Optional[str] = None


class CreateUserRequest(BaseUser):
    """Model for creating a user."""
    pass


class User(BaseUser):
    """Model for user response from API."""

    id: str

class CreateUserResponse(User):
    pass
