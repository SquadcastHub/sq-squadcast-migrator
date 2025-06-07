import os
from pathlib import Path
from typing import Dict, List, Union

from .models.base import TerraformResource


class TerraformConfigManager:
    """Manages Terraform configuration file generation from Pydantic models"""

    def __init__(self, output_dir: Union[str, Path], provider_config: Dict[str, str]):
        """Initialize the Terraform configuration manager.

        Args:
            output_dir: Directory where Terraform files will be generated
            provider_config: Configuration for the Squadcast provider
        """
        self.output_dir = Path(output_dir)
        self.provider_config = provider_config
        self.resources: Dict[str, List[TerraformResource]] = {}

    def add_resource(self, resource: TerraformResource):
        """Add a resource to be managed.
        
        Resources are grouped by type for organized file generation.
        """
        resource_type = resource.terraform_resource_type
        if resource_type not in self.resources:
            self.resources[resource_type] = []
        self.resources[resource_type].append(resource)

    def generate_provider_file(self):
        """Generate the provider configuration file"""
        provider_path = self.output_dir / "provider.tf"
        
        # Convert provider config to HCL
        config_lines = []
        for key, value in self.provider_config.items():
            config_lines.append(f'  {key} = "{value}"')
        
        content = [
            'terraform {',
            '  required_providers {',
            '    squadcast = {',
            '      source = "SquadcastHub/squadcast"',
            '    }',
            '  }',
            '}',
            '',
            'provider "squadcast" {',
            *config_lines,
            '}'
        ]
        
        provider_path.write_text('\n'.join(content))

    def generate_root_main_tf(self):
        """Generate a root main.tf file that includes all modules"""
        main_path = self.output_dir / "main.tf"
        
        # Generate module blocks for each resource type
        module_blocks = []
        for resource_type in self.resources.keys():
            # Get module name (e.g., "user" from "squadcast_user")
            module_name = resource_type.split('_')[1]
            
            module_block = [
                f'module "{module_name}" {{',
                f'  source = "./{module_name}"',
                '}'
            ]
            module_blocks.append('\n'.join(module_block))
        
        if module_blocks:
            main_content = '\n\n'.join(module_blocks)
            main_path.write_text(main_content)

    def generate_resource_files(self):
        """Generate Terraform configuration files for all resources"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generate_provider_file()
        self.generate_root_main_tf()
        
        # Group resources by type into separate files
        for resource_type, resources in self.resources.items():
            # Create subdirectory for the resource type
            resource_dir = self.output_dir / resource_type.split('_')[1]
            resource_dir.mkdir(exist_ok=True)
            
            # Generate main.tf with all resources of this type
            main_tf = resource_dir / "main.tf"
            content = []
            
            for resource in resources:
                content.append(resource.to_hcl())
                content.append("")  # Empty line between resources
            
            main_tf.write_text('\n'.join(content))

            # Generate empty variables.tf for potential future use
            variables_tf = resource_dir / "variables.tf"
            if not variables_tf.exists():
                variables_tf.touch()

            # Generate terraform.tf for provider configuration
            terraform_tf = resource_dir / "terraform.tf"
            terraform_content = [
                'terraform {',
                '  required_providers {',
                '    squadcast = {',
                '      source = "SquadcastHub/squadcast"',
                '    }',
                '  }',
                '}',
            ]
            terraform_tf.write_text('\n'.join(terraform_content))

    def export_terraform_config(self):
        """Export all resources as Terraform configuration files"""
        try:
            self.generate_resource_files()
            return {
                "status": "success",
                "output_dir": str(self.output_dir),
                "resource_counts": {
                    rtype: len(resources) 
                    for rtype, resources in self.resources.items()
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }