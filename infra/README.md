# infra/ — ④ store & serve

**Role:** ClickStack data platform (ClickHouse + HyperDX + collector + MongoDB). Applies the contract DDL, rollups, dashboards.
**Language:** SQL + Docker · **Branch prefix:** `infra/*` (e.g. `infra/T5-rollup-mv`)
**Full brief:** [../docs/lanes/INFRA.md](../docs/lanes/INFRA.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `curl` an OTLP payload → row in `apex.spark_events` → a HyperDX tile **and** a skew query both return it, traced by `job_id`.

Layout: `docker-compose.yml` (4 services) · `sql/` (001_db · 002_spark_events · 003_findings · 004_rollup_mv · 005_skew) · `dashboards/`.
Note: the **canonical** `CREATE TABLE`s live in [`../contract/`](../contract/); `infra/sql/` applies them and adds partitioning/TTL/rollups. Watch: MongoDB is **required** for HyperDX state; `Map(String,String)` attrs, not JSON; register a **custom Source** for `spark_events`.
