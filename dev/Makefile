# Apex dev-env — Makefile (T13).  `make help` lists targets.
SHELL   := /usr/bin/env bash
COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help env build up down clean ps verify doctor gen-data run-pathology logs-check scale

help: ## List available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n",$$1,$$2}'

env: ## Create .env from .env.example if it doesn't exist yet
	@[ -f .env ] || { cp .env.example .env && echo "created .env from .env.example"; }

build: env ## Build the Spark image (S3A + Delta jars baked in)
	$(COMPOSE) build

up: env ## Start the cluster and wait until every service is healthy
	$(COMPOSE) up -d --wait

down: ## Stop the cluster (keep the MinIO volume)
	$(COMPOSE) down

clean: ## Stop and remove volumes — full from-scratch reset
	$(COMPOSE) down -v --remove-orphans

ps: ## Show service status
	$(COMPOSE) ps

verify: env ## PROVE fresh-clone reproducibility end-to-end (build→up→smoke→history→teardown)
	./scripts/verify.sh

doctor: verify ## Alias for `verify`

fp-test: ## T7: prove the plan_fingerprint normalizes literals (same query/diff literals -> same hash)
	$(COMPOSE) exec -T spark-master /opt/spark/bin/spark-submit \
	  --master 'local[2]' --conf spark.eventLog.enabled=false /opt/apex/tests/test_fingerprint.py

# Integration proof: dev apexdev.PlanFingerprint == jar apex.ApexPlanFingerprint for
# the same query. Mounts the jar lane's compiled Scala class (read-only) onto the
# classpath. Requires the jar built at ../jar/target/spark40-jvm-2.13/classes.
JAR_CLASSES ?= ../jar/target/spark40-jvm-2.13/classes
fp-crosscheck: ## T7 integration: dev fingerprint == jar's Scala fingerprint (cross-language)
	@test -d "$(JAR_CLASSES)" || { echo "jar classes not found at $(JAR_CLASSES) — build the jar lane first"; exit 1; }
	docker run --rm --entrypoint /opt/spark/bin/spark-submit \
	  -v "$(CURDIR)/common:/opt/apex/common:ro" \
	  -v "$(CURDIR)/tests:/opt/apex/tests:ro" \
	  -v "$(CURDIR)/conf/spark-defaults.conf:/opt/spark/conf/spark-defaults.conf:ro" \
	  -v "$(abspath $(JAR_CLASSES)):/opt/jarlane/classes:ro" \
	  -e PYTHONHASHSEED=0 -e TZ=UTC \
	  $(APEX_IMAGE) --master 'local[2]' \
	  --driver-class-path '/opt/apex/lib/apex-devfp.jar:/opt/jarlane/classes' \
	  --conf spark.eventLog.enabled=false /opt/apex/tests/test_fingerprint.py

APEX_IMAGE ?= apex-spark:local
listener-probe: up ## T6: run the listener probe and show emitted contract records
	$(COMPOSE) exec -T spark-master /opt/spark/bin/spark-submit \
	  --master spark://spark-master:7077 /opt/apex/tests/listener_probe.py
	@echo "--- out/spark_events.jsonl ---"; cat out/spark_events.jsonl

gen-data: up ## Generate deterministic ~50% hot-key Delta tables (T8)
	$(COMPOSE) exec -T spark-master /opt/spark/bin/spark-submit \
	  --master spark://spark-master:7077 /opt/apex/jobs/generate_data.py

JOB ?= skew_join
AQE ?= off
FIX ?= off
SAFE ?= off
DRIVER_MEM ?=
run-pathology: up ## Run a pathology: JOB=skew_join|spill|bad_shuffle|driver_oom [AQE=on] [FIX=on] [SAFE=on]
	@dm="$(DRIVER_MEM)"; [ "$(JOB)" = "driver_oom" ] && dm="$${dm:-512m}"; \
	$(COMPOSE) exec -T -e APEX_AQE=$(AQE) -e APEX_FIX=$(FIX) -e APEX_SAFE=$(SAFE) spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	  $${dm:+--driver-memory $$dm} /opt/apex/jobs/$(JOB).py

e2e: env ## Lane exit proof: run ALL 4 pathologies and assert each signal (build→up→run→teardown)
	./scripts/e2e.sh

logs-check: ## Show the listener's contract rows (out/spark_events.jsonl)
	@tail -n 20 out/spark_events.jsonl 2>/dev/null || echo "no rows yet — run a pathology job first"

WORKERS ?= 2
scale: env ## Scale workers, e.g. make scale WORKERS=3
	$(COMPOSE) up -d --scale spark-worker=$(WORKERS) --wait
