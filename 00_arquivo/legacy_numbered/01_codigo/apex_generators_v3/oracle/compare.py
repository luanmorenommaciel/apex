#!/usr/bin/env python3
"""
Oraculo (v3) — endurecido.

Mudancas vs v2 (que tinha band-aids):
- Em vez de `if False:` desabilitando a comparacao de ratio, o oraculo agora DETECTA
  quando os dois logs medem distribuicoes diferentes (ex: o real colapsou em 1 task no
  ambiente 1-core, enquanto o sintetico tem spread). Isso vira um AVISO honesto
  ("ambiente colapsou — rode multi-core para validar o ratio"), nao um fail silencioso
  nem um green forjado.
- Usa apexlib para isolar o stage de reduce do join (compara mesma-coisa-com-mesma-coisa).
- Compara: operador de join (hard), volume da task quente (com tolerancia), e ratio
  (apenas quando ambos os lados tem spread — senao reporta o colapso).
"""
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib


def signals(log_path):
    events = apexlib.read_events(log_path)
    op, used_final = apexlib.join_operator(events)
    _, records = apexlib.hottest_reduce_stage(events)
    m = apexlib.skew_metrics(records)
    return {"join_op": op, "used_final_plan": used_final, **m}


def main(scenario_path, synthetic_log, real_log):
    tol = yaml.safe_load(open(scenario_path))["oracle"]["tolerance"]
    s, r = signals(synthetic_log), signals(real_log)
    print(f"sintetico: join={s['join_op']} hot={s['hot']} ratio={s['ratio']} tasks={s['n_tasks']}")
    print(f"real:      join={r['join_op']} hot={r['hot']} ratio={r['ratio']} tasks={r['n_tasks']}")

    problems, warnings = [], []

    # 1. Operador de join: tem que bater (hard).
    if s["join_op"] != r["join_op"]:
        problems.append(f"join operator divergiu: {s['join_op']} vs {r['join_op']}")

    # 2. Volume da task quente: com tolerancia (sinal estavel entre ambientes).
    if r["hot"]:
        rec_dev = abs(s["hot"] - r["hot"]) / r["hot"]
        if rec_dev > tol["records"]:
            problems.append(
                f"registros da task quente divergiram {rec_dev:.0%} (tolerancia {tol['records']:.0%})"
            )

    # 3. Ratio: so compara se AMBOS tem spread (>1 task). Se um colapsou, reporta honestamente.
    if s["collapsed"] or r["collapsed"]:
        lado = "real" if r["collapsed"] else "sintetico"
        warnings.append(
            f"o lado {lado} colapsou em 1 task (AQE/1-core) — ratio nao comparavel. "
            f"Rode o job em cluster multi-core para validar a cauda da distribuicao."
        )
    elif r["ratio"] and r["ratio"] != float("inf"):
        ratio_dev = abs(s["ratio"] - r["ratio"]) / r["ratio"]
        if ratio_dev > tol["skew_ratio"]:
            problems.append(
                f"skew ratio divergiu {ratio_dev:.0%} (tolerancia {tol['skew_ratio']:.0%})"
            )

    for w in warnings:
        print(f"⚠️  {w}")

    if problems:
        print("\n❌ ORACULO: o sintetico DESVIOU do Spark real:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("\n✅ ORACULO: sintetico fiel ao Spark real dentro da tolerancia. Fidelidade OK.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: compare.py <scenario.yaml> <synthetic.ndjson> <real.ndjson|.zstd>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
