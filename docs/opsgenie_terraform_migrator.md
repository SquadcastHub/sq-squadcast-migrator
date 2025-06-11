# OpsGenie to Squadcast Terraform Migrator

This documentation covers how to use the OpsGenie to Terraform migrator to generate Terraform configurations for Squadcast resources based on your OpsGenie setup.

## Overview

The OpsGenie Terraform Migrator extracts users and teams from your OpsGenie account and generates Terraform configuration files that can be used to create equivalent resources in Squadcast. This approach allows you to:

1. Version control your Squadcast infrastructure
2. Review changes before applying them
3. Maintain your infrastructure as code

## Prerequisites

- Python 3.13+
- OpsGenie API key with read permissions
- Squadcast API token

## Environment Setup

Create a `.env` file with your credentials:

```
# OpsGenie API Configuration
OPSGENIE_API_KEY=your_opsgenie_api_key_here
OPSGENIE_API_URL=https://api.opsgenie.com/v2

# General settings
DRY_RUN=True  # Set to False when ready to generate files
LOG_LEVEL=INFO
```

## Running the Migrator

Execute the migration script:

```bash
python migrate_opsgenie_to_terraform.py
```

The script will:
1. Connect to OpsGenie API
2. Fetch and transform users and teams
3. Generate Terraform configuration files in the `terraform_output` directory

## Terraform Configuration Structure

The generated Terraform configurations are organized as follows:

```
terraform_output/
├── main.tf            # Main tf file with all resources
├── provider.tf        # Squadcast provider configuration
├── variables.tf       # Variable declarations
├── outputs.tf         # Output
├── terraform.tfvars.example  # Example variables file
```

## Applying Terraform Configurations

1. Rename `terraform.tfvars.example` to `terraform.tfvars` and set your Squadcast API token
2. Navigate to the terraform_output directory
3. Initialize Terraform: `terraform init`
4. Plan the changes: `terraform plan`
5. Apply the changes: `terraform apply`

## Customization

You can modify `src/migrators/opsgenie_migrator.py` if you need to customize how resources are transformed from OpsGenie to Squadcast.
