import logging
from typing import Dict, Any
from src.alerting_client import AlertingClient
from src.squadcast.client import SquadcastClient
from tqdm import tqdm
from config.config import settings
from src.schemas.migration import UserMigrationStats

logger = logging.getLogger(__name__)


class UserMigrator:
    """Migrates users from an alerting system to Squadcast."""

    def __init__(
        self, source_client: AlertingClient, squadcast_client: SquadcastClient
    ):
        """
        Initialize the user migrator.

        Args:
            source_client: Source alerting system client (implements AlertingClient)
            squadcast_client: Squadcast API client
        """
        self.source_client = source_client
        self.squadcast_client = squadcast_client

    def migrate(self) -> UserMigrationStats:
        """
        Migrate all users from source alerting system to Squadcast.

        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting user migration from {settings.system} to Squadcast")
        
        source_users = self.source_client.get_users()
        migration_stats = UserMigrationStats(
            total_count=len(source_users),
            success_count=0,
            failure_count=0,
            skipped_count=0,
            migration_map={},
            errors=[],
        )
        logger.info(f"Found {len(source_users)} users in {settings.system}")

        for user in tqdm(source_users, desc="Migrating users"):
            try:
                sq_user_data = self.source_client.transform_user(user)
                sq_user = self.squadcast_client.create_user(user_data=sq_user_data)

                logger.info(
                    f"Successfully migrated user: {user.get('username')} ({sq_user.id})"
                )
                migration_stats.success_count += 1
                migration_stats.migration_map[user.get("id")] = sq_user.id

            except Exception as e:
                logger.error(f"Failed to migrate user {user.get('username')}: {str(e)}")
                migration_stats.errors.append(
                    f"Failed to migrate user {user.get('username')}: {str(e)}"
                )
                migration_stats.failure_count += 1

        return migration_stats
