"""Schedule models for OpsGenie API."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .base import OpsGenieModel, OpsGenieOwnerTeam

@dataclass
class OpsGenieParticipant:
    """Represents a participant in a rotation."""

    id: str
    type: str
    username: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieParticipant":
        """Create a participant from API response data."""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            username=data.get("username", ""),
        )
    

@dataclass
class OpsGenieTimeRestriction:
    type: str # "weekday-and-time-of-day" or "time-of-day"
    restrictions: List["OpsGenieRestrictions"] = field(default_factory=list)
    restriction: Optional["OpsGenieRestrictions"] = None  # Used for single restriction case i.e when type = time-of-day
    
    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieTimeRestriction":
        """Create time restriction from API response data."""
        restrictions = [
            OpsGenieRestrictions.from_dict(r) for r in data.get("restrictions", [])
        ]
        restriction = OpsGenieRestrictions.from_dict(data["restriction"]) if data.get("restriction") else None
        return cls(
            type=data["type"],
            restrictions=restrictions,
            restriction=restriction
        )
    
@dataclass
class OpsGenieRestrictions:
    """Represents time restrictions for a rotation."""

    startDay: str
    startHour: int
    startMin: int
    endDay: str
    endHour: int
    endMin: int
    
    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieRestrictions":
        """Create restrictions from API response data."""
        return cls(
            startDay=data.get("startDay", ""),
            startHour=data["startHour"],
            startMin=data["startMin"],
            endDay=data.get("endDay", ""),
            endHour=data["endHour"],
            endMin=data["endMin"],
        )
    


@dataclass
class OpsGenieRotation(OpsGenieModel):
    """Represents a rotation within a schedule."""

    name: str
    start_date: datetime
    type: str  # weekly, daily, hourly, custom
    end_date: Optional[datetime] = None
    participants: List[OpsGenieParticipant] = field(default_factory=list)
    end_date: Optional[datetime] = None
    time_restriction: Optional[OpsGenieTimeRestriction] = None # Used to limit schedule rotation to certain day and time of the week
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
            participants=[OpsGenieParticipant.from_dict(p) for p in data.get("participants", [])],
            time_restriction=OpsGenieTimeRestriction.from_dict(data["timeRestriction"])
            if data.get("timeRestriction") else None,
            length=data.get("length"),
        )


@dataclass
class OpsGenieSchedule(OpsGenieModel):
    """Represents an on-call schedule in OpsGenie."""

    name: str
    description: Optional[str] = None
    timezone: str = "UTC"
    enabled: bool = True
    owner_team: Optional[OpsGenieOwnerTeam] = None
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
            owner_team=OpsGenieOwnerTeam.from_dict(data["ownerTeam"]) if data.get("ownerTeam") else None,
            rotations=rotations,
        )
