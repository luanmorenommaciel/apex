"""Read-only diagnosis and telemetry comparison services."""

from __future__ import annotations

from .models import Diagnosis, FindingView, MetricComparison, RunComparison, StageView


class ApexReadService:
    def __init__(self, store) -> None:
        self._store = store

    def analyze_run(self, job_id: str) -> Diagnosis:
        stage_rows = self._store.stages(job_id)
        stages = [_stage_view(row) for row in stage_rows]
        if not stages:
            return Diagnosis(job_id=job_id, status="not_found", summary="No stage telemetry exists for this job_id.")
        findings = [FindingView.model_validate(row) for row in self._store.findings(job_id)]
        app_id = str(stage_rows[0].get("app_id") or "") or None
        status = "findings" if findings else "healthy"
        summary = f"{len(findings)} persisted finding(s) across {len(stages)} stage(s)." if findings else f"{len(stages)} stage(s) with no persisted findings."
        return Diagnosis(job_id=job_id, app_id=app_id, status=status, stages=stages, findings=findings, summary=summary)

    def compare_runs(self, baseline_job_id: str, current_job_id: str) -> RunComparison:
        before = self._metrics(baseline_job_id)
        after = self._metrics(current_job_id)
        missing = [job_id for job_id, metrics in ((baseline_job_id, before), (current_job_id, after)) if metrics is None]
        if missing:
            return RunComparison(baseline_job_id=baseline_job_id, current_job_id=current_job_id, status="not_comparable", missing_job_ids=missing)
        comparisons = [_comparison(name, before[name], after[name]) for name in sorted(before)]
        improved = sum(item.status == "improved" for item in comparisons)
        regressed = sum(item.status == "regressed" for item in comparisons)
        status = "improved" if improved > regressed else "regressed" if regressed > improved else "unchanged"
        return RunComparison(baseline_job_id=baseline_job_id, current_job_id=current_job_id, status=status, comparisons=comparisons)

    def _metrics(self, job_id: str) -> dict[str, float] | None:
        stages = [_stage_view(row) for row in self._store.stages(job_id)]
        if not stages:
            return None
        findings = self._store.findings(job_id)
        return {
            "finding_count": float(len(findings)),
            "max_p99_p50_ratio": max(stage.p99_p50_ratio for stage in stages),
            "total_spilled_bytes": float(sum(stage.spilled_bytes for stage in stages)),
        }


def _stage_view(row: dict) -> StageView:
    p50 = float(row.get("p50_ms") or 0)
    p99 = float(row.get("p99_ms") or 0)
    return StageView(
        stage_id=int(row["stage_id"]),
        shuffle_read_bytes=int(row.get("shuffle_read_bytes") or 0),
        spilled_bytes=int(row.get("spilled_bytes") or 0),
        p50_ms=p50,
        p99_ms=p99,
        p99_p50_ratio=p99 / p50 if p50 else 0.0,
    )


def _comparison(metric: str, before: float, after: float) -> MetricComparison:
    status = "unchanged" if before == after else "improved" if after < before else "regressed"
    return MetricComparison(metric=metric, before=before, after=after, delta=after - before, status=status)
