"""Base models for the schemas."""

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base class for all schemas."""

    class Config:
        """Pydantic config."""

        extra = "allow"
