#!/usr/bin/env python3
import os
import logging
import sys
from pathlib import Path
from datetime import datetime

from config.config import settings
from src.migrators.opsgenie_migrator import OpsGenieTerraformMigrator
from src.logging.formatter import CustomFormatter

os.makedirs("logs", exist_ok=True)

log_filename = (
    f"logs/terraform_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
custom_formatter = CustomFormatter(log_format)

root_logger = logging.getLogger()
root_logger.setLevel(settings.log_level)
root_logger.handlers.clear()

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(custom_formatter)
root_logger.addHandler(console_handler)

file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(custom_formatter)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)
logger.info(f"💾 Logs will be stored in: {log_filename}")


def main():
    """Main entry point for the script."""

    output_dir = Path("terraform_output")

    # Configure provider settings
    provider_config = {
        "region": "${var.squadcast_region}",  # Use a variable for region (us or eu)
        "refresh_token": "${var.squadcast_refresh_token}",  # Use a variable for sensitive data
    }

    try:
        logger.info(f"Initializing {settings.system} Terraform migrator")
        migrator = OpsGenieTerraformMigrator(
            output_dir=output_dir, provider_config=provider_config
        )

        # Migrate users
        logger.info(f"🚀 Starting user migration from {settings.system} to Terraform")
        user_result = migrator.migrate_users()
        logger.info(
            f"📊 User migration summary → "
            f"Total: {user_result.total_count}, "
            f"✅ Success: {user_result.success_count}, "
            f"❌ Failed: {user_result.failure_count}"
        )

        # Migrate teams
        logger.info(f"🚀 Starting team migration from {settings.system} to Terraform")
        team_result = migrator.migrate_teams()
        logger.info(
            f"📊 Team migration summary → "
            f"Total: {team_result.total_count}, "
            f"✅ Success: {team_result.success_count}, "
            f"❌ Failed: {team_result.failure_count}"
        )

        # Export Terraform configurations
        logger.info("📄 Exporting Terraform configurations")
        export_result = migrator.export_terraform_config()

        if export_result["status"] == "success":
            logger.info(
                f"✅ Successfully generated Terraform configuration in: {export_result['output_dir']}"
            )
            logger.info(f"📊 Resource counts: {export_result['resource_counts']}")

            print("\n" + "=" * 80)
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"Terraform configuration generated in: {output_dir}")
            print("\nTo apply this configuration:")
            print("1. Rename terraform.tfvars.example to terraform.tfvars")
            print("2. Update terraform.tfvars with your Squadcast API token")
            print("3. Run:")
            print(f"   cd {output_dir}")
            print("   terraform init")
            print("   terraform plan  # Review the planned changes")
            print("   terraform apply # Apply the changes")
            print("=" * 80 + "\n")
        else:
            logger.error(
                f"❌ Failed to export Terraform configuration: {export_result['message']}"
            )

    except Exception as e:
        logger.exception(f"❌ Migration failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
