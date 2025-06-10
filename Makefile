# Makefile for Squadcast Migrator

.PHONY: build run help

# Default variables
STATE_DIR ?= ./terraform_output

help:
	@echo "Squadcast Migrator"
	@echo ""
	@echo "Usage:"
	@echo "  make build                  Build the Docker image"
	@echo "  make run STATE_DIR=/path    Run the Docker container with parameters"
	@echo ""
	@echo "Parameters for run:"
	@echo "  STATE_DIR       Path to Terraform state directory (default: ./terraform_output)"
	@echo "  PARAMS          Additional parameters to pass to the container"
	@echo ""
	@echo "Example:"
	@echo "  make run STATE_DIR=/path/to/tf PARAMS='--dry --squadcast-region=eu --squadcast-refresh-token=ABC123'"
	@echo ""

build:
	@echo "Building Docker image: squadcast-migrator"
	docker build -t squadcast-migrator:latest .

run:
	@echo "Running Squadcast Migrator with parameters: $(PARAMS)"
	@mkdir -p $(STATE_DIR)
	docker run -it --rm \
	  -v "$(STATE_DIR):/terraform_state" \
	  squadcast-migrator:latest \
	  --state_dir /terraform_state $(PARAMS)
