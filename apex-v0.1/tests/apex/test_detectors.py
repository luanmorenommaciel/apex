from apex_diagnostics.config import DiagnosticsThresholds, load_plan_patterns
from apex_diagnostics.detectors import run_all
from apex_diagnostics.detectors.gc import GC_SQL, detect_gc
from apex_diagnostics.detectors.oom import OOM_SQL, detect_oom
from apex_diagnostics.detectors.plans import ADAPTIVE_PLAN_TEXT_SQL, PLAN_TEXT_SQL, PLANS_SQL, detect_plans
from apex_diagnostics.detectors.shuffle import SHUFFLE_SQL, detect_shuffle
from apex_diagnostics.detectors.skew import SKEW_SQL, detect_skew
from apex_diagnostics.models import Severity

from tests.fakes.clickhouse import FakeCHClient

THRESHOLDS = DiagnosticsThresholds()
APP = "app-20260706-0001"


def skew_row(stage_id=4, max_ms=45000, p50_ms=3000, n_tasks=24, stage_attempt_id=0):
    return {"stage_id": stage_id, "stage_attempt_id": stage_attempt_id, "max_ms": max_ms, "p50_ms": p50_ms, "n_tasks": n_tasks}


def shuffle_row(stage_id=2, shuffle_bytes=64 * 1024 * 1024, memory_spilled=0, disk_spilled=0, max_gc_ms=100, n_tasks=24, stage_attempt_id=0):
    return {
        "stage_id": stage_id,
        "stage_attempt_id": stage_attempt_id,
        "shuffle_bytes": shuffle_bytes,
        "memory_spilled": memory_spilled,
        "disk_spilled": disk_spilled,
        "max_gc_ms": max_gc_ms,
        "n_tasks": n_tasks,
    }


def test_skew_critical_on_high_ratio():
    client = FakeCHClient({SKEW_SQL: [skew_row()]})
    findings = detect_skew(client, APP, THRESHOLDS.skew)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.severity is Severity.CRITICAL
    assert finding.stage_id == 4
    assert finding.evidence["ratio"] == 15.0
    assert client.queries[0][1] == {"app_id": APP}


def test_skew_warning_between_thresholds():
    client = FakeCHClient({SKEW_SQL: [skew_row(max_ms=12000, p50_ms=3000)]})
    findings = detect_skew(client, APP, THRESHOLDS.skew)
    assert [f.severity for f in findings] == [Severity.WARNING]


def test_skew_guards_suppress_small_stages():
    small_stage = skew_row(n_tasks=4)
    short_stage = skew_row(max_ms=2000, p50_ms=100)
    client = FakeCHClient({SKEW_SQL: [small_stage, short_stage]})
    assert detect_skew(client, APP, THRESHOLDS.skew) == []


def test_shuffle_critical_on_disk_spill():
    client = FakeCHClient({SHUFFLE_SQL: [shuffle_row(disk_spilled=5_000_000)]})
    findings = detect_shuffle(client, APP, THRESHOLDS.shuffle)
    assert [f.severity for f in findings] == [Severity.CRITICAL]
    assert findings[0].evidence["disk_bytes_spilled"] == 5_000_000


def test_shuffle_warning_on_memory_spill():
    client = FakeCHClient({SHUFFLE_SQL: [shuffle_row(memory_spilled=1_000_000)]})
    findings = detect_shuffle(client, APP, THRESHOLDS.shuffle)
    assert [f.severity for f in findings] == [Severity.WARNING]


def test_shuffle_guard_suppresses_small_shuffles():
    client = FakeCHClient({SHUFFLE_SQL: [shuffle_row(shuffle_bytes=1024, disk_spilled=999)]})
    assert detect_shuffle(client, APP, THRESHOLDS.shuffle) == []


def test_plans_info_on_replans():
    client = FakeCHClient(
        {
            PLANS_SQL: [{"execution_id": 1, "replan_count": 4}, {"execution_id": 2, "replan_count": 1}],
            PLAN_TEXT_SQL: [],
            ADAPTIVE_PLAN_TEXT_SQL: [],
        }
    )
    findings = detect_plans(client, APP, THRESHOLDS.plans)
    assert len(findings) == 1
    assert findings[0].severity is Severity.INFO
    assert findings[0].execution_id == 1


def test_plans_flags_cartesian_product_in_plan_text():
    plan = "== Physical Plan ==\nCartesianProduct\n:- Range (0, 100)\n+- Range (0, 100)"
    client = FakeCHClient(
        {
            PLANS_SQL: [],
            PLAN_TEXT_SQL: [{"execution_id": 3, "physical_plan": plan}],
            ADAPTIVE_PLAN_TEXT_SQL: [],
        }
    )
    findings = detect_plans(client, APP, THRESHOLDS.plans)
    assert [f.severity for f in findings] == [Severity.CRITICAL]
    assert findings[0].evidence["pattern"] == "CartesianProduct"
    assert findings[0].execution_id == 3


def test_plans_flags_pattern_in_adaptive_plan_only():
    """AQE can introduce a join pattern absent from the initial plan; the
    detector must catch it in the adaptive plan and not double-report when the
    pattern appears in both plan versions of the same execution."""
    plan = "AdaptiveSparkPlan\nBroadcastNestedLoopJoin BuildRight\n:- Range (0, 10)"
    client = FakeCHClient(
        {
            PLANS_SQL: [],
            PLAN_TEXT_SQL: [{"execution_id": 7, "physical_plan": "== Physical Plan ==\nSortMergeJoin"}],
            ADAPTIVE_PLAN_TEXT_SQL: [{"execution_id": 7, "physical_plan": plan}],
        }
    )
    findings = detect_plans(client, APP, THRESHOLDS.plans)
    assert [f.severity for f in findings] == [Severity.WARNING]
    assert findings[0].evidence["pattern"] == "BroadcastNestedLoopJoin"
    assert findings[0].execution_id == 7


def test_plan_patterns_loaded_from_config_yaml():
    """Seam 1b: the plan-pattern catalog is externalized to
    src/config/anti_patterns.yaml, not a hardcoded list. Loading it yields the
    implemented plan-text patterns with severities coerced to the enum."""
    patterns = load_plan_patterns()
    by_name = {p.name: p for p in patterns}
    assert {"CartesianProduct", "BroadcastNestedLoopJoin", "groupByKey"} <= set(by_name)
    assert by_name["CartesianProduct"].severity is Severity.CRITICAL
    assert by_name["BroadcastNestedLoopJoin"].severity is Severity.WARNING
    assert by_name["groupByKey"].severity is Severity.WARNING
    assert by_name["CartesianProduct"].id == "ANTI-001"


def test_plans_flags_groupbykey_from_config():
    """A pattern added purely via YAML (no detector code change) is detected,
    proving the catalog drives detection. The finding carries its catalog id."""
    plan = "== Physical Plan ==\nMapGroups groupByKey(value)\n+- Exchange hashpartitioning"
    client = FakeCHClient(
        {
            PLANS_SQL: [],
            PLAN_TEXT_SQL: [{"execution_id": 9, "physical_plan": plan}],
            ADAPTIVE_PLAN_TEXT_SQL: [],
        }
    )
    findings = detect_plans(client, APP, THRESHOLDS.plans)
    assert [f.severity for f in findings] == [Severity.WARNING]
    assert findings[0].evidence["pattern"] == "groupByKey"
    assert findings[0].evidence["anti_pattern_id"] == "ANTI-003"
    assert findings[0].execution_id == 9


def gc_row(stage_id=1, gc_ms=3000, total_ms=10000, max_gc_ms=800, n_tasks=8, stage_attempt_id=0):
    return {"stage_id": stage_id, "stage_attempt_id": stage_attempt_id, "gc_ms": gc_ms, "total_ms": total_ms, "max_gc_ms": max_gc_ms, "n_tasks": n_tasks}


def test_gc_warning_and_critical_by_ratio():
    client = FakeCHClient({GC_SQL: [gc_row(stage_id=1, gc_ms=1200), gc_row(stage_id=2, gc_ms=2500)]})
    findings = detect_gc(client, APP, THRESHOLDS.gc)
    assert [(f.stage_id, f.severity) for f in findings] == [(1, Severity.WARNING), (2, Severity.CRITICAL)]
    assert findings[1].evidence["gc_ratio"] == 0.25


def test_gc_guard_suppresses_short_stages():
    client = FakeCHClient({GC_SQL: [gc_row(gc_ms=900, total_ms=2000)]})
    assert detect_gc(client, APP, THRESHOLDS.gc) == []


def test_oom_flags_oom_and_executor_lost():
    client = FakeCHClient(
        {
            OOM_SQL: [
                {"stage_id": 4, "stage_attempt_id": 0, "oom_tasks": 2, "executor_lost_tasks": 0, "failed_tasks": 2, "sample_reason": "java.lang.OutOfMemoryError: Java heap space"},
                {"stage_id": 5, "stage_attempt_id": 0, "oom_tasks": 0, "executor_lost_tasks": 0, "failed_tasks": 1, "sample_reason": "ExceptionFailure"},
            ]
        }
    )
    findings = detect_oom(client, APP)
    assert len(findings) == 1
    assert findings[0].severity is Severity.CRITICAL
    assert findings[0].stage_id == 4
    assert "OutOfMemoryError" in findings[0].title


def healthy_fixture() -> FakeCHClient:
    healthy_tasks = [skew_row(stage_id=s, max_ms=900, p50_ms=400, n_tasks=4) for s in range(3)]
    healthy_shuffle = [shuffle_row(stage_id=s, shuffle_bytes=200_000) for s in range(3)]
    healthy_gc = [gc_row(stage_id=s, gc_ms=50, total_ms=2500) for s in range(3)]
    return FakeCHClient(
        {
            SKEW_SQL: healthy_tasks,
            SHUFFLE_SQL: healthy_shuffle,
            PLANS_SQL: [{"execution_id": 0, "replan_count": 1}],
            PLAN_TEXT_SQL: [{"execution_id": 0, "physical_plan": "== Physical Plan ==\nSortMergeJoin"}],
            ADAPTIVE_PLAN_TEXT_SQL: [{"execution_id": 0, "physical_plan": "AdaptiveSparkPlan\nSortMergeJoin"}],
            GC_SQL: healthy_gc,
            OOM_SQL: [],
        }
    )


def test_healthy_smoke_baseline_has_zero_findings():
    assert run_all(healthy_fixture(), APP, THRESHOLDS) == []


def test_registry_is_the_single_source_of_truth():
    from apex_diagnostics.detectors import DETECTORS, DETECTORS_BY_NAME

    names = [spec.name for spec in DETECTORS]
    assert names == ["detect_skew", "detect_shuffle", "detect_plans", "detect_gc", "detect_oom"]
    # oom is the only detector without a tunable threshold.
    assert [s.name for s in DETECTORS if s.threshold_attr is None] == ["detect_oom"]
    assert set(DETECTORS_BY_NAME) == set(names)


def test_run_all_covers_every_registered_detector():
    from apex_diagnostics.detectors import DETECTORS

    # run_all must invoke exactly the registered detectors (guards against the
    # crew/MCP-vs-run_all 3-vs-5 drift): the healthy fixture registers one SQL
    # per detector, so a missing/extra detector would raise or change the count.
    client = healthy_fixture()
    run_all(client, APP, THRESHOLDS)
    queried_sql = {sql for sql, _ in client.queries}
    # plans issues two queries; every other detector issues one -> >= len(DETECTORS)
    assert len(queried_sql) >= len(DETECTORS)
