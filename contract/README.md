# contract/ — the frozen interface (as artifacts)

The enforceable half of [../CONTRACT.md](../CONTRACT.md). Every stage builds against these files; obey the field names exactly.

| File | What it is | Who uses it |
|---|---|---|
| `sample_event.json` | One canonical telemetry event (the fixture) | `engine/` + `serve/` build against it **before `jar/` is real** — load it into ClickHouse and the brain is unblocked |
| `spark_events.ddl.sql` | Canonical `CREATE TABLE apex.spark_events` | `infra/` applies it (+ partitioning/TTL/rollups); `engine/`/`serve/` read it |
| `findings.ddl.sql` | Canonical `CREATE TABLE apex.findings` | `engine/` writes; `serve/` reads |

**To fill in:** copy the DDL + fixture from `LANE-0-CONTRACT.md` §1.4 and §2. These three files are commit #1 — they unblock the entire build.

> Rule: a stage may **add** a column; it may never rename or repurpose one. Any change here = version bump in [../CONTRACT.md](../CONTRACT.md).
