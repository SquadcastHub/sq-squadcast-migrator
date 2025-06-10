# Squadcast Migrator Docker CLI Guide

This guide explains how to use the Squadcast Migrator Docker CLI.

## Building the Docker Image

```bash
# Build the Docker image
docker build -t squadcast-migrator:latest .

# Or use the Makefile
make build
```

## Running the Docker CLI

### Basic Usage

```bash
docker run -it --rm \
  -v "/path/to/tf/state_dir:/terraform_state" \
  squadcast-migrator:latest \
  --state_dir /terraform_state --dry --squadcast-region=eu --squadcast-refresh-token=YOUR_TOKEN
```

### Using the Shell Script

```bash
./squadcast-cli.sh \
  --state_dir /path/to/tf/state_dir \
  --squadcast-region=eu \
  --squadcast-refresh-token=YOUR_TOKEN
```

### Using the Makefile

```bash
make run STATE_DIR=/path/to/tf/state_dir PARAMS="--squadcast-region=eu --squadcast-refresh-token=YOUR_TOKEN"
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--state_dir` | Path to Terraform state directory | `/terraform_state` |
| `--squadcast-region` | Squadcast region (us or eu) | `us` |
| `--squadcast-refresh-token` | Squadcast refresh token | Required |
| `--source` | Source system to migrate from | `opsgenie` |

## Example Workflow

1. Build the Docker image:
   ```bash
   make build
   ```

2. Create a directory for Terraform state:
   ```bash
   mkdir -p ~/squadcast_terraform
   ```

3. Run the migration:
   ```bash
   ./squadcast-cli.sh \
     --state_dir ~/squadcast_terraform \
     --dry \
     --squadcast-region=eu \
     --squadcast-refresh-token=YOUR_TOKEN
   ```

4. Review the generated Terraform files in the state directory.

5. When ready, run without the `--dry` flag to perform the actual migration:
   ```bash
   ./squadcast-cli.sh \
     --state_dir ~/squadcast_terraform \
     --squadcast-region=eu \
     --squadcast-refresh-token=YOUR_TOKEN
   ```

6. Apply the Terraform configuration:
   ```bash
   cd ~/squadcast_terraform
   terraform init
   terraform plan
   terraform apply
   ```
