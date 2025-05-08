# OpsGenie to Squadcast Migrator

A tool to migrate data from OpsGenie to Squadcast.

## Features

- Migrate data from OpsGenie to Squadcast
- Dry-run mode to preview migration without making any changes
- Command-line interface with clear options
- Extensible architecture for adding more migration types

## Installation

1. Clone this repository:
```bash
git clone https://github.com/SquadcastHub/opsgenie-squadcast-migrator.git
cd opsgenie-squadcast-migrator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

You can configure the migrator in two ways:

### Environment Variables

Create a `.env` file in the root directory with the following content:

```
OPSGENIE_API_KEY=your_opsgenie_api_key
OPSGENIE_API_URL=https://api.opsgenie.com/v2
SQUADCAST_REFRESH_TOKEN=your_squadcast_refresh_token
SQUADCAST_API_URL=https://api.squadcast.com/v3
SQUADCAST_AUTH_URL=https://auth.squadcast.com/oauth/access-token
DRY_RUN=False
LOG_LEVEL=INFO
```

### Command Line Arguments

Alternatively, you can provide configuration via command-line arguments:

```bash
python main.py --opsgenie-api-key YOUR_KEY --squadcast-refresh-token YOUR_TOKEN migrate-users
```

## Usage

### Migrating Users

To migrate users from OpsGenie to Squadcast:

```bash
python main.py migrate-users
```

To run in dry-run mode (no actual changes will be made):

```bash
python main.py --dry-run migrate-users
```

### Migrating Everything

To migrate all supported entities:

```bash
python main.py migrate-all
```

## Development

### Project Structure

```
opsgenie-squadcast-migrator/
├── config/                 # Configuration management
│   ├── __init__.py
│   └── config.py
├── src/
│   ├── __init__.py
│   ├── opsgenie/           # OpsGenie API client
│   │   ├── __init__.py
│   │   └── client.py
│   ├── squadcast/          # Squadcast API client
│   │   ├── __init__.py
│   │   └── client.py
│   └── migrators/          # Migration logic
│       ├── __init__.py
│       └── user_migrator.py
```

### Adding New Migration Types

To add a new migration type:

1. Create a new migrator class in the `src/migrators` directory
2. Implement the necessary client methods in `src/opsgenie/client.py` and `src/squadcast/client.py`
3. Add a new command to the CLI in `main.py`
