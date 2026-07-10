"""Testes do T1 deterministico (G4) — regras sobre stage/task metrics, sem LLM."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "v1-skeleton" / "analysis"))
import t1_triage  # noqa: E402


def stage(sid=4, **kw):
    base = dict(stage_id=sid, num_tasks=8, failed_tasks=0, duration_ms=20000,
                input_bytes=0, shuffle_read=0, shuffle_write=0,
                memory_spill=0, disk_spill=0, gc_time_ms=0)
    base.update(kw)
    return base


def test_healthy_stage_no_findings():
    assert t1_triage.triage_rows([stage()], {4: [100, 110, 105, 98, 102, 99, 104, 101]}) == []


def test_skew_by_task_duration():
    f = t1_triage.triage_rows([stage()], {4: [5000, 100, 110, 105, 98, 102, 99, 104]})
    assert f and f[0]["pattern"] == "skew" and f[0]["confidence"] >= 0.6
    assert f[0]["bottleneck_stage_id"] == 4


def test_spill_critical_on_disk():
    f = t1_triage.triage_rows([stage(shuffle_read=400 * 2**20, disk_spill=50 * 2**20)])
    assert f and f[0]["pattern"] == "spill" and f[0]["severity"] == "critical"


def test_gc_pressure():
    f = t1_triage.triage_rows([stage(duration_ms=20000, gc_time_ms=5000)])
    assert f and f[0]["pattern"] == "gc_pressure" and f[0]["confidence"] >= 0.6


def test_oom_on_failed_tasks():
    f = t1_triage.triage_rows([stage(failed_tasks=2)])
    assert f and f[0]["pattern"] == "oom" and f[0]["severity"] == "critical"


def test_parallelism_collapse():
    f = t1_triage.triage_rows([stage(num_tasks=2, input_bytes=2 * 2**30)])
    assert f and f[0]["pattern"] == "parallelism_collapse"


def test_small_shuffle_never_spill_alert():
    # guard de 16 MiB: shuffle pequeno com spill nao alerta (falso positivo comum)
    f = t1_triage.triage_rows([stage(shuffle_read=1 * 2**20, memory_spill=1024)])
    assert f == []


def test_t1_is_fast():
    rows = [stage(sid=i) for i in range(200)]
    tasks = {i: [100 + j for j in range(64)] for i in range(200)}
    t0 = time.perf_counter()
    t1_triage.triage_rows(rows, tasks)
    assert (time.perf_counter() - t0) < 1.0  # criterio G4: < 1s sem LLM
