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

os.makedirs('logs', exist_ok=True)

log_filename = f"logs/migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Set up logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename)
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Logs will be stored in: {log_filename}")

@click.group()
@click.option('--opsgenie-api-key', '-o', help='OpsGenie API key')
@click.option('--squadcast-refresh-token', '-s', help='Squadcast refresh token')
@click.option('--dry-run/--no-dry-run', default=False, 
              help='Run in dry-run mode (no actual changes)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, opsgenie_api_key: Optional[str], squadcast_refresh_token: Optional[str], 
        dry_run: bool, verbose: bool):
    """
    OpsGenie to Squadcast Migration Tool.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if opsgenie_api_key:
        settings.opsgenie_api_key = opsgenie_api_key
    
    if squadcast_refresh_token:
        settings.squadcast_refresh_token = squadcast_refresh_token
    
    settings.dry_run = dry_run
    
    # Store clients in context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj['opsgenie_client'] = OpsGenieClient()
    ctx.obj['squadcast_client'] = SquadcastClient()
    
    if dry_run:
        logger.info("Running in DRY RUN mode. No changes will be made.")


@cli.command('migrate-users')
@click.pass_context
def migrate_users(ctx):
    """Migrate users from OpsGenie to Squadcast."""
    opsgenie_client = ctx.obj['opsgenie_client']
    squadcast_client = ctx.obj['squadcast_client']
    
    migrator = UserMigrator(opsgenie_client, squadcast_client)
    result = migrator.migrate()
    ctx.obj['user_migration_map'] = result.get('migration_map', {})
    
    logger.info("User migration completed.")
    logger.info(f"Total: {result['total']}, Success: {result['success']}, "
                f"Failed: {result['failure']}, Skipped: {result['skipped']}")


@cli.command('migrate-all')
@click.pass_context
def migrate_all(ctx):
    """Migrate all entities from OpsGenie to Squadcast."""
    logger.info("Starting full migration from OpsGenie to Squadcast")
    
    ctx.invoke(migrate_users)
    # Add other migration commands here 
    
    logger.info("Full migration completed successfully.")


if __name__ == '__main__':
    cli(obj={})