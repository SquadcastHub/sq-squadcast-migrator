import logging
from typing import Dict, Optional
import click
from src.alerting_client import AlertingClient
from src.squadcast.client import SquadcastClient
from tqdm import tqdm
from config.config import settings
from src.schemas.migration import TeamMigrationStats
from src.db.db_manager import DBManager
from src.schemas.team import CreateTeamRequest, Team
from src.schemas.squad import CreateSquadRequest

logger = logging.getLogger(__name__)


class TeamMigrator:
    """Migrates teams from an alerting system to Squadcast."""

    def __init__(
        self,
        source_client: AlertingClient,
        squadcast_client: SquadcastClient,
        db_manager: Optional[DBManager] = None,
        user_migration_map: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the team migrator.

        Args:
            source_client: Source alerting system client (implements AlertingClient)
            squadcast_client: Squadcast API client
        """
        self.source_client = source_client
        self.squadcast_client = squadcast_client
        self.db_manager = db_manager or DBManager()

        self.user_migration_map = user_migration_map or {}
        self.selected_team = None  # Selected team for squad migration
        self.migration_mode = None  # Will be set during migration based on user input

    def _prompt_migration_mode(self):
        """
        Prompt the user to choose a migration mode.
        """
        click.echo("\n🔄 Team Migration Options:\n")
        click.echo("1) Migrate as separate teams in Squadcast (default)")
        click.echo("2) Migrate as squads within a single team in Squadcast\n")

        choice = click.prompt(
            "Choose migration mode",
            type=click.Choice(["1", "2"]),
            default="1",
            show_choices=False,
        )

        if choice == "1":
            self.migration_mode = "separate_teams"
            logger.info("Migration mode: Teams will be migrated as separate teams")
        else:
            self.migration_mode = "squads_in_team"
            logger.info(
                "Migration mode: Teams will be migrated as squads within a single team"
            )

    def migrate(self) -> TeamMigrationStats:
        """
        Migrate all teams from source alerting system to Squadcast.

        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting team migration from {settings.system} to Squadcast")

        self._prompt_migration_mode()

        source_teams = self.source_client.get_teams()
        logger.info(f"Found {len(source_teams)} teams in {settings.system}")

        migration_stats = TeamMigrationStats(
            total_count=len(source_teams),
            migration_mode=self.migration_mode,
            skipped_count=0,
            success_count=0,
            failure_count=0,
            errors=[]
        )

        if self.migration_mode == "squads_in_team":
            sq_teams = self.squadcast_client.get_all_teams()
            logger.info(f"Found {len(sq_teams)} teams in Squadcast")
            team_name = click.prompt(
                "Select a team to migrate squads into",
                type=click.Choice([t.name for t in sq_teams]),
                default=sq_teams[0].name,
                show_choices=True,
            )
            self.selected_team = next(
                (t for t in sq_teams if t.name == team_name), None
            )
            if not self.selected_team:
                logger.warning(f"Selected team not found in Squadcast: {team_name}")
            else:
                logger.info(
                    f"Selected team for squad migration: {self.selected_team.name}"
                )

        for source_team in tqdm(source_teams, desc="Migrating teams"):
            try:
                team_id = source_team.get("id")
                if not team_id:
                    logger.warning(f"Team without ID found, skipping: {source_team}")
                    skipped_count += 1
                    continue
                    
                existing_map = self.db_manager.get_migration_map(
                    source_id=team_id,
                    source_system=settings.system,
                    entity_type="team"
                )
                if existing_map:
                    logger.info(
                        f"Skipping team {source_team.get('name')} ({team_id}) - already migrated"
                    )
                    migration_stats.skipped_count += 1
                    continue

                team_data = self.source_client.get_team_details(team_id)
                sq_team_data = self.source_client.transform_team(
                    team_data,
                    self.user_migration_map,
                    migration_mode=self.migration_mode,
                )

                if self.migration_mode == "separate_teams":
                    response = self.squadcast_client.create_team(sq_team_data)
                    sq_team = response.team
                    self.db_manager.record_migration_map(
                        source_id=team_id,
                        squadcast_id=sq_team.id,
                        source_system=settings.system,
                        entity_type="team",
                    )

                    logger.info(f"Successfully migrated team: {sq_team.name}")
                else:
                    response = self.squadcast_client.create_squad(
                        self.selected_team, squad_data=sq_team_data
                    )
                    sq_squad = response.squad
                    self.db_manager.record_migration_map(
                        source_id=team_id,
                        squadcast_id=sq_squad.id,
                        source_system=settings.system,
                        entity_type="team",
                    )
                    logger.info(
                        f"Successfully migrated team {source_team.get('name')} as a squad in {self.selected_team.name}"
                    )

                migration_stats.success_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to migrate team {source_team.get('name', 'Unknown')}: {str(e)}"
                )

                self.db_manager.record_failed_migration(
                    source_id=source_team.get("id", "unknown"),
                    source_system=settings.system,
                    entity_type="team",
                    entity_data=sq_team_data.model_dump(),
                    error_message=str(e),
                    additional_info={
                        "migration_mode": self.migration_mode,
                        "selected_team": {"id": self.selected_team.id, "name": self.selected_team.name} if self.selected_team else None,
                    }
                )

                migration_stats.failure_count += 1
                migration_stats.errors.append(
                    f"Failed to migrate team {source_team.get('name', 'Unknown')}: {str(e)}"
                )

        return migration_stats

    def retry_failed_migrations(self) -> TeamMigrationStats:
        """
        Retry previously failed team migrations.

        Returns:
            Dictionary with retry migration statistics
        """
        logger.info(f"Starting retry of failed team migrations from {settings.system}")

        failed_migrations = self.db_manager.get_failed_migrations(entity_type="team", status="failed")
        if not failed_migrations:
            logger.info("No failed team migrations to retry")
            return TeamMigrationStats(
                total_count=0,
                success_count=0,
                failure_count=0,
                skipped_count=0,
                errors=[],
            )
            
        migration_stats = TeamMigrationStats(
            total_count=len(failed_migrations),
            success_count=0,
            failure_count=0,
            skipped_count=0,
            errors=[],
        )
        logger.info(f"Found {len(failed_migrations)} failed team migrations to retry")

        for failed_migration in tqdm(failed_migrations, desc="Retrying failed team migrations"):
            record_id = failed_migration["id"]
            sq_team_data = failed_migration["entity_data"]
            source_id = failed_migration["source_id"]
            additional_info = failed_migration.get("additional_info", {})
            migration_mode = additional_info.get("migration_mode", "separate_teams")
            selected_team = Team(**additional_info.get("selected_team", {})) if additional_info.get("selected_team") else None
            logger.info(f"Retrying migration for team {sq_team_data.get('name', 'Unknown')} (ID: {source_id})")

            try:
                if migration_mode == "separate_teams":
                    response = self.squadcast_client.create_team(team_data=CreateTeamRequest(**sq_team_data))
                    sq_team = response.team
                    self.db_manager.record_migration_map(
                        source_id=source_id,
                        squadcast_id=sq_team.id,
                        source_system=settings.system,
                        entity_type="team",
                    )

                    logger.info(f"Successfully migrated team: {sq_team.name}")
                else:
                    if not selected_team:
                        logger.error(
                            "No selected team found for squad migration, skipping"
                        )
                        migration_stats.skipped_count += 1
                        continue

                    response = self.squadcast_client.create_squad(
                        selected_team, squad_data=CreateSquadRequest(**sq_team_data)
                    )
                    sq_squad = response.squad
                    self.db_manager.record_migration_map(
                        source_id=source_id,
                        squadcast_id=sq_squad.id,
                        source_system=settings.system,
                        entity_type="team",
                    )
                    logger.info(
                        f"Successfully migrated team {sq_squad.name} as a squad in {selected_team.name}"
                    )

                logger.info(
                    f"Successfully migrated team on retry: {sq_team_data.get('name')} ({source_id})"
                )
                
                self.db_manager.update_migration_status(record_id, status="resolved")
                
                migration_stats.success_count += 1

            except Exception as e:
                error_message = f"Failed to migrate team {sq_team_data.get('name')} on retry: {str(e)}"
                logger.error(error_message)
                
                self.db_manager.increment_retry_count(record_id)
                self.db_manager.update_migration_status(
                    record_id,
                    status="failed",
                    error_message=str(e),
                )

                migration_stats.errors.append(error_message)
                migration_stats.failure_count += 1

        return migration_stats

