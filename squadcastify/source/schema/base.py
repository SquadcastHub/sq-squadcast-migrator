"""Base models for the schema."""

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base class for all schema."""

    class Config:
        """Pydantic config."""

        extra = "allow"
