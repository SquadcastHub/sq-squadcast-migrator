# Alerting System to Squadcast Migrator

A tool to migrate data from alerting systems like OpsGenie, PagerDuty to Squadcast.

## Features

- Migrate data from various alerting systems to Squadcast (users, teams, escalation policies, schedules etc.)
- Generic `AlertingClient` interface for easy integration with new alerting systems
- Dry-run mode to preview migration without making any changes
- Command-line interface with clear options
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

STATE_DIR=/terraform_state

# PagerDuty API Configuration
PAGERDUTY_API_TOKEN=your_pagerduty_token_here
PAGERDUTY_API_URL=https://api.pagerduty.com

# OpsGenie API Configuration
OPSGENIE_API_KEY=your_opsgenie_api_key_here
OPSGENIE_API_URL=https://api.opsgenie.com/v2

# Squadcast API Configuration
SQUADCAST_REFRESH_TOKEN=your_squadcast_refresh_token_here
SQUADCAST_REGION=us # or 'eu' depending on your region

# Migration Settings
LOG_LEVEL=INFO
```

## Usage

### Local Usage

#### Migrating Everything

To migrate all supported entities:

```bash
uv run -m squadcastify.main
```

### Docker CLI Usage

You can use the Docker container as a CLI tool in the following ways:

#### Using the Makefile:

```bash
make build
make run
```

#### Direct Docker run:
```bash
docker run -it \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/terraform_output:/app/terraform_output \
  squadcast-migrator:latest
```

## Development

### Project Structure

```
squadcast-migrator/
├── squadcastify
│   ├── __init__.py
│   ├── config.py
│   ├── log_utils
│   │   ├── __init__.py
│   │   └── formatter.py
│   ├── main.py
│   ├── source
│   │   ├── __init__.py
│   │   ├── alerting_client.py
│   │   ├── opsgenie
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── migrator.py
│   │   ├── pagerduty
│   │   │   └── __init__.py
│   │   ├── schema
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── migration.py
│   │   │   ├── squad.py
│   │   │   ├── team.py
│   │   │   └── user.py
│   │   └── transformer.py
├── DOCKER_CLI_GUIDE.md
├── Dockerfile
├── tests
└── uv.lock
```

### Managing Dependencies

This project uses UV for dependency management. Here are some common commands:

- Add a new dependency: `uv pip install package_name`
- Install all dependencies: `uv pip install .`
- Update a dependency: `uv pip install --upgrade package_name`

Dependencies are defined in `pyproject.toml`.
