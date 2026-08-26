# Apex dev-env — Makefile (T13).  `make help` lists targets.
SHELL   := /usr/bin/env bash
# Whenever apex-collect-net exists (collect lane is up), compose WITH the C3
# overlay so master/worker join that network and plugin telemetry reaches the
# canonical store. Without this, a plain `make up` / `run-pathology` would
# RECREATE containers off the overlay and silently drop OTLP delivery.
C3_NET_UP := $(shell docker network inspect apex-collect-net >/dev/null 2>&1 && echo 1)
ifeq ($(C3_NET_UP),1)
COMPOSE := docker compose -f docker-compose.yml -f docker-compose.c3-otlp.yml
else
COMPOSE := docker compose
endif
C3_COMPOSE := docker compose -f docker-compose.yml -f docker-compose.c3-otlp.yml

.DEFAULT_GOAL := help
.PHONY: help env env-spark41 build up down clean ps verify doctor gen-data run-pathology scale calibrate c3-up c3-plugin-skew c4-aqe-skew c4-aqe-skewsplit c4-aqe-probe e2e e2e-canonical

help: ## List available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n",$$1,$$2}'

env: ## Create .env from .env.example if it doesn't exist yet
	@python3 scripts/ensure_env.py .env.example .env

env-spark41: ## Create .env from the baseline plus the Spark 4.1.2 overlay
	@python3 scripts/ensure_env.py .env.example .env.spark41.example .env

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
	  --master 'local[2]' --conf spark.eventLog.enabled=false /opt/apex/tests/prove_fingerprint.py

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
	  --conf spark.eventLog.enabled=false /opt/apex/tests/prove_fingerprint.py

APEX_IMAGE ?= apex-spark:local
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

c3-up: env ## Join infra's OTLP network and wait for the Spark driver service
	$(C3_COMPOSE) up -d --wait

c3-plugin-skew: c3-up ## C3: ApexPlugin -> infra OTLP collector
	$(C3_COMPOSE) exec -T -e APEX_AQE=off -e APEX_FIX=off -e APEX_SAFE=off spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	  --conf spark.plugins=apex.ApexPlugin \
	  --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 \
	  --conf spark.apex.aqe.enabled=false \
	  /opt/apex/jobs/skew_join.py

c4-aqe-skew: c3-up ## C4: AQE skew split + ApexPlugin plan_transition -> infra OTLP collector
	$(C3_COMPOSE) exec -T -e APEX_AQE=on -e APEX_FIX=off -e APEX_SAFE=off spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	  --conf spark.plugins=apex.ApexPlugin \
	  --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 \
	  --conf spark.apex.aqe.enabled=true \
	  /opt/apex/jobs/skew_join.py

c4-aqe-skewsplit: c3-up ## C4 calibration: force a real AQE skew_split without changing the default cell
	$(C3_COMPOSE) exec -T -e APEX_AQE=on -e APEX_FIX=off -e APEX_SAFE=off \
	  -e APEX_AQE_SKEW_THRESHOLD=1m -e APEX_AQE_ADVISORY_PARTITION=512k \
	  -e APEX_AQE_SKEW_FACTOR=2 -e APEX_AQE_COALESCE=false \
	  -e APEX_AQE_FORCE_OPTIMIZE_SKEW=true spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	  --conf spark.plugins=apex.ApexPlugin \
	  --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 \
	  --conf spark.apex.aqe.enabled=true \
	  /opt/apex/jobs/skew_join.py

c4-aqe-probe: c3-up ## C4 calibration probe: mirror the JAR AQE transition test at runtime
	$(C3_COMPOSE) exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	  --conf spark.plugins=apex.ApexPlugin \
	  --conf spark.apex.otlp.endpoint=http://apex-otel-collector:4318 \
	  --conf spark.apex.aqe.enabled=true \
	  /opt/apex/jobs/aqe_skew_split_probe.py

e2e: e2e-canonical ## Official pathology gate: 4 jobs asserted through canonical ClickHouse

e2e-canonical: env ## Canonical proof: 4 pathologies via OTLP/ClickHouse; requires running collect+infra and password env
	./scripts/e2e_canonical.sh $(E2E_ARGS)

WORKERS ?= 2
scale: env ## Scale workers, e.g. make scale WORKERS=3
	$(COMPOSE) up -d --scale spark-worker=$(WORKERS) --wait

RUNS ?= 3
calibrate: ## Prove each pathology is mechanical: RUNS× per job, report signal CVs + noise floor
	python3 scripts/calibrate.py --runs $(RUNS)
