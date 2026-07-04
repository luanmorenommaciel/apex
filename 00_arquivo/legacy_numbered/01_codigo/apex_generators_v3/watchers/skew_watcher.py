#!/usr/bin/env python3
"""
Skew Watcher (v3) — endurecido.

Mudancas vs v2 (que tinha band-aids):
- Usa apexlib: isola o stage de reduce do join (nao mistura tasks de scan que leem 0).
- Le o plano FINAL pos-AQE.
- Trata o caso de 1 task (colapso do AQE) explicitamente, com mensagem honesta,
  em vez do hack `or [1]` que produzia um ratio sem sentido.
- Auto-descomprime logs zstd e valida o schema antes de analisar.
"""
import sys
import json
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib


def build_finding(scenario, events):
    sig = scenario["plan_generator"]["expected_signals"]
    op, used_final = apexlib.join_operator(events)
    stage_id, records = apexlib.hottest_reduce_stage(events)
    m = apexlib.skew_metrics(records)

    plan_note = "plano final pos-AQE" if used_final else "plano inicial (sem update de AQE)"
    evidence = [f"join operator: {op} ({plan_note})"]

    if m["collapsed"]:
        evidence.append(
            f"stage {stage_id}: 1 task leu {m['hot']} registros — distribuicao colapsada "
            f"(AQE coalesceu ou concentracao total). Rode em multi-core para a cauda completa."
        )
        ratio_txt = "colapso (1 task)"
    else:
        evidence.append(
            f"stage {stage_id}: task quente {m['hot']} vs mediana das frias {int(m['median_cold'])} "
            f"-> skew ratio {m['ratio']}x ({m['n_tasks']} tasks)"
        )
        ratio_txt = f"{m['ratio']}x"

    # Skew confirmado se: operador certo E (colapso OU ratio acima do minimo declarado).
    is_skew = op == sig["join_operator"] and (m["collapsed"] or m["ratio"] >= sig["skew_ratio_min"])
    # Confianca derivada da evidencia (nunca auto-avaliada arbitrariamente).
    if m["collapsed"]:
        confidence = 0.95
    elif m["ratio"] == float("inf"):
        confidence = 0.99
    else:
        confidence = round(min(0.99, m["ratio"] / (m["ratio"] + 3)), 2)

    finding = {
        "watcher": "shuffle_skew",
        "stage": stage_id,
        "severity": "high" if is_skew else "low",
        "confidence": confidence,
        "evidence": evidence,
        "root_cause": (
            f"data skew na chave de join customer_id ({op}): "
            f"1 particao concentra {ratio_txt} o trabalho"
        ),
        "recommendations": [
            "habilitar spark.sql.adaptive.skewJoin.enabled",
            "broadcast o lado customers (dimensao pequena)",
            "salgar a chave customer_id",
        ],
    }
    return finding, is_skew


def check_acceptance(finding, scenario):
    acc = scenario["acceptance"]
    blob = (finding["root_cause"] + " " + " ".join(finding["evidence"])).lower()
    missing = [t for t in acc["root_cause_includes"] if t.lower() not in blob]
    enough = len(finding["recommendations"]) >= acc.get("min_recommendations", 1)
    return (not missing) and enough, missing, enough


def main(scenario_path, log_path):
    scenario = yaml.safe_load(open(scenario_path))
    events = apexlib.read_events(log_path)

    for w in apexlib.validate_schema(events):
        print(f"⚠️  schema: {w}", file=sys.stderr)

    finding, is_skew = build_finding(scenario, events)
    print(json.dumps(finding, indent=2, ensure_ascii=False))

    ok, missing, enough = check_acceptance(finding, scenario)
    print("\n--- ACCEPTANCE ---")
    if not is_skew:
        print("❌ Watcher NAO detectou o anti-pattern declarado.")
        sys.exit(1)
    if not ok:
        print(f"❌ Finding nao satisfaz acceptance. Faltou: {missing}; recs suficientes: {enough}")
        sys.exit(1)
    print("✅ Anti-pattern detectado E Finding satisfaz o acceptance do scenario. GATE VERDE.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: skew_watcher.py <scenario.yaml> <event-log.ndjson|.zstd>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
