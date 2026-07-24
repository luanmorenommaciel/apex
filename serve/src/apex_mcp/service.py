"""Read-only diagnosis and telemetry comparison services."""

from __future__ import annotations

from .models import (
    Diagnosis, FindingView, FixSuggestion, KnowledgeHit, KnowledgeSearch,
    MetricComparison, RunComparison, StageView,
)


CONFIDENCE_SCORE = {"LOW": 0.3, "MEDIUM": 0.6, "HIGH": 0.9}


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

    def search_kb(self, query: str, top_k: int = 5) -> KnowledgeSearch:
        return KnowledgeSearch(
            query=query,
            hits=[KnowledgeHit.model_validate(row) for row in self._store.search_kb(query, top_k)],
        )

    def suggest_fix(
        self, job_id: str, finding_id: str | None = None, min_confidence: float = 0.75
    ) -> FixSuggestion:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence_out_of_range")
        rows = self._store.findings(job_id)
        selected = next((row for row in rows if finding_id is None or row["finding_id"] == finding_id), None)
        if selected is None:
            return FixSuggestion(
                job_id=job_id, finding_id=finding_id, status="not_found", confidence=0.0,
                min_confidence=min_confidence,
                rationale="No persisted finding matched this job_id and finding_id.",
            )
        confidence = CONFIDENCE_SCORE.get(str(selected.get("confidence", "")).upper(), 0.0)
        advisory = confidence < min_confidence
        action = str(selected["fix"])
        finding_ref = str(selected["finding_id"])
        return FixSuggestion(
            job_id=job_id,
            finding_id=finding_ref,
            status="advisory" if advisory else "proposed",
            confidence=confidence,
            min_confidence=min_confidence,
            diff=_proposal_diff(finding_ref, action),
            pr_body=_pr_body(selected, confidence, advisory),
            rationale=(
                "Confidence is below the human-review threshold; this is advisory only."
                if advisory else "A deterministic persisted finding supports a reviewable proposal."
            ),
        )

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


def _proposal_diff(finding_id: str, action: str) -> str:
    return "\n".join((
        "--- a/<operator-selected-spark-job.py>",
        "+++ b/<operator-selected-spark-job.py>",
        "@@ review-required APEX suggestion @@",
        f"+# APEX finding: {finding_id}",
        f"+# Suggested remediation: {action}",
        "+# Review the data shape and Spark configuration before making a manual change.",
    ))


def _pr_body(finding: dict, confidence: float, advisory: bool) -> str:
    status = "advisory" if advisory else "proposed"
    return "\n".join((
        "## APEX suggested remediation",
        f"- Status: {status}; human approval is required.",
        f"- Finding: `{finding['finding_id']}` ({finding['type']}) on stage {finding['stage_id']}",
        f"- Confidence: {confidence:.2f}",
        f"- Evidence: {finding['evidence']}",
        f"- Proposed action: {finding['fix']}",
        "- This MCP tool did not change files, Git state, or a running Spark job.",
    ))
