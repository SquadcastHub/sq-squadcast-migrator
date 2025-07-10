# Alerting System to Squadcast Migrator

A tool to migrate data from alerting systems like OpsGenie, PagerDuty to Squadcast.

## Features

- Migrate data from various alerting systems to Squadcast (users, teams, escalation policies, schedules, squads etc.)
- Terraform resource generation for infrastructure-as-code approach
- Enhanced HCL (HashiCorp Configuration Language) generation with support for complex nested structures
- Generic testing framework for Terraform resource models
- Docker containerized CLI for easy deployment and use

## Installation

### Local Installation

1. Clone this repository:

```bash
git clone https://github.com/SquadcastHub/squadcast-migrator.git
cd squadcast-migrator
```

2. Install UV (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install .
```

### Docker CLI Installation

1. Build the Docker image:

```bash
make build
```

This will create a Docker image named `squadcast-migrator:latest` that you can use as a CLI tool.

## Configuration

You can configure the migrator in two ways:

### Environment Variables

Create a `.env` file in the root directory with the following content:

```
# Source Configuration. Can be either 'opsgenie' or 'pagerduty'
SOURCE=opsgenie

# Terraform state directory (optional)
STATE_DIR=/terraform_state

# PagerDuty API Configuration
PAGERDUTY_API_TOKEN=your_pagerduty_token_here
PAGERDUTY_API_URL=https://api.pagerduty.com

# OpsGenie API Configuration
OPSGENIE_API_KEY=your_opsgenie_api_key_here
OPSGENIE_API_URL=https://api.opsgenie.com/v2

OPSGENIE_TARGET_TEAM_NAME=ITSM # Optional - pass only if you want to migrated data from a particular team

# Squadcast API Configuration
SQUADCAST_REFRESH_TOKEN=your_squadcast_refresh_token_here
SQUADCAST_REGION=us # or 'eu' depending on your region

# Migration Settings
LOG_LEVEL=INFO

# Output Settings
TERRAFORM_OUTPUT_DIR=./terraform_output  # Directory for generated .tf files
```

## Usage

### Local Usage

#### Migrating Everything

To migrate all supported entities:

```bash
uv run -m squadcastify.main
```

#### Team-Specific Migration

For OpsGenie migrations, you can filter the migration to a specific team. This is useful when you want to migrate one team at a time or test the migration process on a smaller subset of data.

In order to do this, you need to add `OPSGENIE_TARGET_TEAM_NAME` to the .env file.

```
OPSGENIE_TARGET_TEAM_NAME=ITSM
```

When using team filtering, the migrator will only process:

- Users who are members of the specified team
- The specified team itself
- Escalation policies owned by the specified team
- Schedules owned by the specified team

### Docker CLI Usage

You can use the Docker container as a CLI tool in the following ways:

#### Using the Makefile:

```bash
make build
make generate
make plan
```

#### Direct Docker run:

```bash
docker run -it \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/terraform_output:/app/terraform_output \
  -v $(pwd)/logs:/app/logs \
  squadcast-migrator:latest
```

#### Using Generated Terraform Files

After migration, you'll find `.tf` files in the `terraform_output` directory. To use them with Terraform:

```bash
# Navigate to the output directory
cd terraform_output

# Initialize Terraform
terraform init

# Plan the deployment (dry-run)
terraform plan

# Apply the configuration
terraform apply
```

### Output Structure

The migrator generates the following outputs:

1. **Terraform Files** (`.tf`): Located in `terraform_output/` directory

   - `main.tf`: Main resource definitions
   - `variables.tf`: Input variables (if any)
   - `outputs.tf`: Output values (if any)

2. **Migration Logs**: Located in `logs/` directory with timestamp-based filenames

3. **State Information**: Intermediate migration state (if using state directory)

## Terraform Integration

This migrator generates Terraform configuration files for infrastructure-as-code management of your Squadcast resources. The generated `.tf` files can be used with Terraform to manage your Squadcast configuration programmatically.

### Terraform Resource Models

The project includes comprehensive Terraform resource models for:

- **Users** (`squadcast_user`): User accounts and profiles
- **Teams** (`squadcast_team`): Team configurations and settings
- **Team Members** (`squadcast_team_member`): Team membership associations
- **Squads** (`squadcast_squad`): Squad definitions and member assignments
- **Services** (`squadcast_service`): Service configurations
- **Escalation Policies** (`squadcast_escalation_policy`): Complex escalation rules with support for:
  - Multiple escalation rules with delays
  - Target assignments (users, squads, schedules)
  - Notification channels (Email, SMS, Push, Phone)
  - Repeat configurations
  - Round-robin scheduling
- **Schedules** (`squadcast_schedule_v2`): On-call scheduling with rotations

### Testing Framework

The project includes a comprehensive testing framework for Terraform models:

- **Generic Test Base Class** (`TerraformResourceTestCase`): Reduces code duplication across tests
- **HCL Validation Methods**:
  - `assert_hcl_equals()`: Compare generated HCL with expected output
  - `assert_hcl_contains()`: Check for specific elements in generated HCL
  - `validate_complex_hcl()`: Validate complex nested structures
- **Resource Property Testing**:
  - `assert_terraform_name()`: Test auto-generation of Terraform names
  - `assert_terraform_resource_type()`: Validate resource type definitions

## Development

### Project Structure

```
squadcast-migrator/
├── squadcastify/
│   ├── __init__.py
│   ├── config.py                    # Configuration management
│   ├── main.py                      # CLI entry point
│   ├── log_utils/                   # Logging utilities
│   │   ├── __init__.py
│   │   └── formatter.py
│   ├── source/                      # Source system integrations
│   │   ├── __init__.py
│   │   ├── alerting_client.py       # Generic alerting client interface
│   │   ├── opsgenie/                # OpsGenie integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── migrator.py
│   │   ├── pagerduty/               # PagerDuty integration
│   │   │   └── __init__.py
│   │   ├── schema/                  # Data schemas
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── migration.py
│   │   │   ├── squad.py
│   │   │   ├── team.py
│   │   │   └── user.py
│   │   └── transformer.py           # Data transformation logic
│   └── terraform/                   # Terraform resource generation
│       ├── exporter.py              # Terraform export functionality
│       ├── transformer.py           # Terraform data transformation
│       └── models/                  # Terraform resource models
│           ├── __init__.py
│           ├── base.py              # Base TerraformResource class
│           ├── common.py            # Common model components
│           ├── escalation_policy.py # Escalation policy resources
│           ├── schedule.py          # Schedule resources
│           ├── service.py           # Service resources
│           ├── squad.py             # Squad resources
│           ├── team.py              # Team resources
│           ├── team_member.py       # Team member resources
│           ├── user.py              # User resources
│           └── utils.py             # Utility functions
├── tests/                           # Test suite
│   └── terraform/
│       └── models/
│           ├── __init__.py
│           ├── test_escalation_policy.py
│           ├── test_squad.py
├── examples/                        # Usage examples
│   └── basic_usage.py
├── logs/                           # Migration logs
├── terraform_output/               # Generated Terraform files
├── Dockerfile                      # Docker configuration
├── docker-compose.yml             # Docker Compose setup
├── Makefile                        # Build and run commands
├── pyproject.toml                  # Project dependencies
└── README.md
```

### Managing Dependencies

This project uses UV for dependency management. Here are some common commands:

- Add a new dependency: `uv pip install package_name`
- Install all dependencies: `uv pip install .`
- Update a dependency: `uv pip install --upgrade package_name`

Dependencies are defined in `pyproject.toml`.

### Running Tests

To run the test suite:

```bash
# Run all tests
uv run -m pytest tests/

# Run specific test files
uv run -m pytest tests/terraform/models/test_escalation_policy.py

# Run tests with verbose output
uv run -m pytest tests/ -v

# Run tests with coverage
uv run -m pytest tests/ --cov=squadcastify
```

### Adding New Terraform Resources

To add a new Terraform resource model:

1. Create a new model class inheriting from `TerraformResource` in `squadcastify/terraform/models/`
2. Implement the required `terraform_resource_type` property
3. Define the resource fields using Pydantic models

Example:

```python
from squadcastify.terraform.models.base import TerraformResource

class SquadcastNewResource(TerraformResource):
    name: str
    team_id: str

    @property
    def terraform_resource_type(self) -> str:
        return "squadcast_new_resource"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `uv pip install .`

2. **API Authentication Failures**:

   - Verify your API tokens/keys are correct
   - Check that the API URLs match your region/instance
   - Ensure tokens have the necessary permissions

3. **Terraform Generation Issues**:

   - Check the logs in the `logs/` directory for detailed error messages
   - Verify the `terraform_output` directory has write permissions
   - Ensure complex nested data structures are properly formatted

4. **Test Failures**:
   - Run tests in verbose mode: `uv run -m pytest tests/ -v`
   - Check that test data matches expected HCL format
   - Verify Pydantic model definitions are correct

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file for more detailed output.

### Getting Help

- Check the logs in the `logs/` directory for detailed error information
- Review the generated Terraform files for any syntax issues
- Validate your source system API connectivity before migration

## Contributing

When contributing to this project:

1. **Adding New Features**:

   - Follow the existing code structure and patterns
   - Add comprehensive tests
   - Update documentation and examples

2. **Testing**:

   - Run the full test suite before submitting PRs
   - Add tests for any new Terraform resource models
   - Ensure HCL generation is properly tested
