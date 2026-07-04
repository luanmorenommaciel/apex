"""
Suite de testes do slice do Apex. Cada teste fixa um comportamento que antes era
band-aid ou nao era coberto. Roda sem Spark — usa fixtures de event log deterministicas.
"""
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from apex import apexlib


# ---------- helpers de fixture ----------
def task_end(stage, tid, records):
    return {"Event": "SparkListenerTaskEnd", "Stage ID": stage,
            "Task Info": {"Task ID": tid},
            "Task Metrics": {"Shuffle Read Metrics": {"Total Records Read": records}}}


def sql_start(plan):
    return {"Event": "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart",
            "physicalPlanDescription": plan}


def aqe_update(plan):
    return {"Event": "org.apache.spark.sql.execution.ui.SparkListenerSQLAdaptiveExecutionUpdate",
            "physicalPlanDescription": plan}


def write_ndjson(tmp_path, name, events):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(e) for e in events))
    return str(p)


# ---------- leitura resiliente ----------
def test_reader_tolerates_blank_and_corrupt_lines(tmp_path):
    p = tmp_path / "log.ndjson"
    p.write_text('{"Event":"A"}\n\n{linha corrompida}\n{"Event":"B"}\n')
    events = apexlib.read_events(str(p))
    assert [e["Event"] for e in events] == ["A", "B"]


def test_reader_autodecompress_zstd(tmp_path):
    zstd = pytest.importorskip("zstandard")
    raw = b'{"Event":"SparkListenerTaskEnd","Stage ID":1,"Task Info":{"Task ID":0},' \
          b'"Task Metrics":{"Shuffle Read Metrics":{"Total Records Read":42}}}\n'
    comp = zstd.ZstdCompressor().compress(raw)
    p = tmp_path / "log.zstd"
    p.write_bytes(comp)
    events = apexlib.read_events(str(p))
    assert events[0]["Task Metrics"]["Shuffle Read Metrics"]["Total Records Read"] == 42


# ---------- plano final pos-AQE ----------
def test_join_operator_prefers_final_plan():
    events = [sql_start("== Physical Plan ==\nSortMergeJoin ..."),
              aqe_update("== Physical Plan ==\nBroadcastHashJoin ...")]
    op, used_final = apexlib.join_operator(events)
    assert op == "BroadcastHashJoin"   # o plano FINAL venceu, nao o inicial
    assert used_final is True


def test_join_operator_falls_back_to_initial():
    events = [sql_start("== Physical Plan ==\nSortMergeJoin ...")]
    op, used_final = apexlib.join_operator(events)
    assert op == "SortMergeJoin"
    assert used_final is False


# ---------- isolamento do stage de reduce ----------
def test_hottest_stage_ignores_scan_tasks():
    events = [task_end(0, 0, 0), task_end(0, 1, 0),       # scan: 0 shuffle read
              task_end(4, 0, 160000), task_end(4, 1, 5000), task_end(4, 2, 5200)]  # reduce
    sid, records = apexlib.hottest_reduce_stage(events)
    assert sid == 4
    assert records[0] == 160000


# ---------- metricas de skew ----------
def test_skew_metrics_spread():
    m = apexlib.skew_metrics([160000, 5000, 5200, 5100])
    assert m["collapsed"] is False
    assert m["ratio"] > 10
    assert m["n_tasks"] == 4


def test_skew_metrics_single_task_is_collapse_not_crash():
    m = apexlib.skew_metrics([200100])   # antes: divisao por zero / hack [1]
    assert m["collapsed"] is True
    assert m["n_tasks"] == 1
    assert m["hot"] == 200100            # nao quebra, sinaliza colapso


def test_skew_metrics_balanced_is_not_skew():
    m = apexlib.skew_metrics([5000, 5100, 4900, 5050])
    assert m["ratio"] < 2               # distribuicao equilibrada -> ratio baixo


# ---------- watcher end-to-end ----------
SCENARIO = str(ROOT / "scenarios" / "skew_on_join_30x.yaml")


def run(script, *args):
    return subprocess.run([sys.executable, str(ROOT / script), *args],
                          capture_output=True, text=True)


def test_watcher_detects_spread(tmp_path):
    events = [sql_start("SortMergeJoin"),
              *[task_end(4, i, 200100 if i == 0 else 5700 + i) for i in range(8)]]
    log = write_ndjson(tmp_path, "spread.ndjson", events)
    r = run("watchers/skew_watcher.py", SCENARIO, log)
    assert "GATE VERDE" in r.stdout, r.stdout + r.stderr


def test_watcher_detects_real_collapse(tmp_path):
    # reproduz o log real do plat-v0 1-core: 1 task quente, resto 0
    events = [sql_start("SortMergeJoin"),
              task_end(0, 0, 0), task_end(1, 0, 0),
              task_end(4, 0, 200100)]
    log = write_ndjson(tmp_path, "collapse.ndjson", events)
    r = run("watchers/skew_watcher.py", SCENARIO, log)
    assert "GATE VERDE" in r.stdout, r.stdout + r.stderr
    assert "colapsada" in r.stdout    # reporta o colapso honestamente


def test_watcher_no_false_positive_on_balanced(tmp_path):
    events = [sql_start("SortMergeJoin"),
              *[task_end(4, i, 5000 + i) for i in range(8)]]   # sem cauda
    log = write_ndjson(tmp_path, "balanced.ndjson", events)
    r = run("watchers/skew_watcher.py", SCENARIO, log)
    assert r.returncode != 0          # nao deve gritar skew onde nao ha


# ---------- oraculo ----------
def test_oracle_passes_on_collapse_with_warning(tmp_path):
    syn = write_ndjson(tmp_path, "syn.ndjson",
                       [sql_start("SortMergeJoin"),
                        *[task_end(4, i, 200100 if i == 0 else 5700) for i in range(8)]])
    real = write_ndjson(tmp_path, "real.ndjson",
                        [sql_start("SortMergeJoin"), task_end(4, 0, 200100)])
    r = run("oracle/compare.py", SCENARIO, syn, real)
    assert "Fidelidade OK" in r.stdout, r.stdout + r.stderr
    assert "colapsou" in r.stdout      # avisa, nao finge


def test_oracle_catches_join_mismatch(tmp_path):
    syn = write_ndjson(tmp_path, "syn.ndjson",
                       [sql_start("SortMergeJoin"), task_end(4, 0, 200100), task_end(4, 1, 5000)])
    real = write_ndjson(tmp_path, "real.ndjson",
                        [sql_start("BroadcastHashJoin"), task_end(4, 0, 200100), task_end(4, 1, 5000)])
    r = run("oracle/compare.py", SCENARIO, syn, real)
    assert r.returncode != 0
    assert "join operator divergiu" in r.stdout
