import logging
from typing import Dict, Any, List
import click
from src.alerting_client import AlertingClient
from src.squadcast.client import SquadcastClient
from tqdm import tqdm
from config.config import settings

logger = logging.getLogger(__name__)

class TeamMigrator:
    """Migrates teams from an alerting system to Squadcast."""
    
    def __init__(self, source_client: AlertingClient, squadcast_client: SquadcastClient, user_migration_map: Dict[str, str] = None):
        """
        Initialize the team migrator.
        
        Args:
            source_client: Source alerting system client (implements AlertingClient)
            squadcast_client: Squadcast API client
            user_migration_map: Optional mapping of source user IDs to Squadcast user IDs
        """
        self.source_client = source_client
        self.squadcast_client = squadcast_client
        self.user_migration_map = user_migration_map or {}
        self.selected_team = None  # Selected team for squad migration
        self.migration_map = {}  # Maps source team IDs to Squadcast team IDs
        self.migration_mode = None  # Will be set during migration based on user input
    
    def migrate(self) -> Dict[str, Any]:
        """
        Migrate all teams from source alerting system to Squadcast.
        
        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting team migration from {settings.system} to Squadcast")
        
        self._prompt_migration_mode()
        
        source_teams = self.source_client.get_teams()
        logger.info(f"Found {len(source_teams)} teams in {settings.system}")
        
        success_count = 0
        failure_count = 0
        skipped_count = 0

        if self.migration_mode == "squads_in_team":
            sq_teams = self.squadcast_client.get_all_teams()
            logger.info(f"Found {len(sq_teams)} teams in Squadcast")
            team_name = click.prompt(
                "Select a team to migrate squads into",
                type=click.Choice([t.get("name") for t in sq_teams]),
                default=sq_teams[0].get("name"),
                show_choices=True
            )
            self.selected_team = next((t for t in sq_teams if t.get("name") == team_name), None)
            if not self.selected_team:
                logger.warning(f"Selected team not found in Squadcast: {team_name}")
            else:
                logger.info(f"Selected team for squad migration: {self.selected_team.get('name')}")

        
        for team in tqdm(source_teams, desc="Migrating teams"):
            try:
                team_id = team.get("id")
                if not team_id:
                    logger.warning(f"Team without ID found, skipping: {team}")
                    skipped_count += 1
                    continue
                
                team_data = self.source_client.get_team_details(team_id)
                sq_team_data = self.source_client.transform_team(
                    team_data, 
                    self.user_migration_map,
                    migration_mode=self.migration_mode
                )
                
                if self.migration_mode == "separate_teams":
                    sq_team = self.squadcast_client.create_team(sq_team_data)
                    self.migration_map[team_id] = sq_team.get("id")
                    
                    logger.info(f"Successfully migrated team: {team.get('name')}")
                else:
                    sq_squad = self.squadcast_client.create_squad(
                        self.selected_team,
                        squad_data=sq_team_data
                    )
                    self.migration_map[team_id] = sq_squad.get("id")
                    logger.info(f"Successfully migrated team {team.get('name')} as a squad in {self.selected_team.get('name')}")
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate team {team.get('name', 'Unknown')}: {str(e)}")
                failure_count += 1
        
        return {
            "total": len(source_teams),
            "success": success_count,
            "failure": failure_count,
            "skipped": skipped_count,
            "migration_map": self.migration_map,
            "migration_mode": self.migration_mode
        }
    
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
            show_choices=False
        )
        
        if choice == "1":
            self.migration_mode = "separate_teams"
            logger.info("Migration mode: Teams will be migrated as separate teams")
        else:
            self.migration_mode = "squads_in_team"
            logger.info("Migration mode: Teams will be migrated as squads within a single team")