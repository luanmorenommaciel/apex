# Apex infra — Makefile.  `make help` lists targets.
SHELL   := /usr/bin/env bash

.DEFAULT_GOAL := help
.PHONY: help apply-ddl verify-ddl

help: ## List available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n",$$1,$$2}'

apply-ddl: ## Idempotently apply every sql/*.sql (filename order) to the RUNNING ClickHouse
	@./scripts/apply_ddl.sh

verify-ddl: ## DESCRIBE each contract table and diff it against its DDL source of truth
	@python3 scripts/verify_ddl.py
