#!/bin/bash
# run-with-volume.sh - Run Squadcast Migrator with local storage for Terraform state

# Define variables
LOCAL_STATE_DIR="./terraform_output"  # Directory on your local machine
CONTAINER_STATE_DIR="/terraform_state" # Directory inside the container

# Create the local state directory if it doesn't exist
mkdir -p "$LOCAL_STATE_DIR"

echo "Running Squadcast Migrator with Docker..."
echo "Local state directory: $LOCAL_STATE_DIR"
echo "Container state directory: $CONTAINER_STATE_DIR"

# Run the Docker container with volume mounting and pass environment variables
# This maps your local directory to the container directory
docker run -it --rm \
  -v "$(pwd)/$LOCAL_STATE_DIR:$CONTAINER_STATE_DIR" \
  -e "STATE_DIR=$CONTAINER_STATE_DIR" \
  -e "OPSGENIE_API_KEY=${OPSGENIE_API_KEY}" \
  -e "OPSGENIE_API_URL=${OPSGENIE_API_URL:-https://api.opsgenie.com/v2}" \
  -e "SQUADCAST_REFRESH_TOKEN=${SQUADCAST_REFRESH_TOKEN}" \
  -e "SQUADCAST_REGION=${SQUADCAST_REGION:-us}" \
  -e "SOURCE=${SOURCE:-opsgenie}" \
  -e "LOG_LEVEL=${LOG_LEVEL:-INFO}" \
  squadcast-migrator:latest

echo "Migration complete! Terraform configuration has been generated in $LOCAL_STATE_DIR"
echo "To apply the Terraform configuration:"
echo "1. cd $LOCAL_STATE_DIR"
echo "2. terraform init"
echo "3. terraform plan"
echo "4. terraform apply"
