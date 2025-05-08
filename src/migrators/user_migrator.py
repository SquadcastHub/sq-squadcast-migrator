import logging
from typing import Dict, Any
from src.opsgenie.client import OpsGenieClient
from src.squadcast.client import SquadcastClient
from tqdm import tqdm

logger = logging.getLogger(__name__)

class UserMigrator:
    """Migrates users from OpsGenie to Squadcast."""
    
    def __init__(self, opsgenie_client: OpsGenieClient, squadcast_client: SquadcastClient):
        """
        Initialize the user migrator.
        
        Args:
            opsgenie_client: OpsGenie API client
            squadcast_client: Squadcast API client
        """
        self.opsgenie_client = opsgenie_client
        self.squadcast_client = squadcast_client
        self.migration_map = {}  # Maps OpsGenie IDs to Squadcast IDs
        
    def _transform_user(self, opsgenie_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an OpsGenie user to Squadcast user format.
        
        Args:
            opsgenie_user: User data from OpsGenie
            
        Returns:
            User data in Squadcast format
        """
        full_name = opsgenie_user.get('fullName', '')
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": opsgenie_user.get("username"),
            "role": "user",
        }
    
    def migrate(self) -> Dict[str, Any]:
        """
        Migrate all users from OpsGenie to Squadcast.
        
        Returns:
            Dictionary with migration statistics
        """
        logger.info("Starting user migration from OpsGenie to Squadcast")
        
        opsgenie_users = self.opsgenie_client.get_users()
        logger.info(f"Found {len(opsgenie_users)} users in OpsGenie")
        
        success_count = 0
        failure_count = 0
        skipped_count = 0
        
        for user in tqdm(opsgenie_users, desc="Migrating users"):
            try:
                squadcast_user_data = self._transform_user(user)
                
                squadcast_user = self.squadcast_client.create_user(squadcast_user_data)
                
                self.migration_map[user.get("id")] = squadcast_user.get("id")
                
                logger.info(f"Successfully migrated user: {user.get('username')}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate user {user.get('username')}: {str(e)}")
                failure_count += 1
        
        return {
            "total": len(opsgenie_users),
            "success": success_count,
            "failure": failure_count,
            "skipped": skipped_count,
            "migration_map": self.migration_map
        }