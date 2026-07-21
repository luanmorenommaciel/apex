# engine/ — ⑤ reason

**Role:** CrewAI analysis brain. 5 **deterministic SQL watchers** (Tier 1, no LLM) + **gated** CrewAI correlation/Judger (Tier 2) → `findings`.
**Language:** Python (CrewAI + clickhouse-connect) · **Branch prefix:** `engine/*` (e.g. `engine/T6-skew-watcher`)
**Full brief:** [../docs/lanes/ENGINE.md](../docs/lanes/ENGINE.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `analyze(job_id)` runs the watchers, escalates only `confidence<0.6 AND severity>=high` through the crew, inserts validated `Finding` rows. A clean job → 0 rows + **0 LLM calls**.

**Buildable FIRST against the fixture** — load [`../contract/sample_event.json`](../contract/) into ClickHouse and build the whole brain before `jar/` exists.
Layout: `pyproject.toml` · `apex_engine/` (schema · ch_client · watchers/ · crew/ · gate · sink · pipeline).
Watch: watchers are **SQL rules, not agents**. CrewAI is ONLY for gated correlation + the adversarial Judger. Models: `claude-haiku-4-5` → `claude-sonnet-5` → `claude-opus-4-8`.
