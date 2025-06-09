from pathlib import Path
from typing import Dict, List, Union

from config.config import settings
from .models.base import TerraformResource


class TerraformExporter:
    """Manages Terraform configuration file generation from Pydantic models"""

    def __init__(self, output_dir: Union[str, Path], provider_config: Dict[str, str]):
        """Initialize the Terraform configuration manager.

        Args:
            output_dir: Directory where Terraform files will be generated
            provider_config: Configuration for the Squadcast provider
        """
        self.output_dir = Path(output_dir)
        self.provider_config = provider_config
        self.__resources: Dict[str, List[TerraformResource]] = {}

    def add_resource(self, resource: TerraformResource):
        """Add a resource to be managed.

        Resources are grouped by type for organized file generation.
        """
        resource_type = resource.terraform_resource_type
        if resource_type not in self.__resources:
            self.__resources[resource_type] = []
        self.__resources[resource_type].append(resource)

    def _generate_provider_file(self):
        """Generate the provider configuration file (internal method)"""
        provider_path = self.output_dir / "provider.tf"

        # Convert provider config to HCL
        config_lines = []
        for key, value in self.provider_config.items():
            config_lines.append(f'  {key} = "{value}"')

        content = [
            "terraform {",
            "  required_providers {",
            "    squadcast = {",
            '      source = "SquadcastHub/squadcast"',
            "    }",
            "  }",
            "}",
            "",
            'provider "squadcast" {',
            *config_lines,
            "}",
        ]

        provider_path.write_text("\n".join(content))

    def _generate_root_main_tf(self):
        """Generate a root main.tf file that contains all resource definitions (internal method)"""
        main_path = self.output_dir / "main.tf"

        # Directly write all resources to the main.tf file
        content = []

        # Add a header comment
        content.append("# Main Terraform configuration file containing all resources")
        content.append("")

        # Add all resources grouped by resource type
        for resource_type, resources in self.__resources.items():
            # Add a comment header for the resource type
            content.append(
                f"# {resource_type.replace('squadcast_', '').upper()} RESOURCES"
            )
            content.append("")

            # Add all resources of this type
            for resource in resources:
                content.append(resource.to_hcl())
                content.append("")

        # Write the file if we have any resources
        if len(content) > 2:  # More than just the header
            main_path.write_text("\n".join(content))

    def _generate_root_variables_tf(self):
        """Generate a root variables.tf file for sensitive data (internal method)"""
        variables_path = self.output_dir / "variables.tf"

        content = [
            'variable "squadcast_refresh_token" {',
            '  description = "Squadcast API token"',
            "  type        = string",
            "  sensitive   = true",
            "}",
            "",
            'variable "squadcast_region" {',
            '  description = "Squadcast region (us or eu)"',
            "  type        = string",
            '  default     = "us"',  # Default to US region, can be changed in terraform.tfvars
            "}",
        ]

        variables_path.write_text("\n".join(content))

        tfvars_file = self.output_dir / "terraform.tfvars.example"
        tfvars_content = [
            "# Rename this file to terraform.tfvars and update with your actual token",
            'squadcast_refresh_token = "YOUR_SQUADCAST_API_TOKEN"',
            'squadcast_region = "REGION"  # e.g., "us" or "eu"',
        ]
        tfvars_file.write_text("\n".join(tfvars_content))

        if settings.squadcast_refresh_token or settings.squadcast_region:
            tfvars_file = self.output_dir / "terraform.tfvars"
            tfvars_content = [
                f'squadcast_refresh_token = "{settings.squadcast_refresh_token}"',
                f'squadcast_region = "{settings.squadcast_region}"',
            ]
            tfvars_file.write_text("\n".join(tfvars_content))

    def _generate_variables_file(self, resource_type: str, variables: Dict[str, str]):
        """Add variables to the root variables.tf file (internal method)"""
        variables_tf = self.output_dir / "variables.tf"

        # Read existing content if the file exists
        if variables_tf.exists():
            existing_content = variables_tf.read_text()
        else:
            existing_content = ""

        # Generate new variable definitions
        content = []
        for var_name, var_type in variables.items():
            # Only add if not already in the file
            if f'variable "{var_name}"' not in existing_content:
                content.append(f'variable "{var_name}" {{')
                content.append(f"  type = {var_type}")
                content.append("}")
                content.append("")

        # Append new content to existing content
        if content:
            if existing_content:
                variables_tf.write_text(
                    existing_content + "\n" + "\n".join(content).strip()
                )
            else:
                variables_tf.write_text("\n".join(content).strip())

    def _generate_resource_files(self):
        """Generate Terraform configuration files for all resources (internal method)"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._generate_provider_file()
        self._generate_root_variables_tf()
        self._generate_root_main_tf()

        # Create a single outputs.tf file for all resources
        outputs_tf = self.output_dir / "outputs.tf"
        output_content = []

        # Generate outputs for all resource types
        for resource_type, resources in self.__resources.items():
            print(f"Processing resource type: {resource_type}")

            # Create a logical output name like "user_ids", "team_ids", etc.
            logical_output_name = resource_type.replace("squadcast_", "") + "_ids"

            output_content.append(f'output "{logical_output_name}" {{')
            output_content.append("  value = {")
            for resource in resources:
                output_content.append(
                    f"    {resource.terraform_name} = {resource.terraform_resource_type}.{resource.terraform_name}.id"
                )
            output_content.append("  }")
            output_content.append("}")
            output_content.append("")  # Empty line between outputs

        if output_content:
            outputs_tf.write_text("\n".join(output_content).strip())

    def export(self):
        """Export all resources as Terraform configuration files"""
        try:
            self._generate_resource_files()
            return {
                "status": "success",
                "output_dir": str(self.output_dir),
                "resource_counts": {
                    rtype: len(resources)
                    for rtype, resources in self.__resources.items()
                },
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
