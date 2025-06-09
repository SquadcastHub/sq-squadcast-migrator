"""Migration statistics models."""

from typing import Dict, Optional, List
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema


class MigrationStats(BaseSchema):
    """Model for migration statistics."""

    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    skipped_count: Optional[int] = 0
    errors: Optional[List[str]] = Field(default_factory=list)


class UserMigrationStats(MigrationStats):
    """User migration statistics."""

    pass


class TeamMigrationStats(MigrationStats):
    """Team migration statistics."""

    pass
