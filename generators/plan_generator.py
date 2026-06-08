#!/usr/bin/env python3
"""
Gerador de plano (v4) — sintetiza event log fiel ao Spark, sem executar.

Correcoes nesta versao:
- P1 #5: a distribuicao da task quente deixou de usar `single_task_shuffle_read_records`
  (que era o TOTAL e, sendo > rows, colapsava as cold tasks para 1-22 registros e
  inflava o ratio para 15392x). Agora deriva da carga real: a task quente recebe a
  parcela da hot key (rows * hot_share) e as cold tasks dividem o restante. Isso produz
  um ratio ~30x que BATE com o cluster real (29.5x).
- Validacao: falha cedo se hot_share produzir distribuicao impossivel.
- Proveniencia: insere ApexSyntheticProvenance como primeiro evento, com scenario_hash.
"""
import sys
import json
import time
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib

GENERATOR_VERSION = "4"


def synthesize_events(config, scenario_hash):
    sid = config["scenario_id"]
    code = config["code_generator"]
    sig = config["plan_generator"]["expected_signals"]
    line = code.get("anti_pattern_line", 0)
    rows = code["data"]["orders"]["rows"]
    hot_share = code["data"]["orders"]["hot_share"]
    parts = int(code["spark_config"]["spark.sql.shuffle.partitions"])
    stage = sig["hot_stage"]
    join_op = sig["join_operator"]

    if not (0 < hot_share < 1):
        raise ValueError(f"hot_share deve estar em (0,1), recebido {hot_share}")
    if parts < 2:
        raise ValueError(f"shuffle.partitions deve ser >= 2 para haver distribuicao, recebido {parts}")

    # [P1 #5] distribuicao derivada da carga real, nao de um total declarado.
    # A particao quente concentra a hot key; as frias dividem o restante.
    hot_records = int(rows * hot_share)            # ex: 200000 * 0.80 = 160000
    cold_total = rows - hot_records                # 40000
    cold_each = max(cold_total // (parts - 1), 1)  # ~5714 por particao fria
    if hot_records <= cold_each:
        raise ValueError(
            f"distribuicao impossivel: hot ({hot_records}) <= cold ({cold_each}). "
            f"Verifique hot_share e shuffle.partitions."
        )

    app_id = f"app-{int(time.time())}-0001"
    t0 = int(time.time() * 1000)

    events = [
        # Cadeia de custodia: primeiro evento carrega a assinatura do contrato.
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
        events.append({
            "Event": "SparkListenerTaskEnd", "Stage ID": stage, "Stage Attempt ID": 0,
            "Task Type": "ShuffleMapTask", "Task End Reason": {"Reason": "Success"},
            "Task Info": {"Task ID": tid, "Index": tid, "Attempt": 0,
                          "Launch Time": t0, "Finish Time": t0 + recs // 100, "Failed": False},
            "Task Metrics": {"Executor Run Time": recs // 100, "JVM GC Time": 0,
                             "Memory Bytes Spilled": 0,
                             "Shuffle Read Metrics": {"Total Records Read": recs,
                                                      "Remote Bytes Read": recs * 64,
                                                      "Fetch Wait Time": 0}},
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
