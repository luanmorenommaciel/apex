# Apex Console — every task runs through here.
.DEFAULT_GOAL := help
SHELL := /bin/bash
COMPOSE := docker compose

# What the PRODUCTION image is started with. Nothing here is baked into the
# bundle — the image entrypoint renders /config.js from these at container
# start, so one image serves every deployment (see README, "Configure a
# deployment"). The console reads through the Apex API alone (D-api-only,
# 2026-10-19): the browser carries an API token and no database user.
#
# APEX_API_UPSTREAM is where nginx forwards /v1. Inside the container
# 127.0.0.1 is the container itself, so an API published on the host is
# reached through the gateway alias instead. APEX_API_URL is deliberately not
# passed — it would make the browser call the API cross-origin, which the API
# refuses.
DATA_SOURCE ?= http
APEX_API_UPSTREAM ?= http://host.docker.internal:8099
APEX_API_TOKEN ?=

.PHONY: help install dev up up-fixtures down logs sh build preview prod typecheck clean reset

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[38;5;208m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies on the host (no Docker)
	npm install

dev: ## Run Vite on the host, proxying /v1 to the API on 127.0.0.1:8099
	npm run dev

up: ## Start the console through the Apex API (http://localhost:5173) — start serve's apex-api on 8099 first, pass VITE_APEX_API_TOKEN
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

prod: ## Build and run the nginx production image on :8080 through the API (APEX_API_UPSTREAM/APEX_API_TOKEN); DATA_SOURCE=fixtures for the recording
	@# The build stage already runs `npm run build`.
	docker build --target prod -t apex-console:prod .
	@# host.docker.internal is provided by Docker Desktop; --add-host makes the
	@# gateway explicit on Linux, exactly as docker-compose.yml does for dev.
	docker run --rm -p 8080:80 \
		--add-host host.docker.internal:host-gateway \
		-e DATA_SOURCE="$(DATA_SOURCE)" \
		-e APEX_API_UPSTREAM="$(APEX_API_UPSTREAM)" \
		-e APEX_API_TOKEN="$(APEX_API_TOKEN)" \
		apex-console:prod

typecheck: ## tsc --noEmit
	npm run typecheck

clean: ## Remove build output and node_modules
	rm -rf dist node_modules

reset: ## Stop the console. The store has its own lifecycle: see infra/
	$(COMPOSE) down
