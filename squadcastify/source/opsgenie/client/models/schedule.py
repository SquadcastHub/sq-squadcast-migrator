"""Schedule models for OpsGenie API."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import OpsGenieModel


@dataclass
class OpsGenieRotation(OpsGenieModel):
    """Represents a rotation within a schedule."""

    name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    type: str  # weekly, daily, hourly, custom
    participants: List[Dict[str, Any]] = field(default_factory=list)
    time_restriction: Optional[Dict[str, Any]] = None
    length: Optional[int] = None  # Length of the rotation in minutes

    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieRotation":
        """Create a rotation from API response data."""
        return cls(
            id=data["id"],
            name=data["name"],
            start_date=datetime.fromisoformat(data["startDate"].rstrip("Z")),
            end_date=datetime.fromisoformat(data["endDate"].rstrip("Z"))
            if data.get("endDate")
            else None,
            type=data["type"],
            participants=data.get("participants", []),
            time_restriction=data.get("timeRestriction"),
            length=data.get("length"),
        )


@dataclass
class OpsGenieSchedule(OpsGenieModel):
    """Represents an on-call schedule in OpsGenie."""

    name: str
    description: Optional[str] = None
    timezone: str = "UTC"
    enabled: bool = True
    owner_team: Optional[Dict[str, Any]] = None
    rotations: List[OpsGenieRotation] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieSchedule":
        """Create a schedule from API response data."""
        rotations = [
            OpsGenieRotation.from_dict(rotation)
            for rotation in data.get("rotations", [])
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            timezone=data.get("timezone", "UTC"),
            enabled=data.get("enabled", False),
            owner_team=data.get("ownerTeam"),
            rotations=rotations,
        )
