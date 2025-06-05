import logging
from typing import Optional
from src.alerting_client import AlertingClient
from src.squadcast.client import SquadcastClient
from src.db.db_manager import DBManager
from src.opsgenie.client import OpsGenieClient

logger = logging.getLogger(__name__)


class OpsGenieMigrator:
    """Migrates data from Opsgenie to Squadcast."""

    def __init__(
        self,
        opsgenie_client: OpsGenieClient,
        squadcast_client: SquadcastClient,
        db_manager: Optional[DBManager] = None,
    ):
        """
        Initialize the Opsgenie migrator.

        Args:
            opsgenie_client: OpsGenie API client
            squadcast_client: Squadcast API client
            db_manager: Database manager for tracking migration status (optional)
        """
        self.opsgenie_client = opsgenie_client
        self.squadcast_client = squadcast_client
        self.db_manager = db_manager or DBManager()

    def migrate_users(self):
        """Migrates users from Opsgenie to Squadcast."""
        logger.info("Starting user migration from Opsgenie to Squadcast")
        opsgenie_users = self.opsgenie_client.get_users()

        terraform_config = ""
        for user in opsgenie_users:
            sq_user_data = self.opsgenie_client.transform_user(user)
            resource_name = sq_user_data.email.replace('@', '_').replace('.', '_')
            terraform_config += f"""resource "squadcast_user" "{resource_name}" {{
  email      = "{sq_user_data.email}"
  first_name = "{sq_user_data.first_name}"
  last_name  = "{sq_user_data.last_name}"
  role       = "{sq_user_data.role}"
}}

"""

        with open("squadcast_users.tf", "w") as f:
            f.write(terraform_config)

        logger.info("Successfully generated Terraform configuration for users")

    def migrate_teams(self):
        """Migrates teams from Opsgenie to Squadcast."""
        logger.info("Starting team migration from Opsgenie to Squadcast")
        opsgenie_teams = self.opsgenie_client.get_teams()

        terraform_config = ""
        for team in opsgenie_teams:
            sq_team_data = self.opsgenie_client.transform_team(team)
            resource_name = sq_team_data.name.replace(' ', '_')
            terraform_config += f"""resource "squadcast_team" "{resource_name}" {{
  name        = "{sq_team_data.name}"
  description = "{sq_team_data.description}"
}}

"""

        with open("squadcast_teams.tf", "w") as f:
            f.write(terraform_config)

        logger.info("Successfully generated Terraform configuration for teams")
