import logging
from typing import Dict, Any
from src.alerting_client import AlertingClient
from src.squadcast.client import SquadcastClient
from tqdm import tqdm
from config.config import settings

logger = logging.getLogger(__name__)

class UserMigrator:
    """Migrates users from an alerting system to Squadcast."""
    
    def __init__(self, source_client: AlertingClient, squadcast_client: SquadcastClient):
        """
        Initialize the user migrator.
        
        Args:
            source_client: Source alerting system client (implements AlertingClient)
            squadcast_client: Squadcast API client
        """
        self.source_client = source_client
        self.squadcast_client = squadcast_client
        self.migration_map = {}  # Maps source IDs to Squadcast IDs
    
    def migrate(self) -> Dict[str, Any]:
        """
        Migrate all users from source alerting system to Squadcast.
        
        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting user migration from {settings.system} to Squadcast")
        
        source_users = self.source_client.get_users()
        logger.info(f"Found {len(source_users)} users in {settings.system}")
        
        success_count = 0
        failure_count = 0
        skipped_count = 0
        
        for user in tqdm(source_users, desc="Migrating users"):
            try:
                sq_user_data = self.source_client.transform_user(user)
                
                sq_user = self.squadcast_client.create_user(sq_user_data)
                
                self.migration_map[user.get("id")] = sq_user.get("_id")
                
                logger.info(f"Successfully migrated user: {user.get('username')} ({sq_user.get('_id')})")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate user {user.get('username')}: {str(e)}")
                failure_count += 1
        
        return {
            "total": len(source_users),
            "success": success_count,
            "failure": failure_count,
            "skipped": skipped_count,
            "migration_map": self.migration_map
        }