"""
Suite de testes do slice Apex v4. Cada teste fixa um comportamento corrigido.
Roda sem Spark — fixtures deterministicas.
"""
import io
import os
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from apex import apexlib

SCENARIO = str(ROOT / "scenarios" / "skew_on_join_30x.yaml")


# ---------- fixtures helpers ----------
def task_end(stage, tid, records):
    return {"Event": "SparkListenerTaskEnd", "Stage ID": stage,
            "Task Info": {"Task ID": tid},
            "Task Metrics": {"Shuffle Read Metrics": {"Total Records Read": records}}}


def stage_submitted(stage, name):
    return {"Event": "SparkListenerStageSubmitted",
            "Stage Info": {"Stage ID": stage, "Stage Name": name}}


def sql_start(plan, exec_id=1):
    return {"Event": "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart",
            "executionId": exec_id, "physicalPlanDescription": plan}


def aqe_update(plan, exec_id=1):
    return {"Event": "org.apache.spark.sql.execution.ui.SparkListenerSQLAdaptiveExecutionUpdate",
            "executionId": exec_id, "physicalPlanDescription": plan}


def write_ndjson(tmp_path, name, events):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(e) for e in events))
    return str(p)


def run(script, *args):
    return subprocess.run([sys.executable, str(ROOT / script), *args],
                          capture_output=True, text=True)


# ---------- P0 #1: streaming zstd ----------
def test_reader_autodecompress_zstd_streaming(tmp_path):
    zstd = pytest.importorskip("zstandard")
    raw = ('{"Event":"SparkListenerTaskEnd","Stage ID":4,"Task Info":{"Task ID":0},'
           '"Task Metrics":{"Shuffle Read Metrics":{"Total Records Read":160000}}}\n').encode()
    p = tmp_path / "log.zstd"
    p.write_bytes(zstd.ZstdCompressor().compress(raw))
    events = apexlib.read_events(str(p))
    assert events[0]["Task Metrics"]["Shuffle Read Metrics"]["Total Records Read"] == 160000


def test_iter_events_is_lazy(tmp_path):
    # iter_events deve ser um gerador (streaming), nao materializar tudo de cara
    p = write_ndjson(tmp_path, "log.ndjson", [task_end(4, 0, 100)])
    gen = apexlib.iter_events(p)
    assert hasattr(gen, "__next__")  # e um iterador


# ---------- P0 #3: leitura de diretorio (rolling logs) ----------
def test_reads_rolling_log_directory(tmp_path):
    d = tmp_path / "eventlog_dir"
    d.mkdir()
    (d / "events_1_app").write_text(json.dumps(task_end(4, 0, 160000)))
    (d / "events_2_app").write_text(json.dumps(task_end(4, 1, 5000)))
    (d / "events_10_app").write_text(json.dumps(task_end(4, 2, 5200)))
    events = apexlib.read_events(str(d))
    recs = [e["Task Metrics"]["Shuffle Read Metrics"]["Total Records Read"] for e in events]
    assert sorted(recs) == [5000, 5200, 160000]  # leu os 3 arquivos


def test_rolling_sort_is_numeric_not_lexical():
    # events_10 deve vir DEPOIS de events_2 (ordem numerica)
    assert apexlib._rolling_sort_key("events_2_app") < apexlib._rolling_sort_key("events_10_app")


# ---------- P0 #2: isolamento do stage do join ----------
def test_hottest_stage_prefers_join_named_stage():
    # Um sort lê MAIS shuffle que o join — sem cross-ref pegaria o sort (errado).
    events = [
        stage_submitted(3, "Sort at job.py:10"),
        stage_submitted(4, "SortMergeJoin at job.py:20"),
        task_end(3, 0, 500000), task_end(3, 1, 400000),   # sort: volume maior
        task_end(4, 0, 160000), task_end(4, 1, 5000),     # join: o que queremos
    ]
    sid, records = apexlib.hottest_reduce_stage(events, join_op="SortMergeJoin")
    assert sid == 4  # escolheu o stage do JOIN, nao o sort de maior volume


def test_hottest_stage_fallback_without_join_op():
    events = [task_end(4, 0, 160000), task_end(4, 1, 5000)]
    sid, records = apexlib.hottest_reduce_stage(events)
    assert sid == 4


# ---------- P1 #6: associacao por executionId ----------
def test_join_operator_prefers_final_plan():
    events = [sql_start("SortMergeJoin ...", 1), aqe_update("BroadcastHashJoin ...", 1)]
    op, used_final = apexlib.join_operator(events)
    assert op == "BroadcastHashJoin" and used_final is True


def test_join_operator_finds_join_across_executions():
    # exec 2 tem um update sem join (so um filtro); exec 1 tem o join. Deve achar o join.
    events = [
        sql_start("Filter + Scan", 2),
        aqe_update("Filter + Scan no join here", 2),
        sql_start("SortMergeJoin [k]", 1),
        aqe_update("SortMergeJoin [k] final", 1),
    ]
    op, _ = apexlib.join_operator(events)
    assert op == "SortMergeJoin"


# ---------- P1 #5: distribuicao correta (ratio ~30x, nao 15392x) ----------
def test_plan_generator_ratio_is_realistic(tmp_path):
    out = str(tmp_path / "syn.ndjson")
    r = run("generators/plan_generator.py", SCENARIO, out)
    assert r.returncode == 0, r.stdout + r.stderr
    events = apexlib.read_events(out)
    _, records = apexlib.hottest_reduce_stage(events, join_op="SortMergeJoin")
    m = apexlib.skew_metrics(records)
    # 200000*0.8=160000 hot; 40000/7~5714 cold -> ratio ~28x. NUNCA 15392x.
    assert 20 <= m["ratio"] <= 40, f"ratio fora do esperado: {m['ratio']}"


def test_skew_metrics_single_task_collapse():
    m = apexlib.skew_metrics([200100])
    assert m["collapsed"] is True and m["n_tasks"] == 1


# ---------- cadeia de custodia (scenario_hash) ----------
def test_scenario_hash_is_deterministic():
    h1 = apexlib.compute_scenario_hash(SCENARIO)
    h2 = apexlib.compute_scenario_hash(SCENARIO)
    assert h1 == h2 and h1.startswith("sha256:")


def test_code_and_plan_emit_same_hash(tmp_path):
    job = str(tmp_path / "job.py")
    syn = str(tmp_path / "syn.ndjson")
    run("generators/code_generator.py", SCENARIO, job)
    run("generators/plan_generator.py", SCENARIO, syn)
    manifest = json.load(open(str(tmp_path / "job.meta.json")))
    first_event = json.loads(open(syn).readline())
    assert manifest["scenario_hash"] == first_event["scenario_hash"]
    assert manifest["generator_version"] == "4"  # corrige o "3" da v4 spec


def test_provenance_passes_when_hash_matches(tmp_path):
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", SCENARIO, syn)
    events = apexlib.read_events(syn)
    # nao deve levantar
    h = apexlib.validate_provenance(events, SCENARIO)
    assert h is not None


def test_provenance_error_on_stale_artifact(tmp_path):
    # gera com um scenario, depois altera o scenario -> deve dar PROVENANCE ERROR
    scen = tmp_path / "scen.yaml"
    scen.write_text(Path(SCENARIO).read_text())
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", str(scen), syn)
    scen.write_text(scen.read_text() + "\n# mudanca que invalida o log\n")
    events = apexlib.read_events(syn)
    with pytest.raises(ValueError, match="PROVENANCE ERROR"):
        apexlib.validate_provenance(events, str(scen))


def test_real_log_without_provenance_passes(tmp_path):
    # log real nao tem ApexSyntheticProvenance -> validacao ignora, nao falha
    real = write_ndjson(tmp_path, "real.ndjson", [task_end(4, 0, 160000), task_end(4, 1, 5000)])
    events = apexlib.read_events(real)
    assert apexlib.validate_provenance(events, SCENARIO) is None


# ---------- watcher end-to-end ----------
def test_watcher_green_on_synthetic(tmp_path):
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", SCENARIO, syn)
    r = run("watchers/skew_watcher.py", SCENARIO, syn)
    assert "GATE VERDE" in r.stdout, r.stdout + r.stderr
    assert "customer_id = 7" in r.stdout  # P1 #7: hot_key no root_cause


def test_watcher_rejects_stale_log(tmp_path):
    scen = tmp_path / "scen.yaml"
    scen.write_text(Path(SCENARIO).read_text())
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", str(scen), syn)
    scen.write_text(scen.read_text() + "\n# stale\n")
    r = run("watchers/skew_watcher.py", str(scen), syn)
    assert r.returncode == 2 and "PROVENANCE ERROR" in r.stdout


def test_watcher_detects_real_collapse(tmp_path):
    real = write_ndjson(tmp_path, "real.ndjson",
                        [sql_start("SortMergeJoin"), task_end(0, 0, 0), task_end(4, 0, 200100)])
    r = run("watchers/skew_watcher.py", SCENARIO, real)
    assert "GATE VERDE" in r.stdout and "colapsada" in r.stdout


# ---------- oracle ----------
def test_oracle_passes_synthetic_vs_realistic_real(tmp_path):
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", SCENARIO, syn)
    # real "saudavel" multi-core: hot 160000, cold ~5400 -> ratio ~29.6x (perto do sintetico)
    real = write_ndjson(tmp_path, "real.ndjson",
                        [sql_start("SortMergeJoin"),
                         *[task_end(4, i, 160000 if i == 0 else 5400 + i*10) for i in range(8)]])
    r = run("oracle/compare.py", SCENARIO, syn, real)
    assert "fiel ao Spark real" in r.stdout, r.stdout + r.stderr


def test_oracle_warns_on_real_collapse(tmp_path):
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", SCENARIO, syn)
    real = write_ndjson(tmp_path, "real.ndjson", [sql_start("SortMergeJoin"), task_end(4, 0, 200100)])
    r = run("oracle/compare.py", SCENARIO, syn, real)
    assert "colapsou" in r.stdout and "fiel ao Spark real" in r.stdout


def test_oracle_catches_join_mismatch(tmp_path):
    syn = str(tmp_path / "syn.ndjson")
    run("generators/plan_generator.py", SCENARIO, syn)
    real = write_ndjson(tmp_path, "real.ndjson",
                        [sql_start("BroadcastHashJoin"),
                         *[task_end(4, i, 160000 if i == 0 else 5400) for i in range(8)]])
    r = run("oracle/compare.py", SCENARIO, syn, real)
    assert r.returncode != 0 and "join operator divergiu" in r.stdout
