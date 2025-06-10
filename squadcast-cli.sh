#!/bin/bash
# squadcast-cli.sh - A wrapper script for the Squadcast Migrator Docker container

# Display help information
function show_help {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --state_dir PATH      Path to Terraform state directory (will be mounted into container)"
  echo "  --squadcast-region    Squadcast region (us or eu)"
  echo "  --squadcast-refresh-token TOKEN  Squadcast refresh token for authentication"
  echo "  --help                Display this help message"
  echo ""
  echo "Example:"
  echo "  $0 --state_dir /path/to/tf/state_dir --dry --squadcast-region=eu --squadcast-refresh-token=ABC123"
  echo ""
}

# Parse command-line arguments
PARAMS=""
STATE_DIR=""

# Check if no arguments provided
if [ $# -eq 0 ]; then
  show_help
  exit 1
fi

while (( "$#" )); do
  case "$1" in
    --help)
      show_help
      exit 0
      ;;
    --state_dir)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        STATE_DIR=$2
        shift 2
      else
        echo "Error: Argument for --state_dir is missing" >&2
        exit 1
      fi
      ;;
    --dry|--squadcast-region=*|--squadcast-refresh-token=*|--source=*)
      PARAMS="$PARAMS $1"
      shift
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      show_help
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

# Check if state_dir is provided
if [ -z "$STATE_DIR" ]; then
  echo "Error: --state_dir parameter is required" >&2
  show_help
  exit 1
fi

# Make sure the state directory exists
mkdir -p "$STATE_DIR"

# Run Docker container
echo "Running Squadcast Migrator with parameters: $PARAMS"
docker run -it --rm \
  -v "$STATE_DIR:/terraform_state" \
  squadcast-migrator:latest \
  --state_dir /terraform_state $PARAMS
