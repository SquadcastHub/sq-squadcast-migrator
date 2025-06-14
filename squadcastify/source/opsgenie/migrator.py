"""OpsGenie to Squadcast migrator."""

import logging
from dataclasses import dataclass, field

from tqdm import tqdm

from squadcastify.terraform.transformer import Transformer

from .context import MigrationContext

from .client.api import OpsgenieAPIClient
from ...terraform.models import (
    SquadcastTeam,
    SquadcastTeamMember,
    SquadcastUser,
    TerraformResource,
)
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class OpsGenieTransformer(Transformer):
    """
    OpsGenieTransformer is responsible for migrating resources from OpsGenie to Terraform configurations.

    This transformer handles the following migration steps:
    - Migrates users from OpsGenie, mapping their details to SquadcastUser resources and tracking them in the migration context.
    - Migrates teams from OpsGenie, mapping their details to SquadcastTeam resources, and associates team members with the corresponding users if they have been migrated.
    - Maintains a MigrationContext to track the mapping between OpsGenie and Squadcast resources for users and teams.

    Attributes:
        client (OpsgenieAPIClient): The OpsGenie API client used to fetch users and teams.
        context (MigrationContext): The migration context for tracking resource mappings.

    Methods:
        _migrate_users(resources): Migrates users from OpsGenie to SquadcastUser resources.
        _migrate_teams(resources): Migrates teams from OpsGenie to SquadcastTeam resources and associates team members.
        transform(): Orchestrates the migration process by migrating users first, then teams and their members, and returns a list of TerraformResource objects.
    """

    client: OpsgenieAPIClient
    context: MigrationContext = field(default_factory=MigrationContext)

    def _migrate_users(self, resources: List[TerraformResource]) -> None:
        """Migrate users from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie user migration to Terraform")

        opsgenie_users = self.client.users.list_users()
        logger.info(f"Found {len(opsgenie_users)} users in OpsGenie")

        for user in tqdm(opsgenie_users, desc="Migrating users", unit="user"):
            try:
                name_parts = user.full_name.split(" ", 1)
                squadcast_user = SquadcastUser(
                    first_name=name_parts[0] if name_parts else "",
                    last_name=name_parts[1] if len(name_parts) > 1 else "",
                    email=user.username,
                    role="user",
                )
                resources.append(squadcast_user)
                self.context.add_user(user.id, squadcast_user)
                logger.info(f"Successfully migrated user: {user.username}")

            except Exception as e:
                logger.error(f"Failed to migrate user {user.username}: {str(e)}")

    def _migrate_teams(self, resources: List[TerraformResource]) -> None:
        """Migrate teams from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie team migration to Terraform")

        opsgenie_teams = self.client.teams.list_teams()
        logger.info(f"Found {len(opsgenie_teams)} teams in OpsGenie")

        for team in tqdm(opsgenie_teams, desc="Migrating teams", unit="team"):
            try:
                description = team.description or f"Team {team.name}"
                squadcast_team = SquadcastTeam(name=team.name, description=description)
                resources.append(squadcast_team)
                self.context.add_team(team.id, squadcast_team)

                # Add team members
                for member in team.members:
                    if not self.context.has_user(member.id):
                        logger.warning(
                            f"User {member.username} not found in migration map, skipping"
                        )
                        continue

                    user = self.context.get_user(member.id)
                    resources.append(
                        SquadcastTeamMember(
                            team_id=squadcast_team.terraform_id_reference,
                            user_id=user.terraform_id_reference,
                        )
                    )

                logger.info(f"Successfully migrated team: {team.name}")

            except Exception as e:
                logger.error(f"Failed to migrate team {team.name}: {str(e)}")

    def transform(self) -> List[TerraformResource]:
        """Transform OpsGenie resources to Terraform configurations and return as a list."""
        logger.info("🚀 Starting migration from OpsGenie to Terraform")

        resources: List[TerraformResource] = []

        # First migrate users so we have them available for team membership
        logger.info("Migrating users...")
        self._migrate_users(resources)

        # Then migrate teams and their members
        logger.info("Migrating teams...")
        self._migrate_teams(resources)

        logger.info("✅ Migration completed")
        return resources
