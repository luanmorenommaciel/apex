# engine/ — ⑤ reason

**Role:** CrewAI analysis brain. 5 **deterministic watchers** (Tier 1, no LLM) + **gated** CrewAI correlation/Judger (Tier 2) → `findings`.
**Language:** Python (CrewAI + clickhouse-connect) · **Branch prefix:** `engine/*` (e.g. `engine/T6-skew-watcher`)
**Full brief:** [../docs/lanes/ENGINE.md](../docs/lanes/ENGINE.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `analyze(job_id)` runs the watchers, escalates only `confidence<0.6 AND severity>=high` through the crew, inserts validated `Finding` rows. A clean job → 0 rows + **0 LLM calls**.

**Status C0/C1:** o núcleo determinístico, a consulta ClickHouse parametrizada e o sink de findings estão implementados e testados com fixture, fake-client e ClickHouse real. A evidência resumida e o comando de reprodução estão em [`VALIDATION.md`](VALIDATION.md). Crew/Judge permanece C5.

**Buildable FIRST against the fixture** — C0/C1 reads [`../contract/sample_event.json`](../contract/) directly before ClickHouse exists. It adds a strict `StageEvent` adapter, contract-exact `Finding` rows, five deterministic watchers and an evidence validator. The ClickHouse sink and Crew/Judge remain C4/C5 work.

```bash
cd engine
uv run --extra dev pytest
```

Layout: `pyproject.toml` · `src/apex_engine/` (schema · watchers · validation · pipeline) · `tests/`.
Watch: watchers are **SQL rules, not agents**. CrewAI is ONLY for gated correlation + the adversarial Judger. Models: `claude-haiku-4-5` → `claude-sonnet-5` → `claude-opus-4-8`.
