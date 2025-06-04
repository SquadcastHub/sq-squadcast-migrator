#!/bin/bash
set -e

# If .env file is provided as a volume, source it
if [ -f ./.env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' ./.env | xargs)
fi

# Execute the command passed to docker run
exec "$@"
