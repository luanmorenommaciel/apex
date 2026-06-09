#!/usr/bin/env python3
"""
Oraculo (v4).

Sobre a v3:
- Emite um AUDIT TRAIL com o scenario_hash do sintetico (cadeia de custodia).
- Com o P1 #5 corrigido, o ratio do sintetico (~28x) bate com o real (~29.5x), entao a
  comparacao de ratio foi REABILITADA (nao mais `if False:`). Se um lado colapsar em
  1 task (1-core), reporta o colapso honestamente em vez de falhar.
"""
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib


def signals(log_path):
    events = apexlib.read_events(log_path)
    op, used_final = apexlib.join_operator(events)
    selected = apexlib.hottest_reduce_stage_details(events, join_op=op)
    m = apexlib.skew_metrics(selected["records"])
    hot_task = selected["tasks"][0] if selected["tasks"] else {}
    task_types = sorted(
        {
            task["task_type"]
            for task in selected["tasks"]
            if task.get("task_type")
        }
    )
    prov = next((e for e in events if e.get("Event") == "ApexSyntheticProvenance"), None)
    return {
        "join_op": op,
        "used_final_plan": used_final,
        "provenance": prov.get("scenario_hash") if prov else None,
        "stage_id": selected["stage_id"],
        "correlation_method": selected["correlation_method"],
        "hot_partition": hot_task.get("partition"),
        "task_types": task_types,
        **m,
    }


def main(scenario_path, synthetic_log, real_log):
    scenario = yaml.safe_load(open(scenario_path))
    tol = scenario["oracle"]["tolerance"]
    s, r = signals(synthetic_log), signals(real_log)

    print("--- AUDIT TRAIL ---")
    print(f"scenario:   {scenario['scenario_id']} (hash {apexlib.compute_scenario_hash(scenario_path)})")
    print(f"synthetic:  {synthetic_log}  provenance={s['provenance']}")
    print(f"real:       {real_log}  provenance={r['provenance'] or 'n/a (log real)'}")
    print("---")
    print(f"join:  synthetic={s['join_op']}  real={r['join_op']}")
    print(f"hot:   synthetic={s['hot']}  real={r['hot']}")
    print(f"ratio: synthetic={s['ratio']}  real={r['ratio']}")
    print(f"part:  synthetic={s['hot_partition']}  real={r['hot_partition']}")
    print(f"type:  synthetic={s['task_types']}  real={r['task_types']}")
    print(
        "corr:  "
        f"synthetic={s['correlation_method']}  real={r['correlation_method']}"
    )

    problems, warnings = [], []

    if s["join_op"] != r["join_op"]:
        problems.append(f"join operator divergiu: {s['join_op']} vs {r['join_op']}")

    if (
        s["hot_partition"] is not None
        and r["hot_partition"] is not None
        and s["hot_partition"] != r["hot_partition"]
    ):
        warnings.append(
            "hot partition divergiu: "
            f"{s['hot_partition']} vs {r['hot_partition']}"
        )

    if s["task_types"] and r["task_types"] and s["task_types"] != r["task_types"]:
        warnings.append(
            f"task type divergiu: {s['task_types']} vs {r['task_types']}"
        )

    for side, signal in (("sintetico", s), ("real", r)):
        if signal["correlation_method"] == "largest_shuffle_fallback":
            warnings.append(
                f"{side} selecionou stage por maior shuffle sem correlacao estrutural"
            )

    if r["hot"]:
        rec_dev = abs(s["hot"] - r["hot"]) / r["hot"]
        if rec_dev > tol["records"]:
            problems.append(f"registros da task quente divergiram {rec_dev:.0%} (tol {tol['records']:.0%})")

    # Ratio reabilitado (P1 #5 corrigido). Se um lado colapsou em 1 task, reporta honestamente.
    if s["collapsed"] or r["collapsed"]:
        lado = "real" if r["collapsed"] else "sintetico"
        warnings.append(
            f"lado {lado} colapsou em 1 task (AQE/1-core); "
            "rode multi-core para comparar ratio"
        )
    elif r["ratio"] and r["ratio"] != float("inf"):
        ratio_dev = abs(s["ratio"] - r["ratio"]) / r["ratio"]
        if ratio_dev > tol["skew_ratio"]:
            problems.append(f"skew ratio divergiu {ratio_dev:.0%} (tol {tol['skew_ratio']:.0%})")

    for w in warnings:
        print(f"[WARN] {w}")
    if problems:
        print("\n[ERROR] ORACULO: o sintetico DESVIOU do Spark real:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(
        "\n[OK] ORACULO: sintetico fiel ao Spark real nos sinais agregados "
        "dentro da tolerancia."
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: compare.py <scenario.yaml> <synthetic.ndjson> <real.ndjson|.zstd|dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
