from dataclasses import dataclass, field
from typing import Dict

from squadcastify.terraform.models import (
    SquadcastTeam, 
    SquadcastUser, 
    SquadcastEscalationPolicy, 
    SquadcastSchedule,
    SquadcastScheduleRotation
)


@dataclass
class MigrationContext:
    """Context for tracking migration state."""

    users: Dict[str, SquadcastUser] = field(default_factory=dict)
    teams: Dict[str, SquadcastTeam] = field(default_factory=dict)
    escalation_policies: Dict[str, SquadcastEscalationPolicy] = field(default_factory=dict)
    schedules: Dict[str, SquadcastSchedule] = field(default_factory=dict)
    rotations: Dict[str, SquadcastScheduleRotation] = field(default_factory=dict)

    def add_user(self, og_id: str, user: SquadcastUser) -> None:
        """Add a migrated user to the context."""
        self.users[og_id] = user

    def add_team(self, og_id: str, team: SquadcastTeam) -> None:
        """Add a migrated team to the context."""
        self.teams[og_id] = team
        
    def add_escalation_policy(self, og_id: str, policy: SquadcastEscalationPolicy) -> None:
        """Add a migrated escalation policy to the context."""
        self.escalation_policies[og_id] = policy

    def get_user(self, og_id: str) -> SquadcastUser:
        """Get a migrated user by OpsGenie ID."""
        return self.users[og_id]

    def has_user(self, og_id: str) -> bool:
        """Check if user exists in context."""
        return og_id in self.users
        
    def get_team(self, og_id: str) -> SquadcastTeam:
        """Get a migrated team by OpsGenie ID."""
        return self.teams[og_id]
        
    def has_team(self, og_id: str) -> bool:
        """Check if team exists in context."""
        return og_id in self.teams
        
    def get_escalation_policy(self, og_id: str) -> SquadcastEscalationPolicy:
        """Get a migrated escalation policy by OpsGenie ID."""
        return self.escalation_policies[og_id]
        
    def has_escalation_policy(self, og_id: str) -> bool:
        """Check if escalation policy exists in context."""
        return og_id in self.escalation_policies
        
    def add_schedule(self, og_id: str, schedule: SquadcastSchedule) -> None:
        """Add a migrated schedule to the context."""
        self.schedules[og_id] = schedule
        
    def get_schedule(self, og_id: str) -> SquadcastSchedule:
        """Get a migrated schedule by OpsGenie ID."""
        return self.schedules[og_id]
        
    def has_schedule(self, og_id: str) -> bool:
        """Check if schedule exists in context."""
        return og_id in self.schedules
        
    def add_rotation(self, og_id: str, rotation: SquadcastScheduleRotation) -> None:
        """Add a migrated rotation to the context."""
        self.rotations[og_id] = rotation
        
    def get_rotation(self, og_id: str) -> SquadcastScheduleRotation:
        """Get a migrated rotation by OpsGenie ID."""
        return self.rotations[og_id]
        
    def has_rotation(self, og_id: str) -> bool:
        """Check if rotation exists in context."""
        return og_id in self.rotations
