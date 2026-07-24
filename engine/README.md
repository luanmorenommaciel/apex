# engine/ — ⑤ reason

**Role:** CrewAI analysis brain. 5 **deterministic watchers** (Tier 1, no LLM) + **gated** CrewAI correlation/Judger (Tier 2) → `findings`.
**Language:** Python (CrewAI + clickhouse-connect) · **Branch prefix:** `engine/*` (e.g. `engine/T6-skew-watcher`)
**Full brief:** [../docs/lanes/ENGINE.md](../docs/lanes/ENGINE.md) · **Obeys:** [../CONTRACT.md](../CONTRACT.md)
**Exit criterion:** `analyze(job_id)` runs the watchers, escalates only `confidence<0.6 AND severity>=high` through the crew, inserts validated `Finding` rows. A clean job → 0 rows + **0 LLM calls**.

**Status C0/C1 + adaptador C5:** o núcleo determinístico, a consulta ClickHouse parametrizada e o sink de findings estão implementados e testados com fixture, fake-client e ClickHouse real. A evidência resumida e o comando de reprodução estão em [`VALIDATION.md`](VALIDATION.md). O adaptador Crew/Judge C5 está implementado e só pode ser chamado para `confidence=LOW` e `severity>=critical`.

**Buildable FIRST against the fixture** — C0/C1 reads [`../contract/sample_event.json`](../contract/) directly before ClickHouse exists. It adds a strict `StageEvent` adapter, contract-exact `Finding` rows, five deterministic watchers and an evidence validator. The ClickHouse sink and Crew/Judge remain C4/C5 work.

```bash
cd engine
uv run --extra dev pytest
```

Layout: `pyproject.toml` · `src/apex_engine/` (schema · watchers · validation · pipeline) · `tests/`.
Watch: watchers are **SQL rules, not agents**. CrewAI is ONLY for gated correlation + the adversarial Judger. Models: `claude-haiku-4-5` → `claude-sonnet-5` → `claude-opus-4-8`.

## Crew/Judge C5

`apex_engine.crew` is deliberately lazy: a deterministic installation neither
imports CrewAI nor requires a provider key. Set `APEX_CREW_JUDGE_ENABLED=1`,
install `uv sync --extra crew`, and provide `ANTHROPIC_API_KEY` only for an
operator-approved Tier-2 run. The Judge receives a validated Tier-1 finding,
may return only `confirm` or `reject`, and must cite text already present in
`finding.evidence`. Rejection is returned as auditable pipeline output; the
adapter never writes to ClickHouse, a filesystem, Git, or Spark.
