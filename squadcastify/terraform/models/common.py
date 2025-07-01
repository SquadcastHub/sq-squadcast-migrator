from pydantic import BaseModel, Field
from typing import Literal

class EntityOwner(BaseModel):
    """Represents an entity owner (user or squad)"""

    id: str = Field(..., description="The ID of the owner")
    type: Literal["user", "squad"] = Field(
        ..., description="The type of the owner (user or squad)"
    )
