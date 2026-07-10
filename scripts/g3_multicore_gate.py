#!/usr/bin/env python3
"""
G3 — Gate multi-core: valida o run REAL de 8 tasks que nunca rodou.

O que ele prova (criterios do framework §7):
  1. O stage do join distribuiu em >= min_tasks reais (nao colapsou em 1 task/1 core)
  2. O ratio real bate com o sintetico dentro da tolerancia do oraculo
  3. O watcher detecta o skew no log REAL (nao so no sintetico)

Uso (com o plat-v0 de pe e o event log real em maos):
    python3 scripts/g3_multicore_gate.py --real-log <log.ndjson|.zstd|dir>

Ou baixando direto do MinIO (env MINIO_* configuradas):
    python3 scripts/g3_multicore_gate.py --from-minio --app-id <app_id>

Exit 0 = G3 VERDE. Ver runbook: docs/playbooks/g3-multicore-runbook.md
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from apex import apexlib  # noqa: E402

SCENARIO = str(ROOT / "scenarios" / "skew_on_join_30x.yaml")
MIN_TASKS = 8


def check(real_log, min_tasks=MIN_TASKS):
    results = []

    # -- 1. distribuicao real de tasks no stage do join
    events = apexlib.read_events(real_log)
    op, used_final = apexlib.join_operator(events)
    stage_id, records = apexlib.hottest_reduce_stage(events, join_op=op)
    m = apexlib.skew_metrics(records)
    if m["collapsed"] or m["n_tasks"] < min_tasks:
        results.append((False, f"distribuicao: {m['n_tasks']} task(s) no stage {stage_id} "
                               f"— esperado >= {min_tasks}. Worker ainda esta 1-core?"))
    else:
        results.append((True, f"distribuicao: {m['n_tasks']} tasks no stage {stage_id} "
                              f"(hot {m['hot']}, ratio {m['ratio']}x)"))

    # -- 2. oraculo: sintetico vs real
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        syn = str(Path(td) / "syn.ndjson")
        r = subprocess.run([sys.executable, str(ROOT / "generators/plan_generator.py"),
                            SCENARIO, syn], capture_output=True, text=True)
        if r.returncode != 0:
            results.append((False, f"plan_generator falhou: {r.stderr[:200]}"))
        else:
            r = subprocess.run([sys.executable, str(ROOT / "oracle/compare.py"),
                                SCENARIO, syn, real_log], capture_output=True, text=True)
            ok = r.returncode == 0
            tail = [l for l in r.stdout.splitlines() if l.strip()][-1] if r.stdout else ""
            results.append((ok, f"oraculo: {tail}"))

    # -- 3. watcher no log real
    r = subprocess.run([sys.executable, str(ROOT / "watchers/skew_watcher.py"),
                        SCENARIO, real_log], capture_output=True, text=True)
    ok = r.returncode == 0 and "GATE VERDE" in r.stdout
    results.append((ok, "watcher no log real: " + ("GATE VERDE" if ok else "NAO detectou / falhou")))

    return results


def main():
    p = argparse.ArgumentParser(description="G3 — gate multi-core")
    p.add_argument("--real-log", help="event log real (arquivo, .zstd ou diretorio de rolling logs)")
    p.add_argument("--from-minio", action="store_true", help="baixa o log mais recente do MinIO")
    p.add_argument("--app-id", default=None)
    p.add_argument("--bucket", default="spark-logs")
    p.add_argument("--prefix", default="events/")
    p.add_argument("--min-tasks", type=int, default=MIN_TASKS)
    args = p.parse_args()

    real_log = args.real_log
    if args.from_minio:
        real_log = "g3_real_log.ndjson"
        cmd = [sys.executable, str(ROOT / "scripts/fetch_real_log.py"),
               "--bucket", args.bucket, "--prefix", args.prefix, "--output", real_log]
        if args.app_id:
            cmd += ["--app-id", args.app_id]
        r = subprocess.run(cmd)
        if r.returncode != 0:
            sys.exit("erro: fetch do MinIO falhou (checar env MINIO_* e plat-v0)")
    if not real_log:
        sys.exit("erro: informe --real-log <path> ou --from-minio")

    print(f"\n=== G3 — multi-core gate | log: {real_log} ===\n")
    results = check(real_log, args.min_tasks)
    all_ok = all(ok for ok, _ in results)
    for ok, msg in results:
        print(("✅" if ok else "❌"), msg)
    print()
    if all_ok:
        print("✅ G3 VERDE — run multi-core validado. Atualizar framework §7 e backlog.")
    else:
        print("❌ G3 VERMELHO — ver itens acima. Runbook: docs/playbooks/g3-multicore-runbook.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
