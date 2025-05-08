import logging
from typing import Dict, Any, List
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
        self.migration_map = {}  # Maps source team IDs to Squadcast team IDs
    
    def migrate(self) -> Dict[str, Any]:
        """
        Migrate all teams from source alerting system to Squadcast.
        
        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting team migration from {settings.system} to Squadcast")
        
        source_teams = self.source_client.get_teams()
        logger.info(f"Found {len(source_teams)} teams in {settings.system}")
        
        success_count = 0
        failure_count = 0
        skipped_count = 0
        
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
                    self.user_migration_map
                )
                
                sq_team = self.squadcast_client.create_team(sq_team_data)

                self.migration_map[team_id] = sq_team.get("_id")
                
                logger.info(f"Successfully migrated team: {team.get('name')}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate team {team.get('name', 'Unknown')}: {str(e)}")
                failure_count += 1
        
        return {
            "total": len(source_teams),
            "success": success_count,
            "failure": failure_count,
            "skipped": skipped_count,
            "migration_map": self.migration_map
        }