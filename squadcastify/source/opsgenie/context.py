from squadcastify.terraform.models import SquadcastTeam, SquadcastUser


from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MigrationContext:
    """Context for tracking migration state."""

    users: Dict[str, SquadcastUser] = field(default_factory=dict)
    teams: Dict[str, SquadcastTeam] = field(default_factory=dict)

    def add_user(self, og_id: str, user: SquadcastUser) -> None:
        """Add a migrated user to the context."""
        self.users[og_id] = user

    def add_team(self, og_id: str, team: SquadcastTeam) -> None:
        """Add a migrated team to the context."""
        self.teams[og_id] = team

    def get_user(self, og_id: str) -> SquadcastUser:
        """Get a migrated user by OpsGenie ID."""
        return self.users[og_id]

    def has_user(self, og_id: str) -> bool:
        """Check if user exists in context."""
        return og_id in self.users
