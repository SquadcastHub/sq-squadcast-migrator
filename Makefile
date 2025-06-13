# Makefile for Squadcast Migrator

.PHONY: build run run-env help

# Default variables
STATE_DIR ?= ./terraform_output
ENV_FILE ?= .env

build:
	@echo "Building Docker image: squadcast-migrator"
	docker build -t squadcast-migrator:latest .

run:
	@echo "Running Squadcast Migrator with environment variables:"
	mkdir -p "$(STATE_DIR)"
	docker run -it --rm \
	  -v "$(shell pwd)/$(STATE_DIR):/terraform_state" \
	  -e "STATE_DIR=/terraform_state" \
	  -e "OPSGENIE_API_KEY=${OPSGENIE_API_KEY}" \
	  -e "OPSGENIE_API_URL=${OPSGENIE_API_URL}" \
	  -e "SQUADCAST_REFRESH_TOKEN=${SQUADCAST_REFRESH_TOKEN}" \
	  -e "SQUADCAST_REGION=${SQUADCAST_REGION}" \
	  -e "SOURCE=${SOURCE}" \
	  -e "LOG_LEVEL=${LOG_LEVEL}" \
	  squadcast-migrator:latest

# Run with environment variables from a .env file
run-env:
	@echo "Running Squadcast Migrator with .env file:"
	mkdir -p "$(STATE_DIR)"
	docker run -it --rm \
	  -v "$(shell pwd)/$(STATE_DIR):/terraform_state" \
	  -e "STATE_DIR=/terraform_state" \
	  --env-file "$(ENV_FILE)" \
	  squadcast-migrator:latest 
