"""Tier-1 deterministic watchers. They receive data; they never call an LLM."""

from __future__ import annotations

from collections.abc import Iterable

from .schema import Confidence, Finding, FindingType, Severity, StageEvent

MIN_SHUFFLE_BYTES = 1_073_741_824
SKEW_WARNING_RATIO = 5.0
SKEW_CRITICAL_RATIO = 10.0
GC_WARNING_RATIO = 0.10
GC_CRITICAL_RATIO = 0.25
COST_SHUFFLE_TO_INPUT_RATIO = 50.0


def run_all(events: Iterable[StageEvent]) -> list[Finding]:
    findings: list[Finding] = []
    for event in events:
        findings.extend(watch_shuffle(event))
        findings.extend(watch_skew(event))
        findings.extend(watch_memory(event))
        findings.extend(watch_cost(event))
        findings.extend(watch_code(event))
    return findings


def watch_shuffle(event: StageEvent) -> list[Finding]:
    spilled = event.spill_disk_bytes + event.spill_mem_bytes
    if event.shuffle_read_bytes < MIN_SHUFFLE_BYTES:
        return []
    severity = Severity.CRITICAL if spilled else Severity.WARNING
    confidence = Confidence.HIGH if spilled else Confidence.MEDIUM
    evidence = f"shuffle_read_bytes={event.shuffle_read_bytes}; spilled_bytes={spilled}"
    return [_finding(event, FindingType.SHUFFLE, severity, confidence, evidence,
        "Shuffle pressure can extend stage runtime and consume local disk.",
        "Review partition sizing and reduce shuffle spill before scaling resources.",
        {"shuffle_read_bytes": event.shuffle_read_bytes, "spilled_bytes": spilled}, "shuffle_watcher")]


def watch_skew(event: StageEvent) -> list[Finding]:
    ratio = event.p99_p50_ratio
    if ratio <= SKEW_WARNING_RATIO:
        return []
    severity = Severity.CRITICAL if ratio > SKEW_CRITICAL_RATIO else Severity.WARNING
    confidence = Confidence.HIGH if severity is Severity.CRITICAL else Confidence.MEDIUM
    return [_finding(event, FindingType.SKEW_ON_JOIN, severity, confidence,
        f"p99/p50={ratio:.1f}x (p99={event.task_duration_p99_ms:.0f}ms, p50={event.task_duration_p50_ms:.0f}ms)",
        "Long-tail tasks dominate the stage runtime.",
        "Validate the join key distribution and enable AQE skew join before considering salting.",
        {"p99_p50_ratio": ratio, "task_duration_p50_ms": event.task_duration_p50_ms,
         "task_duration_p99_ms": event.task_duration_p99_ms, "task_count": event.task_count}, "skew_watcher")]


def watch_memory(event: StageEvent) -> list[Finding]:
    reason = event.failure_reason.lower()
    if "outofmemoryerror" in reason or "executorlostfailure" in reason:
        return [_finding(event, FindingType.DRIVER_OOM, Severity.BLOCKER, Confidence.HIGH,
            "failure_reason indicates an out-of-memory failure",
            "The failed execution cannot complete without changing memory or data shape.",
            "Reduce partition volume, inspect joins and review driver/executor memory before rerun.",
            {"failure_reason": event.failure_reason}, "memory_watcher")]
    if event.executor_run_time_ms <= 0 or event.gc_ratio < GC_WARNING_RATIO:
        return []
    severity = Severity.CRITICAL if event.gc_ratio >= GC_CRITICAL_RATIO else Severity.WARNING
    confidence = Confidence.HIGH if severity is Severity.CRITICAL else Confidence.MEDIUM
    return [_finding(event, FindingType.MEMORY, severity, confidence,
        f"gc_ratio={event.gc_ratio:.3f} (gc_time_ms={event.gc_time_ms})",
        "Garbage collection is consuming a material portion of executor runtime.",
        "Review partition size, caching and memory pressure before adding executors.",
        {"gc_ratio": event.gc_ratio, "gc_time_ms": event.gc_time_ms,
         "executor_run_time_ms": event.executor_run_time_ms}, "memory_watcher")]


def watch_cost(event: StageEvent) -> list[Finding]:
    if event.input_bytes <= 0:
        return []
    ratio = event.shuffle_read_bytes / event.input_bytes
    if ratio < COST_SHUFFLE_TO_INPUT_RATIO:
        return []
    return [_finding(event, FindingType.COST, Severity.WARNING, Confidence.MEDIUM,
        f"shuffle/input={ratio:.1f}x ({event.shuffle_read_bytes}/{event.input_bytes} bytes)",
        "Shuffle amplification can inflate runtime and infrastructure cost.",
        "Review partitioning and join strategy; compare before and after a guarded rerun.",
        {"shuffle_to_input_ratio": ratio}, "cost_watcher")]


def watch_code(event: StageEvent) -> list[Finding]:
    if "CartesianProduct" in event.plan_json:
        return [_finding(event, FindingType.CARTESIAN_PRODUCT, Severity.CRITICAL, Confidence.HIGH,
            "logical plan contains CartesianProduct", "A Cartesian product can grow work multiplicatively.",
            "Inspect join keys and add an explicit join condition before rerun.",
            {"operator": "CartesianProduct"}, "code_watcher")]
    if "BroadcastNestedLoopJoin" in event.plan_json:
        return [_finding(event, FindingType.CARTESIAN_PRODUCT, Severity.WARNING, Confidence.MEDIUM,
            "logical plan contains BroadcastNestedLoopJoin", "A nested-loop join can become expensive as the broadcast side grows.",
            "Confirm a selective join condition and the broadcast-side cardinality.",
            {"operator": "BroadcastNestedLoopJoin"}, "code_watcher")]
    return []


def _finding(event: StageEvent, finding_type: FindingType, severity: Severity,
             confidence: Confidence, evidence: str, impact: str, fix: str,
             details: dict[str, object], detected_by: str) -> Finding:
    return Finding(job_id=event.job_id, stage_id=event.stage_id, type=finding_type,
        severity=severity, evidence=evidence, impact=impact, fix=fix, confidence=confidence,
        detected_by=detected_by, details={"app_id": event.app_id, **details})

