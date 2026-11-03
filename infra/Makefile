# Apex infra — Makefile.  `make help` lists targets.
SHELL   := /usr/bin/env bash

.DEFAULT_GOAL := help
.PHONY: help preflight up bootstrap down apply-ddl verify-ddl

help: ## List available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n",$$1,$$2}'

preflight: ## Refuse to start with a missing or default CLICKHOUSE_PASSWORD / HYPERDX_API_KEY
	@./scripts/preflight.sh

up: preflight ## preflight, bring the stack up (waits for every healthcheck), register HyperDX's first user
	@docker compose up -d --wait
	@./scripts/hyperdx_bootstrap.sh

bootstrap: ## Register HyperDX's first user through the API (idempotent; seeds connection + source)
	@./scripts/hyperdx_bootstrap.sh

down: ## Stop the stack; volumes (ClickHouse data, Mongo state) are kept
	@docker compose down

apply-ddl: ## Idempotently apply every sql/*.sql (filename order) to the RUNNING ClickHouse
	@./scripts/apply_ddl.sh

verify-ddl: ## DESCRIBE each contract table and diff it against its DDL source of truth
	@python3 scripts/verify_ddl.py
