#!/bin/bash
# example-docker-run.sh - Example of how to use the Squadcast Migrator Docker CLI

# Define variables
STATE_DIR="./terraform_output"
SQUADCAST_REGION="eu"
SQUADCAST_TOKEN="your-refresh-token-here"

# Create the state directory if it doesn't exist
mkdir -p "$STATE_DIR"

echo "Running Squadcast Migrator with Docker..."
echo "State directory: $STATE_DIR"
echo "Squadcast region: $SQUADCAST_REGION"

# Run the Docker container
docker run -it --rm \
  -v "$(pwd)/$STATE_DIR:/terraform_state" \
  squadcast-migrator:latest \
  --state_dir /terraform_state \
  --dry \
  --squadcast-region="$SQUADCAST_REGION" \
  --squadcast-refresh-token="$SQUADCAST_TOKEN"

echo "Migration complete! Terraform configuration has been generated in $STATE_DIR"
echo "To apply the Terraform configuration:"
echo "1. cd $STATE_DIR"
echo "2. terraform init"
echo "3. terraform plan"
echo "4. terraform apply"
