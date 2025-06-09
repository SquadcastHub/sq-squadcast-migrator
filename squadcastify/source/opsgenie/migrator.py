#!/usr/bin/env python3
import logging
from typing import Dict, List

from tqdm import tqdm

from squadcastify.source.transformer import Transformer
from squadcastify.source.opsgenie.client import OpsGenieClient
from squadcastify.source.schema.migration import (
    SourceMigratorStats,
)
from squadcastify.terraform.exporter import TerraformExporter
from squadcastify.terraform.models import (
    SquadcastTeam,
    SquadcastTeamMember,
    SquadcastUser,
)

logger = logging.getLogger(__name__)


class OpsgenieTransformer(Transformer):
    """
    Migrates data from OpsGenie to Terraform configurations using the Terraform Config Manager.
    Instead of directly creating entities in Squadcast, this creates Terraform configurations
    that can be applied to create or update resources.
    """

    def __init__(self, exporter: TerraformExporter):
        """
        Initialize the OpsGenie Terraform Migrator.

        Args:
            exporter (TerraformExporter): The exporter to use for generating Terraform configurations.
        """
        self.client = OpsGenieClient()
        self.exporter = exporter

        self.user_mapping: Dict[str, SquadcastUser] = {}
        self.team_mapping: Dict[str, SquadcastTeam] = {}

    def _migrate_users(self) -> SourceMigratorStats:
        """
        Migrate users from OpsGenie to Terraform configurations.

        Returns:
            Dict with migration statistics
        """
        logger.info("Starting OpsGenie user migration to Terraform")

        # Get all users from OpsGenie
        opsgenie_users = self.client.get_users()
        logger.info(f"Found {len(opsgenie_users)} users in OpsGenie")

        success_count = 0
        failure_count = 0
        errors: List[str] = []

        for user_data in tqdm(opsgenie_users, desc="Migrating users", unit="user"):
            try:
                full_name: str = user_data.get("fullName", "")
                name_parts = full_name.split(" ", 1)

                user = SquadcastUser(
                    first_name=name_parts[0] if len(name_parts) > 0 else "",
                    last_name=name_parts[1] if len(name_parts) > 1 else "",
                    email=user_data.get("username"),
                    role="user",
                )

                self.exporter.add_resource(user)

                self.user_mapping[user_data.get("id")] = user

                logger.info(f"Successfully migrated user: {user.email}")
                success_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to migrate user {user_data.get('username')}: {str(e)}"
                )
                errors.append(str(e))
                failure_count += 1

        return SourceMigratorStats(
            total_count=len(opsgenie_users),
            success_count=success_count,
            failure_count=failure_count,
            errors=errors,
        )

    def _migrate_teams(self) -> SourceMigratorStats:
        """
        Migrate teams from OpsGenie to Terraform configurations.

        Returns:
            Dict with migration statistics
        """
        logger.info("Starting OpsGenie team migration to Terraform")

        opsgenie_teams = self.client.get_teams()
        logger.info(f"Found {len(opsgenie_teams)} teams in OpsGenie")

        success_count = 0
        failure_count = 0
        errors: List[str] = []

        for team_data in tqdm(opsgenie_teams, desc="Migrating teams", unit="team"):
            try:
                team_id: str = team_data.get("id")
                if not team_id:
                    logger.warning(f"Team without ID found, skipping: {team_data}")
                    continue

                detailed_team = self.client.get_team_details(team_id)

                description = detailed_team.get("description")
                if not description or description.strip() == "":
                    description = f"Team {detailed_team.get('name', 'Unknown')}"  # Since description is required by Squadcast Terraform provider

                team = SquadcastTeam(
                    name=detailed_team.get("name", ""),
                    description=description,
                )

                self.exporter.add_resource(team)

                team_members = detailed_team.get("members", [])
                team_name = detailed_team.get("name", "Unknown")

                for member in tqdm(
                    team_members,
                    desc=f"Adding members to {team_name}",
                    unit="member",
                    leave=False,
                ):
                    og_user_id = member.get("user", {}).get("id")
                    if not og_user_id or og_user_id not in self.user_mapping:
                        logger.warning(
                            f"User {member.get('user', {}).get('username')} not found in migration map, skipping"
                        )
                        continue
                    self.exporter.add_resource(
                        SquadcastTeamMember(
                            team_id=team.terraform_id_reference,
                            user_id=self.user_mapping[
                                og_user_id
                            ].terraform_id_reference,
                        )
                    )

                self.team_mapping[team_id] = team

                logger.info(f"Successfully migrated team: {detailed_team.get('name')}")
                success_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to migrate team {team_data.get('name', 'Unknown')}: {str(e)}"
                )
                failure_count += 1
                errors.append(str(e))

        return SourceMigratorStats(
            total_count=len(opsgenie_teams),
            success_count=success_count,
            failure_count=failure_count,
            errors=errors,
        )

    def transform(self):
        # Migrate users
        logger.info("🚀 Starting user migration from Opsgenie to Terraform")
        user_result = self._migrate_users()
        logger.info(
            f"📊 User migration summary → "
            f"Total: {user_result.total_count}, "
            f"✅ Success: {user_result.success_count}, "
            f"❌ Failed: {user_result.failure_count}"
        )

        # Migrate teams
        logger.info("🚀 Starting team migration from Opsgenie to Terraform")
        team_result = self._migrate_teams()
        logger.info(
            f"📊 Team migration summary → "
            f"Total: {team_result.total_count}, "
            f"✅ Success: {team_result.success_count}, "
            f"❌ Failed: {team_result.failure_count}"
        )
