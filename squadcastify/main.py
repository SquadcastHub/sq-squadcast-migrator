#!/usr/bin/env python3
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from .config import Settings
from .source.opsgenie.client import OpsgenieAPIClient
from .source.opsgenie.migrator import OpsGenieTransformer
from .source.transformer import Transformer
from .log_utils.formatter import CustomFormatter
from .terraform.exporter import TerraformExporter


def main():
    settings = Settings()
    setup_logger(settings.log_level)

    logger = logging.getLogger(__name__)

    # Use the state_dir parameter as the output directory
    exporter: TerraformExporter = TerraformExporter(
        output_dir=Path(settings.state_dir),  # Use the provided state_dir
        provider_config={
            "region": "${var.squadcast_region}",  # Use a variable for region (us or eu)
            "refresh_token": "${var.squadcast_refresh_token}",  # Use a variable for sensitive data
        },
    )

    try:
        logger.info(f"Initializing {settings.source} Terraform migrator")

        transformer: Transformer = OpsGenieTransformer(
            client=OpsgenieAPIClient(
                api_key=settings.opsgenie_api_key,
                api_url=settings.opsgenie_api_url,
            ),
            exporter=exporter,
        )
        transformer.transform()

        # Export Terraform configurations
        logger.info("📄 Exporting Terraform configurations")
        export_result = exporter.export()

        if export_result["status"] == "success":
            logger.info(
                f"✅ Successfully generated Terraform configuration in: {export_result['output_dir']}"
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


def setup_logger(log_level: str = "INFO"):
    # Create logs directory in the current directory
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_filename = os.path.join(
        logs_dir, f"terraform_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    custom_formatter = CustomFormatter(log_format)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(custom_formatter)
    root_logger.addHandler(console_handler)
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(custom_formatter)
    root_logger.addHandler(file_handler)
    root_logger.info(f"💾 Logs will be stored in: {log_filename}")


if __name__ == "__main__":
    sys.exit(main())
