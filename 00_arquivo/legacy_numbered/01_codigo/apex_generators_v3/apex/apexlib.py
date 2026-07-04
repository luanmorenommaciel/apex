"""
apexlib — funcoes compartilhadas para ler e analisar event logs do Spark (reais ou sinteticos).

Concentra aqui o que o Watcher e o Oraculo precisam, para nao duplicar logica nem
divergir. Cada funcao resolve uma das fragilidades que apareceram no run real:

- read_events       : auto-descomprime zstd (o MinIO/plat-v0 entrega comprimido) e nao
                      derruba o pipeline numa linha corrompida.  [resiliencia]
- validate_schema   : avisa se o event log nao tem a estrutura esperada do Spark. [resiliencia]
- join_operator     : le o plano FINAL pos-AQE quando existe, nao o inicial.       [correcao]
- hottest_reduce_stage : isola o stage de reduce do join, em vez de misturar tasks
                      de scan (que leem 0) com as de reduce.                        [correcao]
- skew_metrics      : trata 1 task (colapso AQE) explicitamente, sem hack de /0.    [correcao]
"""
import json
import shutil
import subprocess
import statistics
from collections import defaultdict

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


def read_events(path):
    """Le um event log NDJSON. Auto-detecta zstd e descomprime. Tolera linhas corrompidas."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] == ZSTD_MAGIC:
        raw = _decompress_zstd(raw)
    text = raw.decode("utf-8", errors="replace")
    events = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # uma linha quebrada nao invalida o log inteiro
    return events


def _decompress_zstd(raw):
    try:
        import zstandard
        return zstandard.ZstdDecompressor().decompress(raw, max_output_size=1 << 30)
    except ImportError:
        pass
    if shutil.which("zstd"):
        return subprocess.run(["zstd", "-d", "-c"], input=raw, capture_output=True).stdout
    raise RuntimeError(
        "Event log comprimido com zstd. Instale `pip install zstandard` ou o binario `zstd`."
    )


def validate_schema(events):
    """Retorna lista de avisos se o event log nao tem a estrutura esperada do Spark."""
    warnings = []
    te = next((e for e in events if e.get("Event") == "SparkListenerTaskEnd"), None)
    if te is None:
        warnings.append("nenhum SparkListenerTaskEnd encontrado")
    elif "Task Metrics" not in te:
        warnings.append("TaskEnd sem 'Task Metrics' — versao do Spark pode ter mudado o schema")
    if not any(e.get("Event", "").endswith("SQLExecutionStart") for e in events):
        warnings.append("nenhum SQLExecutionStart — plano fisico indisponivel")
    return warnings


def join_operator(events):
    """
    Operador de join do plano EXECUTADO.
    Prefere o plano FINAL (ultimo SparkListenerSQLAdaptiveExecutionUpdate), porque o AQE
    muda o plano em pleno voo; cai para o plano inicial so se nao houver update do AQE.
    Retorna (operador | None, usou_plano_final: bool).
    """
    final_plan = initial_plan = None
    for e in events:
        ev = e.get("Event", "")
        if ev.endswith("SparkListenerSQLAdaptiveExecutionUpdate"):
            final_plan = e.get("physicalPlanDescription") or final_plan
        elif ev.endswith("SparkListenerSQLExecutionStart"):
            initial_plan = e.get("physicalPlanDescription") or initial_plan
    plan = final_plan or initial_plan or ""
    for op in ("BroadcastHashJoin", "SortMergeJoin", "ShuffledHashJoin", "BroadcastNestedLoopJoin"):
        if op in plan:
            return op, final_plan is not None
    return None, final_plan is not None


def shuffle_read_by_stage(events):
    """{stage_id: [records lidos por task]} — somente tasks que leram shuffle (>0)."""
    by = defaultdict(list)
    for e in events:
        if e.get("Event") == "SparkListenerTaskEnd":
            recs = (e.get("Task Metrics") or {}).get("Shuffle Read Metrics", {}).get(
                "Total Records Read", 0
            )
            if recs and recs > 0:
                by[e["Stage ID"]].append(recs)
    return dict(by)


def hottest_reduce_stage(events):
    """
    O stage de reduce do join e o que mais leu shuffle no total — isso ISOLA o join,
    em vez de misturar com tasks de scan (que leem 0 shuffle). Retorna (stage_id, [records desc]).
    """
    by = shuffle_read_by_stage(events)
    if not by:
        return None, []
    sid = max(by, key=lambda s: sum(by[s]))
    return sid, sorted(by[sid], reverse=True)


def skew_metrics(records):
    """
    Dada a distribuicao de records de UM stage, retorna dict com:
      hot, median_cold, ratio, n_tasks, collapsed
    Trata 1 task explicitamente (colapso do AQE ou concentracao total) — sem hack de /0.
    """
    if not records:
        return {"hot": 0, "median_cold": 0, "ratio": 0.0, "n_tasks": 0, "collapsed": False}
    n = len(records)
    hot = max(records)
    if n == 1:
        # Uma unica task leu todo o shuffle do stage: ou o AQE coalesceu as particoes,
        # ou ha concentracao total numa chave. Nao da para comparar contra pares.
        return {"hot": hot, "median_cold": 0, "ratio": float("inf"), "n_tasks": 1, "collapsed": True}
    cold = [r for r in records if r != hot]
    median_cold = statistics.median(cold) if cold else hot
    ratio = round(hot / median_cold, 1) if median_cold else float("inf")
    return {"hot": hot, "median_cold": median_cold, "ratio": ratio, "n_tasks": n, "collapsed": False}
