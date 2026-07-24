"""Code watcher — DETERMINISTIC. Query shape, read from the plan.

`plan_json` is a redacted Catalyst TREE-STRING, not JSON (CONTRACT.md is
explicit). It is matched as OPAQUE DATA: operator names are searched for, and
plan text is never echoed into `evidence` and never reaches an LLM prompt from
here. A plan carrying "ignore previous instructions" is just a string that does
not match an operator name.

On the duplicate-fingerprint rule (T9): a repeated `plan_fingerprint` across
stages is NOT by itself a defect — one query legitimately spans many stages,
and the real P0 job has five stages sharing a single fingerprint. Flagging that
would make the engine cry wolf. The rule fires only when the repetition means
real work is redone: the same plan re-reading a substantial amount of SOURCE
data more than once, which is the shape `cache()`/`persist()` exists to fix.
"""

from __future__ import annotations

from collections import defaultdict

from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import MIB, human_bytes, stage_finding

NAME = "code_watcher"

# Operator name -> (severity, confidence, why it matters)
RISKY_OPERATORS = {
    "CartesianProduct": (
        Severity.CRITICAL, 0.92,
        "A cartesian product multiplies row counts; cost grows with the product of both sides.",
        "Add an explicit join condition — an unintended cross join is almost always a missing predicate.",
    ),
    "BroadcastNestedLoopJoin": (
        Severity.WARNING, 0.7,
        "A nested-loop join compares every pair on the broadcast side; it degrades sharply as that side grows.",
        "Confirm the join has a selective equi-condition and that the broadcast side stays small.",
    ),
}

# A re-scan is only worth reporting when the data re-read is substantial.
RESCAN_MIN_INPUT_BYTES = 256 * MIB
RESCAN_MIN_STAGES = 2

SQL = """
SELECT
  job_id, any(app_id) AS app_id, stage_id,
  argMax(plan_json, ts)        AS plan_json,
  argMax(plan_fingerprint, ts) AS plan_fingerprint,
  argMax(input_bytes, ts)      AS input_bytes
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
ORDER BY stage_id
"""


def evaluate(stage: StageAggregate) -> Finding | None:
    for operator, (severity, confidence, impact, fix) in RISKY_OPERATORS.items():
        if operator in stage.plan_json:
            return stage_finding(
                stage,
                finding_type=FindingType.CARTESIAN_PRODUCT,
                severity=severity,
                confidence_score=confidence,
                # Only the matched operator name is quoted — never plan text.
                evidence=f"physical plan for stage {stage.stage_id} contains {operator}",
                impact=impact,
                fix=fix,
                detected_by=NAME,
                details={"operator": operator, "plan_fingerprint": stage.plan_fingerprint},
            )
    return None


def evaluate_job(stages: list[StageAggregate]) -> list[Finding]:
    """Same source data scanned by the same plan in more than one stage."""
    by_fingerprint: dict[str, list[StageAggregate]] = defaultdict(list)
    for stage in stages:
        if stage.plan_fingerprint and stage.input_bytes >= RESCAN_MIN_INPUT_BYTES:
            by_fingerprint[stage.plan_fingerprint].append(stage)

    findings: list[Finding] = []
    for fingerprint, group in sorted(by_fingerprint.items()):
        if len(group) < RESCAN_MIN_STAGES:
            continue
        stage_ids = sorted(s.stage_id for s in group)
        rescanned = sum(s.input_bytes for s in group[1:])
        findings.append(
            stage_finding(
                group[0],
                finding_type=FindingType.DUPLICATE_SCAN,
                severity=Severity.WARNING,
                confidence_score=0.68,
                evidence=(
                    f"plan_fingerprint {fingerprint[:12]}... re-reads source data in "
                    f"{len(group)} stages {stage_ids}; {human_bytes(rescanned)} scanned again"
                ),
                impact="The same source data is read more than once for the same computation.",
                fix="cache()/persist() the shared DataFrame, or restructure so the branch is computed once.",
                detected_by=NAME,
                details={"plan_fingerprint": fingerprint, "stage_ids": stage_ids,
                         "rescanned_bytes": rescanned},
            )
        )
    return findings
