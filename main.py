#!/usr/bin/env python3
import click
import logging
import sys
import os
from typing import Optional
from datetime import datetime

from config.config import settings
from src.opsgenie.client import OpsGenieClient
from src.squadcast.client import SquadcastClient
from src.migrators.user_migrator import UserMigrator
from src.migrators.team_migrator import TeamMigrator
from src.logging import formatter

os.makedirs('logs', exist_ok=True)

log_filename = f"logs/migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
custom_formatter = formatter.CustomFormatter(log_format)

# Configure root logger for all modules
root_logger = logging.getLogger()
root_logger.setLevel(settings.log_level)
root_logger.handlers.clear()

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(custom_formatter)
root_logger.addHandler(console_handler)

# Add file handler
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(custom_formatter)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)
logger.propagate = True

logger.info(f"Logs will be stored in: {log_filename}")

@click.group()
@click.option('--system', '-s', type=click.Choice(['opsgenie', 'pagerduty'], case_sensitive=False), help='Source alerting system to migrate from (opsgenie or pagerduty)')
@click.option('--opsgenie-api-key', '-o', help='OpsGenie API key')
@click.option('--pagerduty-api-token', '-p', help='PagerDuty API token')
@click.option('--squadcast-refresh-token', '-s', help='Squadcast refresh token')
@click.option('--dry-run/--no-dry-run', default=True, is_flag=True, help='Run in dry-run mode (no actual changes)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, opsgenie_api_key: Optional[str], pagerduty_api_token: Optional[str], squadcast_refresh_token: Optional[str], 
        system: Optional[str],
        dry_run: bool, verbose: bool):
    """
    Squadcast Migration Tool.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if opsgenie_api_key:
        settings.opsgenie_api_key = opsgenie_api_key
    
    if squadcast_refresh_token:
        settings.squadcast_refresh_token = squadcast_refresh_token
    
    if pagerduty_api_token:
        settings.pagerduty_api_token = pagerduty_api_token

    if system:
        settings.system = system
    
    settings.dry_run = dry_run
    
    # Store clients in context for sub-commands
    ctx.ensure_object(dict)
    if settings.system == "opsgenie":
        ctx.obj['source_client'] = OpsGenieClient()
    elif settings.system == "pagerduty":
        ctx.obj['source_client'] = None # Replace with PagerDutyClient() if needed
    ctx.obj['squadcast_client'] = SquadcastClient()
    
    if dry_run:
        logger.info("Running in DRY RUN mode. No changes will be made.")


@cli.command('migrate-users')
@click.pass_context
def migrate_users(ctx):
    """Migrate users to Squadcast."""
    source_client = ctx.obj['source_client']
    squadcast_client = ctx.obj['squadcast_client']
    
    migrator = UserMigrator(source_client, squadcast_client)
    result = migrator.migrate()
    ctx.obj['user_migration_map'] = result.get('migration_map', {})
    
    logger.info("User migration completed successfully ✅")
    logger.info(f"Total: {result['total']}, Success: {result['success']}, "
                f"Failed: {result['failure']}, Skipped: {result['skipped']}")


@cli.command('migrate-teams')
@click.pass_context
def migrate_teams(ctx):
    """Migrate teams to Squadcast."""
    source_client = ctx.obj['source_client']
    squadcast_client = ctx.obj['squadcast_client']
    
    user_migration_map = ctx.obj.get('user_migration_map', {})
    if not user_migration_map:
        logger.warning("No user migration map found. Teams will be created without members.")
    
    migrator = TeamMigrator(source_client, squadcast_client, user_migration_map)
    result = migrator.migrate()
    ctx.obj['team_migration_map'] = result.get('migration_map', {})
    
    logger.info("Team migration completed successfully ✅")
    logger.info(f"Total: {result['total']}, Success: {result['success']}, "
                f"Failed: {result['failure']}, Skipped: {result['skipped']}")


@cli.command('migrate-all')
@click.pass_context
def migrate_all(ctx):
    """Migrate all entities to Squadcast."""
    logger.info(f"Starting full migration from {settings.system} to Squadcast")
    
    ctx.invoke(migrate_users)
    ctx.invoke(migrate_teams)
    
    # Add other migration commands here as they are implemented
    
    logger.info("Full migration completed successfully ✅")


if __name__ == '__main__':
    cli(obj={})