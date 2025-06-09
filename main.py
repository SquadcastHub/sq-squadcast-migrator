#!/usr/bin/env python3
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import click

from config.config import settings
from squadcastify.source.opsgenie.migrator import OpsgenieTransformer
from squadcastify.source.transformer import Transformer
from squadcastify.logging.formatter import CustomFormatter
from squadcastify.terraform.exporter import TerraformExporter

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


@click.command()
@click.option(
    "--squadcast-refresh-token",
    help="Squadcast refresh token to use for authentication",
)
@click.option("--squadcast-region", default="us", help="Squadcast region (us or eu)")
@click.option(
    "--source",
    help="Source system to migrate from (default: opsgenie)",
    default="opsgenie",
)
def main(squadcast_refresh_token: str, squadcast_region: str, source: str):
    """Main entry point for the script."""

    # Override settings with command line arguments if provided
    if squadcast_refresh_token:
        settings.squadcast_refresh_token = squadcast_refresh_token
        logger.info("Using Squadcast refresh token from command line")

    if squadcast_region:
        settings.squadcast_region = squadcast_region
        logger.info(f"Using Squadcast region: {squadcast_region}")

    # Configure provider settings

    exporter = TerraformExporter(
        output_dir=Path("terraform_output"),
        provider_config={
            "region": "${var.squadcast_region}",  # Use a variable for region (us or eu)
            "refresh_token": "${var.squadcast_refresh_token}",  # Use a variable for sensitive data
        },
    )

    try:
        logger.info(f"Initializing {settings.system} Terraform migrator")

        transformer: Transformer = OpsgenieTransformer(exporter=exporter)
        transformer.transform()

        # Export Terraform configurations
        logger.info("📄 Exporting Terraform configurations")
        export_result = exporter.export()

        if export_result["status"] == "success":
            logger.info(
                f"✅ Successfully generated Terraform configuration in: {exporter.output_dir}"
            )
            logger.info(f"📊 Resource counts: {export_result['resource_counts']}")

            print("\n" + "=" * 80)
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"Terraform configuration generated in: {exporter.output_dir}")
            print("\nTo apply this configuration:")
            print("1. Rename terraform.tfvars.example to terraform.tfvars")
            print("2. Update terraform.tfvars with your Squadcast API token")
            print("3. Run:")
            print(f"   cd {exporter.output_dir}")
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
