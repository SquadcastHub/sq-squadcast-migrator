#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Dict, List
from src.opsgenie.client import OpsGenieClient
from src.terraform.config_manager import TerraformConfigManager
from src.terraform.models import SquadcastUser, SquadcastTeam, SquadcastEscalationPolicy
from src.opsgenie.client import OpsGenieClient
from src.schemas.migration import UserMigrationStats, TeamMigrationStats

logger = logging.getLogger(__name__)

class OpsGenieTerraformMigrator:
    """
    Migrates data from OpsGenie to Terraform configurations using the Terraform Config Manager.
    Instead of directly creating entities in Squadcast, this creates Terraform configurations
    that can be applied to create or update resources.
    """

    def __init__(self, output_dir: Path = None, 
                 provider_config: Dict[str, str] = None):
        """
        Initialize the OpsGenie Terraform Migrator.

        Args:
            opsgenie_client: An initialized OpsGenie client
            output_dir: Directory where Terraform files will be generated
            provider_config: Configuration for the Squadcast provider
        """
        self.opsgenie_client = OpsGenieClient()
        
        self.output_dir = output_dir or Path("terraform_output")
        
        self.provider_config = provider_config or {
        "region": "${var.squadcast_region}",
        "refresh_token": "${var.squadcast_refresh_token}"
    }
        
        self.config_manager = TerraformConfigManager(self.output_dir, self.provider_config)
        
        self.user_mapping = {}
        self.team_mapping = {}

    def migrate_users(self) -> UserMigrationStats:
        """
        Migrate users from OpsGenie to Terraform configurations.
        
        Returns:
            Dict with migration statistics
        """
        logger.info("Starting OpsGenie user migration to Terraform")
        
        # Get all users from OpsGenie
        opsgenie_users = self.opsgenie_client.get_users()
        logger.info(f"Found {len(opsgenie_users)} users in OpsGenie")
        
        success_count = 0
        failure_count = 0
        errors: List[str] = []
        
        for user_data in opsgenie_users:
            try:
                user_req = self.opsgenie_client.transform_user(user_data)
                
                user = SquadcastUser(
                    email=user_req.email,
                    first_name=user_req.first_name,
                    last_name=user_req.last_name,
                    role=user_req.role
                )
                
                self.config_manager.add_resource(user)
                
                self.user_mapping[user_data.get('id')] = user
                
                logger.info(f"Successfully migrated user: {user_req.email}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate user {user_data.get('username')}: {str(e)}")
                errors.append(str(e))
                failure_count += 1
        
        return UserMigrationStats(
            total_count=len(opsgenie_users),
            success_count=success_count,
            failure_count=failure_count,
            errors=errors
        )
    
    def migrate_teams(self) -> TeamMigrationStats:
        """
        Migrate teams from OpsGenie to Terraform configurations.
        
        Returns:
            Dict with migration statistics
        """
        logger.info("Starting OpsGenie team migration to Terraform")
        
        opsgenie_teams = self.opsgenie_client.get_teams()
        logger.info(f"Found {len(opsgenie_teams)} teams in OpsGenie")
        
        success_count = 0
        failure_count = 0
        errors: List[str] = []
        
        for team_data in opsgenie_teams:
            try:
                team_id = team_data.get('id')
                if not team_id:
                    logger.warning(f"Team without ID found, skipping: {team_data}")
                    continue
                
                detailed_team = self.opsgenie_client.get_team_details(team_id)
                
                team = SquadcastTeam(
                    display_name=detailed_team.get('name', ''),
                    description=detailed_team.get('description', '')
                )
                
                self.config_manager.add_resource(team)
                
                self.team_mapping[team_id] = team
                
                logger.info(f"Successfully migrated team: {detailed_team.get('name')}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate team {team_data.get('name', 'Unknown')}: {str(e)}")
                failure_count += 1
                errors.append(str(e))
        
        return TeamMigrationStats(
            total_count=len(opsgenie_teams),
            success_count=success_count,
            failure_count=failure_count,
            errors=errors
        )
    
    def export_terraform_config(self):
        """
        Export all resources as Terraform configuration files.
        
        Returns:
            Dict with export status and information
        """
        logger.info(f"Exporting Terraform configurations to {self.output_dir}")
        return self.config_manager.export_terraform_config()
