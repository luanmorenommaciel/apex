SHELL := /usr/bin/env bash
ROOT_DIR := $(CURDIR)
ENV_FILE := $(ROOT_DIR)/.env
COMPOSE_FILE := $(ROOT_DIR)/build/docker-compose.yml
COMPOSE := docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE)

include .env.example
-include .env

.PHONY: bootstrap build validate compose ingest-landing bronze sanity smoke spark-logs services test tests down removeimage clean-data workload-skew workload-shuffle workload-gc workload-oom workload-crossjoin workload-cache workloads diagnose validate-detectors

SPARK_SUBMIT := $(COMPOSE) exec -T spark-master env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
	--master spark://spark-master:7077 \
	--deploy-mode client \
	--conf spark.executorEnv.PYTHONPATH=/opt/spark/src

bootstrap:
	@build/scripts/bootstrap.sh

build:
	@build/scripts/validate-bootstrap.sh
	@build/scripts/prepare-image-contexts.sh >/dev/null
	@docker build \
		--build-arg MINIO_BASE_IMAGE=$(MINIO_BASE_IMAGE) \
		-f build/images/minio/Dockerfile.server \
		-t $(MINIO_IMAGE) \
		build/images/minio
	@docker build \
		--build-arg MINIO_MC_BASE_IMAGE=$(MINIO_MC_BASE_IMAGE) \
		-f build/images/minio/Dockerfile.client \
		-t $(MINIO_MC_IMAGE) \
		build/images/minio
	@docker build \
		--build-arg CLICKHOUSE_BASE_IMAGE=$(CLICKHOUSE_BASE_IMAGE) \
		-f build/images/clickhouse/Dockerfile \
		-t $(CLICKHOUSE_IMAGE) \
		build/images/clickhouse
	@docker build \
		--build-arg SPARK_BASE_IMAGE=$(SPARK_BASE_IMAGE) \
		-f build/images/spark/Dockerfile \
		-t $(SPARK_RUNTIME_IMAGE) \
		build/images/spark
	@docker build \
		--build-arg SPARK_RUNTIME_IMAGE=$(SPARK_RUNTIME_IMAGE) \
		-f build/images/spark-history/Dockerfile \
		-t $(SPARK_HISTORY_IMAGE) \
		build/images/spark-history
	@docker build \
		--build-arg GO_BASE_IMAGE=$(GO_BASE_IMAGE) \
		-f build/images/eventlog-loader/Dockerfile \
		-t $(LOADER_IMAGE) \
		build/images/eventlog-loader
	@docker build \
		--build-arg HYPERDX_BASE_IMAGE=$(HYPERDX_BASE_IMAGE) \
		-f build/images/clickstack/Dockerfile.hyperdx \
		-t $(HYPERDX_IMAGE) \
		build/images/clickstack
	@docker build \
		--build-arg MONGO_BASE_IMAGE=$(MONGO_BASE_IMAGE) \
		-f build/images/clickstack/Dockerfile.mongo \
		-t $(MONGO_IMAGE) \
		build/images/clickstack

validate:
	@build/scripts/validate.sh

compose: validate
	@$(COMPOSE) up -d minio minio-init clickhouse mongo hyperdx spark-master spark-worker spark-history
	@build/scripts/wait-ready.sh
	@build/scripts/seed-clickstack.sh

ingest-landing:
	@$(SPARK_SUBMIT) /opt/spark/src/apps/sample_scripts/simple_persist_customers_landing.py

bronze:
	@$(SPARK_SUBMIT) /opt/spark/src/apps/sample_scripts/smoke_job_plat_minio.py

sanity:
	@$(SPARK_SUBMIT) /opt/spark/src/apps/sample_scripts/check_sanity.py

smoke: ingest-landing bronze sanity
	@build/scripts/validate-smoke.sh

spark-logs:
	@$(COMPOSE) run --rm eventlog-loader
	@build/scripts/validate-clickhouse.sh
	@$(MAKE) diagnose

workload-skew:
	@$(SPARK_SUBMIT) /opt/spark/src/workloads/skew_join.py

workload-shuffle:
	@$(SPARK_SUBMIT) /opt/spark/src/workloads/shuffle_heavy.py

workload-gc:
	@$(SPARK_SUBMIT) /opt/spark/src/workloads/gc_churn.py

workload-oom:
	@$(SPARK_SUBMIT) /opt/spark/src/workloads/oom_victim.py

workload-crossjoin:
	@$(SPARK_SUBMIT) /opt/spark/src/workloads/cross_join.py

workload-cache:
	@$(SPARK_SUBMIT) /opt/spark/src/workloads/cache_heavy.py

workloads: workload-skew workload-shuffle workload-gc workload-oom workload-crossjoin workload-cache

diagnose:
	@PYTHONPATH=src uv run python -m apex_diagnostics.cli analyze $(if $(APP_ID),$(APP_ID),--latest) \
		|| echo "WARN: diagnostics failed or skipped; event-log loading unaffected"

# Ground-truth end-to-end: run every problem workload through the real stack,
# ingest + diagnose them (spark-logs), then assert each detector actually fired.
# Prerequisites run in order (workloads -> spark-logs) before the assertion pass.
# Re-sources .env so the host-side ClickHouse client gets CLICKHOUSE_PASSWORD.
validate-detectors: workload-skew workload-shuffle workload-gc workload-oom workload-crossjoin spark-logs
	@set -a; . $(ROOT_DIR)/.env.example; [ -f $(ROOT_DIR)/.env ] && . $(ROOT_DIR)/.env; set +a; \
		APEX_E2E=1 PYTHONPATH=src uv run pytest tests/e2e -m e2e -v

services:
	@build/scripts/services.sh

test: tests

tests:
	@uv run pytest

down:
	@$(COMPOSE) down

removeimage:
	@docker rmi $(SPARK_RUNTIME_IMAGE) $(SPARK_HISTORY_IMAGE) $(LOADER_IMAGE) $(MINIO_IMAGE) $(MINIO_MC_IMAGE) $(CLICKHOUSE_IMAGE) $(HYPERDX_IMAGE) $(MONGO_IMAGE) || true

clean-data:
	@$(COMPOSE) down -v --remove-orphans || true
	@mkdir -p build/var
	@if ! rm -rf build/var/minio-data build/var/clickhouse-data build/var/clickhouse-logs build/var/metrics build/var/mongo-data 2>/dev/null; then \
		echo "Local data contains root-owned files; cleaning through Docker."; \
		cleanup_image="$(SPARK_RUNTIME_IMAGE)"; \
		if ! docker image inspect "$$cleanup_image" >/dev/null 2>&1; then cleanup_image="$(SPARK_BASE_IMAGE)"; fi; \
		docker run --rm --pull=never --user 0 \
			-v "$(ROOT_DIR)/build/var:/target" \
			--entrypoint /bin/sh \
			"$$cleanup_image" \
			-c 'rm -rf /target/minio-data /target/clickhouse-data /target/clickhouse-logs /target/metrics /target/mongo-data'; \
	fi
	@mkdir -p build/var/minio-data build/var/clickhouse-data build/var/clickhouse-logs build/var/metrics build/var/mongo-data
