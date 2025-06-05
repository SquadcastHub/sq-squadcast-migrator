import logging
from typing import Optional
from src.alerting_client import AlertingClient
from src.squadcast.client import SquadcastClient
from src.db.db_manager import DBManager
from tqdm import tqdm
from config.config import settings
from src.schemas.migration import UserMigrationStats

logger = logging.getLogger(__name__)


class UserMigrator:
    """Migrates users from an alerting system to Squadcast."""

    def __init__(
        self, source_client: AlertingClient, squadcast_client: SquadcastClient,
        db_manager: Optional[DBManager] = None
    ):
        """
        Initialize the user migrator.

        Args:
            source_client: Source alerting system client (implements AlertingClient)
            squadcast_client: Squadcast API client
            db_manager: Database manager for tracking failed migrations (optional)
        """
        self.source_client = source_client
        self.squadcast_client = squadcast_client
        # Initialize DB manager if not provided
        self.db_manager = db_manager or DBManager()

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
            errors=[],
        )
        logger.info(f"Found {len(source_users)} users in {settings.system}")

        # source_users = source_users[:1]

        for source_user in tqdm(source_users, desc="Migrating users"):
            try:
                existing_map = self.db_manager.get_migration_map(
                    source_id=source_user.get("id"),
                    source_system=settings.system,
                    entity_type="user"
                )
                if existing_map:
                    logger.info(
                        f"Skipping user {source_user.get('username')} ({source_user.get('id')}) - already migrated"
                    )
                    migration_stats.skipped_count += 1
                    continue

                sq_user_data = self.source_client.transform_user(source_user)
                response = self.squadcast_client.create_user(user_data=sq_user_data)
                sq_user = response.user

                logger.info(
                    f"Successfully migrated user: {source_user.get('username')} ({sq_user.id})"
                )
                self.db_manager.record_migration_map(
                    source_id=source_user.get("id"),
                    squadcast_id=sq_user.id,
                    source_system=settings.system,
                    entity_type="user",
                )
                migration_stats.success_count += 1

            except Exception as e:
                error_message = f"Failed to migrate user {source_user.get('username')}: {str(e)}"
                logger.error(error_message)
                
                self.db_manager.record_failed_migration(
                    source_id=source_user.get("id"),
                    source_system=settings.system,
                    entity_type="user",
                    entity_data=source_user,
                    error_message=str(e)
                )
                logger.debug(f"Recorded failed migration for user {source_user.get('id')}.")
                migration_stats.errors.append(error_message)
                migration_stats.failure_count += 1

        return migration_stats

    def retry_failed_migrations(self) -> UserMigrationStats:
        """
        Retry previously failed user migrations.

        Returns:
            Dictionary with retry migration statistics
        """
        logger.info(f"Starting retry of failed user migrations from {settings.system}")
        
        failed_migrations = self.db_manager.get_failed_migrations(entity_type="user", status="failed")
        if not failed_migrations:
            logger.info("No failed user migrations to retry")
            return UserMigrationStats(
                total_count=0,
                success_count=0,
                failure_count=0,
                skipped_count=0,
                errors=[],
            )
            
        migration_stats = UserMigrationStats(
            total_count=len(failed_migrations),
            success_count=0,
            failure_count=0,
            skipped_count=0,
            errors=[],
        )
        logger.info(f"Found {len(failed_migrations)} failed user migrations to retry")

        for failed_migration in tqdm(failed_migrations, desc="Retrying failed user migrations"):
            record_id = failed_migration["id"]
            source_user = failed_migration["entity_data"]
            source_id = failed_migration["source_id"]
            
            try:
                sq_user_data = self.source_client.transform_user(source_user)
                response = self.squadcast_client.create_user(user_data=sq_user_data)
                sq_user = response.user

                logger.info(
                    f"Successfully migrated user on retry: {source_user.get('username')} ({sq_user.id})"
                )
                
                self.db_manager.update_migration_status(record_id, status="resolved")
                
                migration_stats.success_count += 1
                self.db_manager.record_migration_map(
                    source_id=source_id,
                    squadcast_id=sq_user.id,
                    source_system=settings.system,
                    entity_type="user",
                )

            except Exception as e:
                error_message = f"Failed to migrate user {source_user.get('username')} on retry: {str(e)}"
                logger.error(error_message)
                
                # Update retry count and error message
                self.db_manager.increment_retry_count(record_id)
                self.db_manager.update_migration_status(
                    record_id, 
                    status="failed", 
                    error_message=str(e)
                )
                
                migration_stats.errors.append(error_message)
                migration_stats.failure_count += 1

        return migration_stats
