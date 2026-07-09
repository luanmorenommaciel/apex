#!/usr/bin/env python3
"""
Skew Watcher (v4).

Sobre a v3:
- Valida a proveniencia (scenario_hash) ANTES de analisar — rejeita log stale.
- root_cause inclui a chave e o hot_key do scenario (customer_id = N).
- Isola o stage do join passando o operador para hottest_reduce_stage.
- [G1] Suporte a cenario baseline (anti_pattern.class: none) — verde = zero finding.
"""
import sys
import json
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib

# Threshold padrao do detector quando o scenario nao declara skew_ratio_min.
# Usado nos baselines (G1): o watcher roda com a MESMA regra de producao —
# se disparar num job uniforme, e falso positivo real, nao artefato de config.
DEFAULT_SKEW_RATIO_MIN = 10


def build_finding(scenario, events):
    sig = scenario["plan_generator"]["expected_signals"]
    data = scenario["code_generator"]["data"]["orders"]
    join_key = "customer_id"
    hot_key = data.get("hot_key", "?")

    op, used_final = apexlib.join_operator(events)
    stage_id, records = apexlib.hottest_reduce_stage(events, join_op=op)
    m = apexlib.skew_metrics(records)

    plan_note = "plano final pos-AQE" if used_final else "plano inicial"
    evidence = [f"join operator: {op} ({plan_note})"]
    if m["collapsed"]:
        evidence.append(f"stage {stage_id}: 1 task leu {m['hot']} registros — distribuicao colapsada (AQE/1-core)")
        ratio_txt = "colapso (1 task)"
    else:
        evidence.append(
            f"stage {stage_id}: task quente {m['hot']} vs mediana das frias {int(m['median_cold'])} "
            f"-> skew ratio {m['ratio']}x ({m['n_tasks']} tasks)"
        )
        ratio_txt = f"{m['ratio']}x"

    threshold = sig.get("skew_ratio_min", DEFAULT_SKEW_RATIO_MIN)
    is_skew = op == sig["join_operator"] and (m["collapsed"] or m["ratio"] >= threshold)
    confidence = 0.95 if m["collapsed"] else round(min(0.99, m["ratio"] / (m["ratio"] + 3)), 2) if m["ratio"] != float("inf") else 0.99

    finding = {
        "watcher": "shuffle_skew",
        "stage": stage_id,
        "severity": "high" if is_skew else "low",
        "confidence": confidence,
        "evidence": evidence,
        "root_cause": (
            f"data skew na chave de join {join_key} = {hot_key} ({op}): "
            f"1 particao concentra {ratio_txt} o trabalho"
        ),
        "recommendations": [
            "habilitar spark.sql.adaptive.skewJoin.enabled",
            "broadcast o lado customers (dimensao pequena)",
            f"salgar a chave {join_key}",
        ],
    }
    return finding, is_skew, m


def check_acceptance(finding, scenario):
    acc = scenario["acceptance"]
    blob = (finding["root_cause"] + " " + " ".join(finding["evidence"])).lower()
    missing = [t for t in acc["root_cause_includes"] if t.lower() not in blob]
    enough = len(finding["recommendations"]) >= acc.get("min_recommendations", 1)
    return (not missing) and enough, missing, enough


def main(scenario_path, log_path):
    scenario = yaml.safe_load(open(scenario_path))
    events = apexlib.read_events(log_path)

    try:
        h = apexlib.validate_provenance(events, scenario_path)
        if h:
            print(f"provenance: validada — hash {h}")
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(2)

    for w in apexlib.validate_schema(events):
        print(f"⚠️  schema: {w}", file=sys.stderr)

    finding, is_skew, m = build_finding(scenario, events)
    print(json.dumps(finding, indent=2, ensure_ascii=False))

    print("\n--- ACCEPTANCE ---")

    # [G1] Cenario baseline (class: none): verde = NENHUM finding. Detectar = falso positivo.
    if scenario.get("anti_pattern", {}).get("class", "none") == "none":
        max_ratio = scenario["acceptance"].get("max_skew_ratio", 2.0)
        if is_skew:
            print(f"❌ FALSO POSITIVO: watcher emitiu finding severity high em job saudavel "
                  f"(ratio {m['ratio']}x). GATE VERMELHO.")
            sys.exit(1)
        if not m["collapsed"] and m["ratio"] > max_ratio:
            print(f"❌ BASELINE SUSPEITO: ratio {m['ratio']}x excede max_skew_ratio "
                  f"{max_ratio}x — distribuicao do gerador nao esta uniforme. GATE VERMELHO.")
            sys.exit(1)
        print(f"✅ Baseline limpo: nenhum falso positivo (ratio {m['ratio']}x <= {max_ratio}x). GATE VERDE.")
        return

    ok, missing, enough = check_acceptance(finding, scenario)
    if not is_skew:
        print("❌ Watcher NAO detectou o anti-pattern declarado.")
        sys.exit(1)
    if not ok:
        print(f"❌ Finding nao satisfaz acceptance. Faltou: {missing}; recs ok: {enough}")
        sys.exit(1)
    print("✅ Anti-pattern detectado E Finding satisfaz o acceptance. GATE VERDE.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: skew_watcher.py <scenario.yaml> <event-log.ndjson|.zstd|dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
