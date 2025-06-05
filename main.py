# #!/usr/bin/env python3
# import click
import logging
# import sys
# import os
# from typing import Optional
# from datetime import datetime

# from config.config import settings
from src.opsgenie.client import OpsGenieClient
from src.squadcast.client import SquadcastClient
from src.migrators.opsgenie_migrator import OpsGenieMigrator
# from src.migrators.user_migrator import UserMigrator
# from src.migrators.team_migrator import TeamMigrator
# from src.logging import formatter
# from src.db.db_manager import DBManager

# os.makedirs("logs", exist_ok=True)

# log_filename = f"logs/migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# custom_formatter = formatter.CustomFormatter(log_format)

# # Configure root logger for all modules
# root_logger = logging.getLogger()
# root_logger.setLevel(settings.log_level)
# root_logger.handlers.clear()

# # Add console handler
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setFormatter(custom_formatter)
# root_logger.addHandler(console_handler)

# # Add file handler
# file_handler = logging.FileHandler(log_filename)
# file_handler.setFormatter(custom_formatter)
# root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)
# logger.propagate = True

# logger.info(f"💾 Logs will be stored in: {log_filename}")


# @click.group()
# @click.option(
#     "--system",
#     "-s",
#     type=click.Choice(["opsgenie", "pagerduty"], case_sensitive=False),
#     help="Source alerting system to migrate from (opsgenie or pagerduty)",
# )
# @click.option("--opsgenie-api-key", "-o", help="OpsGenie API key")
# @click.option("--pagerduty-api-token", "-p", help="PagerDuty API token")
# @click.option("--squadcast-refresh-token", "-s", help="Squadcast refresh token")
# @click.option(
#     "--dry-run/--no-dry-run",
#     default=True,
#     is_flag=True,
#     help="Run in dry-run mode (no actual changes)",
# )
# @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
# @click.option(
#     "--db-path",
#     default="migration_data.db",
#     help="Path to the SQLite database file to track failed migrations",
# )
# @click.pass_context
# def cli(
#     ctx,
#     opsgenie_api_key: Optional[str],
#     pagerduty_api_token: Optional[str],
#     squadcast_refresh_token: Optional[str],
#     system: Optional[str],
#     dry_run: bool,
#     verbose: bool,
#     db_path: str = "migration_data.db",
# ):
#     """
#     Squadcast Migration Tool.
#     """
#     if verbose:
#         logging.getLogger().setLevel(logging.DEBUG)

#     if opsgenie_api_key:
#         settings.opsgenie_api_key = opsgenie_api_key

#     if squadcast_refresh_token:
#         settings.squadcast_refresh_token = squadcast_refresh_token

#     if pagerduty_api_token:
#         settings.pagerduty_api_token = pagerduty_api_token

#     if system:
#         settings.system = system

#     settings.dry_run = dry_run

#     # Store clients in context for sub-commands
#     ctx.ensure_object(dict)
#     if settings.system == "opsgenie":
#         ctx.obj["source_client"] = OpsGenieClient()
#     elif settings.system == "pagerduty":
#         ctx.obj["source_client"] = None  # Replace with PagerDutyClient() if needed
#     ctx.obj["squadcast_client"] = SquadcastClient()

#     ctx.obj["db_manager"] = DBManager(db_path=db_path)

#     if dry_run:
#         logger.info("Running in DRY RUN mode. No changes will be made.")


# @cli.command("migrate-users")
# @click.pass_context
# def migrate_users(ctx):
#     """Migrate users to Squadcast."""
#     source_client = ctx.obj["source_client"]
#     squadcast_client = ctx.obj["squadcast_client"]
#     db_manager: DBManager = ctx.obj["db_manager"]

#     logger.info("🚀 Starting user migration...")

#     migrator = UserMigrator(source_client, squadcast_client, db_manager=db_manager)
#     result = migrator.migrate()
#     ctx.obj["total_user_count"] = result.total_count

#     logger.info("✅ User migration completed.")
#     logger.info(
#         f"📊 Summary → Total: {result.total_count}, "
#         f"✅ Success: {result.success_count}, "
#         f"⏭️ Skipped: {result.skipped_count}, "
#         f"❌ Failed: {result.failure_count}"
#     )

#     if result.failure_count > 0:
#         logger.warning("⚠️ Some users failed to migrate and were saved to the database.")
#         logger.info("🔄 You can retry them later using: `uv run main.py retry-failed-users`")


# @cli.command("migrate-teams")
# @click.pass_context
# def migrate_teams(ctx):
#     """Migrate teams to Squadcast."""
#     source_client = ctx.obj["source_client"]
#     squadcast_client = ctx.obj["squadcast_client"]
#     db_manager: DBManager = ctx.obj["db_manager"]
    
#     logger.info("🚀 Starting team migration...")

#     user_migrations = db_manager.get_all_migration_maps("user")
#     if not user_migrations:
#         logger.warning(
#             "⚠️ No user migration map provided — teams will be migrated without members. Please run `migrate-users` first if needed."
#         )
#     else:
#         logger.info(f"👤 Found {len(user_migrations)} user migrations. Proceeding with team migration...")
#     user_migration_map = {user["source_id"]: user["squadcast_id"] for user in user_migrations}

#     migrator = TeamMigrator(source_client, squadcast_client, db_manager=db_manager, user_migration_map=user_migration_map)
#     result = migrator.migrate()

#     logger.info("✅ Team migration completed.")
#     logger.info(
#         f"📊 Summary → Total: {result.total_count}, "
#         f"✅ Success: {result.success_count}, "
#         f"⏭️ Skipped: {result.skipped_count}, "
#         f"❌ Failed: {result.failure_count}"
#     )

#     if result.failure_count > 0:
#         logger.warning("⚠️ Some teams failed to migrate. Check logs above for details.")
#         logger.info("🔄 You can retry them later using: `uv run main.py retry-failed-teams`")

# @cli.command("migrate-all")
# @click.pass_context
# def migrate_all(ctx):
#     """Migrate all entities to Squadcast."""
#     logger.info(f"Starting full migration from {settings.system} to Squadcast")

#     ctx.invoke(migrate_users)
#     ctx.invoke(migrate_teams)

#     # Add other migration commands here as they are implemented

#     logger.info("✅ Full migration completed successfully.")

# @cli.command("retry-failed-users")
# @click.pass_context
# def retry_failed_users(ctx):
#     """Retry previously failed user migrations."""
#     source_client = ctx.obj["source_client"]
#     squadcast_client = ctx.obj["squadcast_client"]
#     db_manager: DBManager = ctx.obj["db_manager"]

#     logger.info("🔄 Starting retry of failed user migrations...")

#     migrator = UserMigrator(source_client, squadcast_client, db_manager=db_manager)
#     result = migrator.retry_failed_migrations()

#     logger.info("✅ Retry of user migrations completed.")
#     logger.info(
#         f"📊 Summary → Total: {result.total_count}, "
#         f"✅ Success: {result.success_count}, "
#         f"⏭️ Skipped: {result.skipped_count}, "
#         f"❌ Failed: {result.failure_count}"
#     )

#     if result.failure_count > 0:
#         logger.warning("⚠️ Some users still failed to migrate. Check logs above for details.")
    
# @cli.command("retry-failed-teams")
# @click.pass_context
# def retry_failed_teams(ctx):
#     """Retry previously failed team migrations."""
#     source_client = ctx.obj["source_client"]
#     squadcast_client = ctx.obj["squadcast_client"]
#     db_manager: DBManager = ctx.obj["db_manager"]

#     logger.info("🔄 Starting retry of failed team migrations...")

#     migrator = TeamMigrator(source_client, squadcast_client, db_manager=db_manager)
#     result = migrator.retry_failed_migrations()

#     logger.info("✅ Retry of team migrations completed.")
#     logger.info(
#         f"📊 Summary → Total: {result.total_count}, "
#         f"✅ Success: {result.success_count}, "
#         f"⏭️ Skipped: {result.skipped_count}, "
#         f"❌ Failed: {result.failure_count}"
#     )

#     if result.failure_count > 0:
#         logger.warning("⚠️ Some teams still failed to migrate. Check logs above for details.")


# @cli.command("list-failed-migrations")
# @click.option(
#     "--entity-type",
#     type=click.Choice(["user", "team"]),
#     help="Type of failed migrations to list (user or team)",
# )
# @click.option(
#     "--status",
#     default="failed",
#     type=click.Choice(["failed", "retried", "resolved"]),
#     help="Status of migrations to list",
# )
# @click.pass_context
# def list_failed_migrations(ctx, entity_type, status):
#     """List all failed migrations stored in the database."""
#     db_manager: DBManager = ctx.obj["db_manager"]

#     failed_migrations = db_manager.get_failed_migrations(entity_type=entity_type, status=status)
#     if not failed_migrations:
#         logger.info(f"No {status} migrations found" + (f" for {entity_type}" if entity_type else ""))
#         return
    
#     logger.info(f"Found {len(failed_migrations)} {status} migrations" + (f" for {entity_type}" if entity_type else ""))
    
#     for migration in failed_migrations:
#         entity_data = migration["entity_data"]
#         logger.info(
#             f"ID: {migration['id']}, "
#             f"Source ID: {migration['source_id']}, "
#             f"Entity Type: {migration['entity_type']}, "
#             f"Name: {entity_data.get('fullName', 'Unknown') if migration['entity_type'] == 'user' else entity_data.get('name', 'Unknown')}, "
#             f"Retry Count: {migration['retry_count']}, "
#             f"Error: {migration['error_message']}, "
#             f"Additional Info: {migration.get('additional_info', 'N/A')}, "
#         )

# if __name__ == "__main__":
#     cli(obj={})

def main():
    """Main entry point for the migration toolkit."""
    logger.info("Starting Opsgenie to Squadcast migration")

    opsgenie_client = OpsGenieClient()
    squadcast_client = SquadcastClient()
    opsgenie_migrator = OpsGenieMigrator(opsgenie_client, squadcast_client)

    opsgenie_migrator.migrate_users()
    opsgenie_migrator.migrate_teams()

    logger.info("Opsgenie to Squadcast migration completed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()