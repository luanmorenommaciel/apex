#!/usr/bin/env python3
"""
Gerador de plano (v4) — sintetiza event log fiel ao Spark, sem executar.

Correcao central: distribuicao derivada de rows * hot_share, nao de single_task_shuffle_read_records.
Ratio ~27.9x (real 29.5x). NUNCA 15392x.
[G1] baseline (anti_pattern.class: none) — distribuicao uniforme.
[G2] sinais por classe: gc_ratio, spill, oom_failed_tasks, plano cartesiano (ISSUE-A01).
"""
import sys
import json
import time
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib

GENERATOR_VERSION = "4"

SKEW_CLASSES = {"data_skew_on_join_key"}


def synthesize_events(config, scenario_hash):
    sid = config["scenario_id"]
    code = config["code_generator"]
    sig = config["plan_generator"]["expected_signals"]
    line = code.get("anti_pattern_line", 0)
    rows = code["data"]["orders"]["rows"]
    hot_share = code["data"]["orders"].get("hot_share") or 0.0
    parts = int(code["spark_config"]["spark.sql.shuffle.partitions"])
    stage = sig.get("hot_stage") or 4
    join_op = sig["join_operator"]
    klass = config.get("anti_pattern", {}).get("class", "none")
    skewed = klass in SKEW_CLASSES

    if parts < 2:
        raise ValueError(f"shuffle.partitions deve ser >= 2, recebido {parts}")

    if skewed:
        if not (0 < hot_share < 1):
            raise ValueError(f"hot_share deve estar em (0,1), recebido {hot_share}")
        hot_records = int(rows * hot_share)
        cold_total = rows - hot_records
        cold_each = max(cold_total // (parts - 1), 1)
        if hot_records <= cold_each:
            raise ValueError(
                f"distribuicao impossivel: hot ({hot_records}) <= cold ({cold_each}). "
                f"Verifique hot_share e shuffle.partitions."
            )
    else:
        # [G1/G2] distribuicao uniforme com jitter leve — nao dispara o skew watcher
        if hot_share:
            raise ValueError(f"scenario '{klass}' nao-skew nao pode ter hot_share > 0, recebido {hot_share}")
        hot_records = cold_each = rows // parts

    # [G2] sinais injetaveis por classe (defaults inertes p/ skew e baseline)
    task_run_ms = sig.get("task_run_time_ms")          # forca duracao por task
    gc_ratio = sig.get("gc_ratio", 0.0)                # fracao do run time em GC
    shuffle_bpt = sig.get("shuffle_bytes_per_task")    # bytes de shuffle por task
    mem_spill = sig.get("memory_spill_bytes_per_task", 0)
    disk_spill = sig.get("disk_spill_bytes_per_task", 0)
    oom_failed = sig.get("oom_failed_tasks", 0)        # tasks extras mortas por OOM

    app_id = f"app-{int(time.time())}-0001"
    t0 = int(time.time() * 1000)

    events = [
        {"Event": "ApexSyntheticProvenance", "scenario_id": sid,
         "scenario_hash": scenario_hash, "generator_version": GENERATOR_VERSION,
         "generated_at": t0},
        {"Event": "SparkListenerApplicationStart", "App Name": sid, "App ID": app_id,
         "Timestamp": t0, "User": "apex"},
        {"Event": "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart",
         "executionId": 1, "description": f"save at job.py:{line}",
         "physicalPlanDescription":
             f"== Physical Plan ==\n*(5) {join_op} [customer_id], [customer_id], Inner\n"
             f":- Exchange hashpartitioning(customer_id, {parts})\n"
             f"+- Exchange hashpartitioning(customer_id, {parts})",
         "time": t0},
        {"Event": "SparkListenerStageSubmitted",
         "Stage Info": {"Stage ID": stage, "Stage Name": f"{join_op} at job.py:{line}",
                        "Number of Tasks": parts}},
    ]
    for tid in range(parts):
        recs = hot_records if tid == 0 else cold_each + (tid * 3)
        run_ms = task_run_ms if task_run_ms else recs // 100
        events.append({
            "Event": "SparkListenerTaskEnd", "Stage ID": stage, "Stage Attempt ID": 0,
            "Task Type": "ShuffleMapTask", "Task End Reason": {"Reason": "Success"},
            "Task Info": {"Task ID": tid, "Index": tid, "Attempt": 0,
                          "Launch Time": t0, "Finish Time": t0 + run_ms, "Failed": False},
            "Task Metrics": {"Executor Run Time": run_ms,
                             "JVM GC Time": int(run_ms * gc_ratio),
                             "Memory Bytes Spilled": mem_spill,
                             "Disk Bytes Spilled": disk_spill,
                             "Shuffle Read Metrics": {
                                 "Total Records Read": recs,
                                 "Remote Bytes Read": shuffle_bpt if shuffle_bpt else recs * 64,
                                 "Fetch Wait Time": 0}},
        })
    for i in range(oom_failed):
        events.append({
            "Event": "SparkListenerTaskEnd", "Stage ID": stage, "Stage Attempt ID": 0,
            "Task Type": "ShuffleMapTask",
            "Task End Reason": {"Reason": "ExceptionFailure",
                                "Class Name": "java.lang.OutOfMemoryError",
                                "Description": "Java heap space",
                                "Full Stack Trace": "java.lang.OutOfMemoryError: Java heap space"},
            "Task Info": {"Task ID": parts + i, "Index": parts + i, "Attempt": 0,
                          "Launch Time": t0, "Finish Time": t0 + 500, "Failed": True},
            "Task Metrics": {},
        })
    events.append({"Event": "SparkListenerStageCompleted",
                   "Stage Info": {"Stage ID": stage, "Number of Tasks": parts,
                                  "Completion Time": t0 + 2000}})
    events.append({"Event": "SparkListenerApplicationEnd", "Timestamp": t0 + 2500})
    return events


def generate_plan(scenario_path, output_path):
    config = yaml.safe_load(open(scenario_path))
    scenario_hash = apexlib.compute_scenario_hash(scenario_path)
    events = synthesize_events(config, scenario_hash)
    with open(output_path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    print(f"✅ {output_path} gerado: {len(events)} eventos, scenario_hash {scenario_hash} embutido.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: plan_generator.py <scenario.yaml> <output.ndjson>")
        sys.exit(1)
    generate_plan(sys.argv[1], sys.argv[2])
