"""OpsGenie to Squadcast migrator."""

import logging
from dataclasses import dataclass, field

from tqdm import tqdm

from .context import MigrationContext

from ..transformer import Transformer
from .client.api import OpsgenieAPIClient
from ...terraform.exporter import TerraformExporter
from ...terraform.models import SquadcastTeam, SquadcastTeamMember, SquadcastUser

logger = logging.getLogger(__name__)


@dataclass
class OpsGenieTransformer(Transformer):
    """Migrates data from OpsGenie to Terraform configurations."""

    client: OpsgenieAPIClient
    exporter: TerraformExporter
    context: MigrationContext = field(default_factory=MigrationContext)

    def _migrate_users(self) -> None:
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
                self.exporter.add_resource(squadcast_user)
                self.context.add_user(user.id, squadcast_user)
                logger.info(f"Successfully migrated user: {user.username}")

            except Exception as e:
                logger.error(f"Failed to migrate user {user.username}: {str(e)}")

    def _migrate_teams(self) -> None:
        """Migrate teams from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie team migration to Terraform")

        opsgenie_teams = self.client.teams.list_teams()
        logger.info(f"Found {len(opsgenie_teams)} teams in OpsGenie")

        for team in tqdm(opsgenie_teams, desc="Migrating teams", unit="team"):
            try:
                description = team.description or f"Team {team.name}"
                squadcast_team = SquadcastTeam(name=team.name, description=description)
                self.exporter.add_resource(squadcast_team)
                self.context.add_team(team.id, squadcast_team)

                # Add team members
                for member in team.members:
                    if not self.context.has_user(member.id):
                        logger.warning(
                            f"User {member.username} not found in migration map, skipping"
                        )
                        continue

                    user = self.context.get_user(member.id)
                    self.exporter.add_resource(
                        SquadcastTeamMember(
                            team_id=squadcast_team.terraform_id_reference,
                            user_id=user.terraform_id_reference,
                        )
                    )

                logger.info(f"Successfully migrated team: {team.name}")

            except Exception as e:
                logger.error(f"Failed to migrate team {team.name}: {str(e)}")

    def transform(self) -> None:
        """Transform OpsGenie resources to Terraform configurations."""
        logger.info("🚀 Starting migration from OpsGenie to Terraform")

        # First migrate users so we have them available for team membership
        logger.info("Migrating users...")
        self._migrate_users()

        # Then migrate teams and their members
        logger.info("Migrating teams...")
        self._migrate_teams()

        logger.info("✅ Migration completed")
