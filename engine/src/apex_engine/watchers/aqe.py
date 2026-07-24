"""AQE watcher — DETERMINISTIC, and the one signal competitors do not have.

Every other watcher reads *symptoms* (bytes, spill, p50/p99) and infers a cause.
This one reads Spark's own runtime *decisions* from `apex.plan_transitions`. When
AQE splits a skewed partition, it is not evidence that skew is likely — it is
Spark stating that it found skew and acted on it. That is ground truth, at $0,
with no LLM involved, and it is strictly stronger than any p99/p50 heuristic.

Honesty about what each transition actually means (they are NOT all skew):
  * `skew_split`  -> AQE split a skewed partition. Direct skew ground truth.
  * `coalesce`    -> AQE merged small post-shuffle partitions. That is evidence of
                     an over-sized shuffle partition count, NOT of skew. Reported
                     as its own finding, not folded into the skew story.
  * `join_switch` -> AQE demoted a sort-merge join to broadcast, i.e. the static
                     estimate was wrong. Useful, low severity.
Only `confidence = HIGH` transitions are treated as ground truth; contract v0.2
marks parsed partition counts as BEST_EFFORT, which is corroboration, not proof.

Stage attribution: contract v0.2 keys transitions by (job_id, execution_id) and
states the execution->stage map is a later enhancement. These findings therefore
carry the job-level sentinel stage_id rather than a fabricated stage.
"""

from __future__ import annotations

from collections import defaultdict

from ..schema import Confidence, Finding, FindingType, PlanTransition, Severity
from .base import JOB_LEVEL_STAGE_ID, build_finding

NAME = "aqe_watcher"

SKEW_SPLIT = "skew_split"
COALESCE = "coalesce"
JOIN_SWITCH = "join_switch"


def evaluate_job(job_id: str, app_id: str, transitions: list[PlanTransition]) -> list[Finding]:
    ground_truth = [t for t in transitions if t.is_ground_truth]
    if not ground_truth:
        return []

    by_type: dict[str, list[PlanTransition]] = defaultdict(list)
    for transition in ground_truth:
        by_type[transition.transition_type].append(transition)

    findings: list[Finding] = []

    if splits := by_type.get(SKEW_SPLIT):
        findings.append(
            _finding(
                job_id, app_id, splits,
                finding_type=FindingType.SKEW_ON_JOIN,
                severity=Severity.CRITICAL,
                confidence_score=0.97,
                evidence=(
                    f"AQE split skewed partitions at runtime in {len(splits)} re-plan(s) "
                    f"[{_describe(splits)}] — Spark itself detected the skew"
                ),
                impact=(
                    "A skewed partition was large enough that Spark had to break it up mid-query; "
                    "without AQE this stage would be held open by a single task."
                ),
                fix=(
                    "Keep spark.sql.adaptive.skewJoin.enabled=true, then remove the skew at the "
                    "source (salt the hot key or pre-aggregate) so the split is not needed."
                ),
            )
        )

    if coalesces := by_type.get(COALESCE):
        findings.append(
            _finding(
                job_id, app_id, coalesces,
                finding_type=FindingType.AQE_REPLAN,
                severity=Severity.WARNING,
                confidence_score=0.9,
                evidence=(
                    f"AQE coalesced post-shuffle partitions in {len(coalesces)} re-plan(s) "
                    f"[{_describe(coalesces)}] — the configured shuffle partition count is too high"
                ),
                impact=(
                    "Spark had to merge undersized partitions at runtime; the static "
                    "spark.sql.shuffle.partitions is oversized for this data volume, "
                    "costing scheduler overhead on every run."
                ),
                fix=(
                    "Lower spark.sql.shuffle.partitions toward the coalesced count, or leave "
                    "AQE coalescing on and tune advisoryPartitionSizeInBytes."
                ),
            )
        )

    if switches := by_type.get(JOIN_SWITCH):
        findings.append(
            _finding(
                job_id, app_id, switches,
                finding_type=FindingType.AQE_REPLAN,
                severity=Severity.INFO,
                confidence_score=0.9,
                evidence=f"AQE changed join strategy at runtime [{_describe(switches)}]",
                impact="The planner's static size estimate was wrong; AQE corrected it mid-query.",
                fix="Refresh table statistics (ANALYZE TABLE) so the initial plan is right without AQE's rescue.",
            )
        )

    return findings


def _finding(job_id: str, app_id: str, transitions: list[PlanTransition], **kwargs) -> Finding:
    return build_finding(
        job_id=job_id,
        app_id=app_id,
        stage_id=JOB_LEVEL_STAGE_ID,
        detected_by=NAME,
        details={
            "source": "apex.plan_transitions",
            "ground_truth": True,
            "execution_ids": sorted({t.execution_id for t in transitions}),
            "transitions": [t.model_dump() for t in transitions],
        },
        **kwargs,
    )


def _describe(transitions: list[PlanTransition]) -> str:
    """Compact, already-redacted descriptors straight from the contract fields."""
    return "; ".join(dict.fromkeys(t.detail for t in transitions if t.detail))


def corroborate_skew(findings: list[Finding], transitions: list[PlanTransition]) -> list[Finding]:
    """Upgrade heuristic skew findings that AQE independently confirms.

    A p99/p50 ratio in the ambiguous 5-10x band is normally gate-eligible and
    may cost an LLM call. If AQE split a skewed partition in the same job, the
    heuristic is corroborated by ground truth: raise confidence to HIGH so the
    finding emits at $0 instead of being escalated. This is the whole point of
    consuming plan_transitions.
    """
    if not any(t.is_ground_truth and t.transition_type == SKEW_SPLIT for t in transitions):
        return findings

    upgraded: list[Finding] = []
    for finding in findings:
        if finding.type is FindingType.SKEW_ON_JOIN and finding.detected_by != NAME:
            upgraded.append(
                finding.model_copy(update={
                    "confidence_score": max(finding.confidence_score, 0.93),
                    "confidence": Confidence.HIGH,
                    "severity": Severity.CRITICAL,
                    "evidence": f"{finding.evidence}; corroborated by an AQE skew_split in the same job",
                    "detected_by": f"{finding.detected_by}+aqe",
                    "details": {**finding.details, "aqe_corroborated": True},
                })
            )
        else:
            upgraded.append(finding)
    return upgraded
