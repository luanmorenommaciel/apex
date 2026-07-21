# dev/ — ① generate

**Role:** Spark/Delta pathology lab. Reproducible jobs (skew · spill · bad-shuffle · driver-OOM) + History Server + MinIO.
**Language:** Python + Docker · **Branch prefix:** `dev/*` (e.g. `dev/T8-generate-data`)
**Full brief:** [../docs/lanes/DEV.md](../docs/lanes/DEV.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `make run-pathology JOB=skew_join` completes, appears in the History Server, and lands a `spark_events` row per stage keyed by `job_id`.

Layout: `docker-compose.yml` · `Dockerfile` · `jobs/` (generate_data + 4 pathologies) · `common/` (session, listener) · `Makefile`.
