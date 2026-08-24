# Apex Console — every task runs through here.
.DEFAULT_GOAL := help
SHELL := /bin/bash
COMPOSE := docker compose

# The canonical store is infra/'s. Override CH if infra/.env shifts the host port
# (the shared dev host moves it to 28123 — see infra/docker-compose.yml).
CH ?= http://127.0.0.1:8123
CH_CONTAINER ?= apex-infra-clickhouse
CH_ADMIN_USER ?= apex
CH_ADMIN_PASSWORD ?= apex_local_dev

.PHONY: help install dev up up-fixtures down logs sh build preview prod typecheck clean reset ch-ping ch-tables ch-user store

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[38;5;208m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies on the host (no Docker)
	npm install

dev: ## Run Vite on the host against 127.0.0.1:8123
	npm run dev

store: ## Start the canonical ClickHouse (infra lane) and seed it
	cd ../infra && $(COMPOSE) up -d clickhouse otel-collector && ./scripts/seed.sh

up: ## Start the console against infra's store (http://localhost:5173) — run `make store` first
	$(COMPOSE) up --build

up-fixtures: ## Start the console alone, served from the recorded run
	VITE_DATA_SOURCE=fixtures $(COMPOSE) up --build console

down: ## Stop everything
	$(COMPOSE) down

logs: ## Tail the console logs
	$(COMPOSE) logs -f console

sh: ## Shell into the console container
	$(COMPOSE) exec console sh

build: ## Type-check and build the production bundle
	npm run build

preview: ## Serve the production bundle locally
	npm run preview

prod: ## Build and run the nginx production image
	$(COMPOSE) -f docker-compose.yml run --rm --build -p 8080:80 \
		--entrypoint "" console sh -c "npm run build" \
		&& docker build --target prod -t apex-console:prod . \
		&& docker run --rm -p 8080:80 apex-console:prod

typecheck: ## tsc --noEmit
	npm run typecheck

ch-ping: ## Check the ClickHouse HTTP interface
	@curl -sf "$(CH)/ping" && echo " clickhouse ok"

ch-tables: ## List the contract tables, as the console's read-only user sees them
	@curl -sf "$(CH)/?user=apex_ro" --data "SHOW TABLES FROM apex"

ch-user: ## Create apex_ro on infra's store (the console ships this credential to the browser)
	@# Via clickhouse-client, not the HTTP interface: HTTP rejects multi-statement
	@# bodies. Same mechanism infra/scripts/apply_ddl.sh uses.
	@docker exec -i $(CH_CONTAINER) clickhouse-client \
		--user $(CH_ADMIN_USER) --password $(CH_ADMIN_PASSWORD) --multiquery \
		< contract/01-readonly-user.sql && echo "apex_ro ready"

clean: ## Remove build output and node_modules
	rm -rf dist node_modules

reset: ## Stop the console. The store has its own lifecycle: see infra/
	$(COMPOSE) down
