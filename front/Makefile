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

# What the PRODUCTION image is started with. Nothing here is baked into the
# bundle — the image entrypoint renders /config.js from these at container
# start, so one image serves every deployment (see README, "Configure a
# deployment"). CLICKHOUSE_UPSTREAM is an endpoint only, never a credential.
#
# It is NOT $(CH): inside the container 127.0.0.1 is the container itself, so a
# store published on the host is reached through the gateway alias instead.
CLICKHOUSE_UPSTREAM ?= http://host.docker.internal:8123
CH_DB ?= apex
CH_USER ?= apex_ro
CH_PASSWORD ?=
DATA_SOURCE ?= clickhouse

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

prod: ## Build and run the nginx production image on :8080 (override CLICKHOUSE_UPSTREAM)
	@# The build stage already runs `npm run build`; the old compose pre-step
	@# rebuilt the same assets in the dev container and threw them away.
	@test -n "$(CLICKHOUSE_UPSTREAM)" || { \
		echo "CLICKHOUSE_UPSTREAM is empty. nginx substitutes it into proxy_pass"; \
		echo "and refuses to start without it."; exit 1; }
	docker build --target prod -t apex-console:prod .
	@# host.docker.internal is provided by Docker Desktop; --add-host makes the
	@# gateway explicit on Linux, exactly as docker-compose.yml does for dev.
	docker run --rm -p 8080:80 \
		--add-host host.docker.internal:host-gateway \
		-e CLICKHOUSE_UPSTREAM="$(CLICKHOUSE_UPSTREAM)" \
		-e CLICKHOUSE_DB="$(CH_DB)" \
		-e CLICKHOUSE_USER="$(CH_USER)" \
		-e CLICKHOUSE_PASSWORD="$(CH_PASSWORD)" \
		-e DATA_SOURCE="$(DATA_SOURCE)" \
		apex-console:prod

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
