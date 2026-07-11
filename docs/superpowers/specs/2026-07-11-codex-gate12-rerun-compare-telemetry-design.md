# Gate 12 Design: Re-Run/Compare Telemetry

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Decision

Add a read-only comparison tool over two telemetry snapshots:

```text
compare_job_telemetry(before_job_id, after_job_id)
```

## Why

Gate 11 can apply a reviewed change safely. The next question is whether the next job execution got better. The Commander should answer from evidence, not from the fact that a patch was applied.

## Data Flow

```text
before_job_id -> query telemetry -> diagnose_findings -> snapshot
after_job_id  -> query telemetry -> diagnose_findings -> snapshot
snapshots     -> metric deltas + resolved/new findings -> status
```

## Output Shape

```json
{
  "status": "improved",
  "before_job_id": "before-job",
  "after_job_id": "after-job",
  "summary": {
    "resolved_findings": ["shuffle_skew_candidate"],
    "new_findings": [],
    "improved_metric_count": 2,
    "regressed_metric_count": 0
  },
  "comparisons": [
    {
      "metric": "max_skew_ratio",
      "before": 29.5,
      "after": 1.0,
      "delta": -28.5,
      "status": "improved"
    }
  ]
}
```

## Safety

- Read-only.
- Does not mutate files.
- Does not write to ClickHouse.
- Does not trigger Spark execution.
- Does not publish branches.

## Out Of Scope

- Automatic Spark re-run orchestration.
- CI scheduler.
- Automatic rollback.
- UI charts.

## Next Gate

Gate 13 should add controlled re-run orchestration:

```text
apply verified -> run job command -> collect telemetry -> compare_job_telemetry
```
