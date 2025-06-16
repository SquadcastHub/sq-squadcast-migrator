# Makefile for Squadcast Migrator

.PHONY: build generate plan apply

# Default variables
ENV_FILE ?= .env

build:
	@echo "Building Docker images"
	docker-compose --env-file $(ENV_FILE) build

generate:
	@echo "Generating Terraform configuration"
	docker-compose --env-file $(ENV_FILE) run --rm squadcastify

plan: generate
	@echo "Running Terraform init (if required) and plan"
	$(eval TERRAFORM_STATE_PATH := $(shell grep TERRAFORM_STATE_PATH $(ENV_FILE) | cut -d '=' -f2))
	@if [ ! -d "$(TERRAFORM_STATE_PATH)/.terraform" ]; then \
		docker-compose --env-file $(ENV_FILE) run --rm terraform init; \
	fi
	docker-compose --env-file $(ENV_FILE) run --rm terraform plan

apply: generate
	@echo "Running Terraform init (if required) and apply"
	$(eval TERRAFORM_STATE_PATH := $(shell grep TERRAFORM_STATE_PATH $(ENV_FILE) | cut -d '=' -f2))
	@if [ ! -d "$(TERRAFORM_STATE_PATH)/.terraform" ]; then \
		docker-compose --env-file $(ENV_FILE) run --rm terraform init; \
	fi
	docker-compose --env-file $(ENV_FILE) run --rm terraform apply
