from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator

from .base import TerraformResource
from .common import EntityOwner
from .utils import generate_terraform_name


class Tag(BaseModel):
    """Represents a tag with key-value pair"""
    
    key: str = Field(..., description="The key of the tag")
    value: str = Field(..., description="The value of the tag")


class Participant(BaseModel):
    """Represents a participant in rotation"""
    
    id: str = Field(..., description="The ID of the participant")
    type: Literal["user", "squad"] = Field(
        ..., description="The type of the participant (user or squad)"
    )


class ParticipantGroup(BaseModel):
    """Represents a group of participants in rotation"""
    
    participants: List[Participant] = Field(
        ..., description="List of participants in this group"
    )


class ShiftTimeslot(BaseModel):
    """Represents a shift timeslot in a rotation"""
    
    start_hour: int = Field(..., description="The hour when the shift starts (0-23)")
    start_minute: int = Field(
        ..., description="The minute when the shift starts (0-59)"
    )
    duration: int = Field(..., description="Duration of the shift in minutes")
    day_of_week: Optional[str] = Field(
        None, description="Day of the week (for custom period only)"
    )
    
    @field_validator('start_hour')
    @classmethod
    def validate_start_hour(cls, v):
        if not 0 <= v <= 23:
            raise ValueError("start_hour must be between 0 and 23")
        return v
    
    @field_validator('start_minute')
    @classmethod
    def validate_start_minute(cls, v):
        if not 0 <= v <= 59:
            raise ValueError("start_minute must be between 0 and 59")
        return v


class ScheduleRotation(TerraformResource):
    """Represents a Squadcast schedule rotation resource in Terraform."""
    
    schedule_id: str = Field(
        ..., description="ID of the schedule this rotation belongs to"
    )
    name: str = Field(..., description="Name of the rotation")
    start_date: str = Field(
        ..., description="Start date of the rotation in ISO format"
    )
    period: Literal["daily", "weekly", "monthly", "custom"] = Field(
        ..., description="Period type of the rotation"
    )
    shift_timeslots: Optional[List[ShiftTimeslot]] = Field(
        None, description="List of shift timeslots (required for custom period)"
    )
    change_participants_frequency: int = Field(
        ..., description="Frequency of changing participants"
    )
    change_participants_unit: Literal["day", "week", "month", "rotation"] = Field(
        ..., description="Unit of changing participants"
    )
    custom_period_frequency: Optional[int] = Field(
        None, description="Frequency for custom period (required if period is 'custom')"
    )
    custom_period_unit: Optional[Literal["day", "week", "month"]] = Field(
        None, description="Unit for custom period (required if period is 'custom')"
    )
    participant_groups: List[ParticipantGroup] = Field(
        ..., description="List of participant groups in this rotation"
    )
    end_date: Optional[str] = Field(
        None, description="End date of the rotation in ISO format"
    )
    
    # Read-only fields
    id: Optional[str] = Field(
        None, description="Rotation ID (read-only)", exclude=True
    )
    
    def __init__(self, **data):
        """Initialize a schedule rotation with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "name" in data:
            data["terraform_name"] = generate_terraform_name(data["name"], data["schedule_id"])
        super().__init__(**data)
    
    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast schedule rotation"""
        return "squadcast_schedule_rotation_v2"
    


class SquadcastSchedule(TerraformResource):
    """Represents a Squadcast schedule resource in Terraform."""
    
    name: str = Field(..., description="Name of the schedule")
    team_id: str = Field(
        ..., description="ID of the team this schedule belongs to"
    )
    description: Optional[str] = Field(None, description="Description of the schedule")
    timezone: str = Field(..., description="Timezone of the schedule")
    entity_owner: EntityOwner = Field(..., description="Owner of the schedule")
    tags: Optional[List[Tag]] = Field(None, description="List of tags for the schedule")
    
    # Read-only fields
    id: Optional[str] = Field(
        None, description="Schedule ID (read-only)", exclude=True
    )
    
    def __init__(self, **data):
        """Initialize a schedule with auto-generated terraform_name if not provided."""
        if "terraform_name" not in data and "name" in data:
            data["terraform_name"] = generate_terraform_name(data["name"])
        super().__init__(**data)
    
    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type for Squadcast schedule"""
        return "squadcast_schedule_v2"