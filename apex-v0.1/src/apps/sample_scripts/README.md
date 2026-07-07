# Sample Scripts

This folder keeps the first platform sample deliberately segmented. The goal is to make the lakehouse flow easy to inspect and easy to replace later with real entities.

## Flow

1. `simple_persist_customers_landing.py` creates a tiny fake customer DataFrame and writes it to `s3a://lakehouse/landing/customer` as JSON. It is intentionally simple and does not use `SparkPlatJob` yet, because it represents an ingestion edge.
2. `smoke_job_plat_minio.py` is the contract-based Spark job. It reads customer JSON from landing, applies a named DataFrame transform, and writes `s3a://lakehouse/bronze/customer` as Delta.
3. `check_sanity.py` is the validation step. It reads landing JSON and bronze Delta, checks row counts and expected columns, and runs a small grouped DataFrame action so the event logs include useful execution details.

## Make Targets

- `make ingest-landing`: run only the landing ingestion script.
- `make bronze`: run only the landing-to-bronze SparkPlatJob.
- `make sanity`: run only the sanity validation script.
- `make smoke`: run all three steps and then validate Spark History, MinIO landing data, MinIO bronze Delta data, and Spark event logs.

## Script Contract

Every executable sample script should keep a module docstring with:

- a manual `spark-submit` command that assumes Compose is already running;
- an explicit numbered execution sequence;
- function or method docstrings for the code that owns each important step.

Use this shape so a new user can open one script and understand where config loading, Spark session creation, reads, transformations, writes, checks, and shutdown happen.

## DataFrame Guidance

Prefer PySpark DataFrame APIs for these samples. Use `.transform(...)` for reusable transformations, avoid unnecessary `orderBy()`, and keep data-quality checks in validation scripts instead of embedding Spark actions inside transformation jobs.
