"""
apexlib (v4) — funcoes compartilhadas para ler e analisar event logs do Spark.

Correcoes nesta versao (sobre a v3):
- read_events / iter_events : streaming zstd (sem OOM) + leitura de diretorio de
                              rolling logs (events_1_, events_2_, ...).        [P0 #1, #3]
- hottest_reduce_stage      : cruza com o nome do stage do join, nao so o maior
                              volume — evita analisar o stage errado.          [P0 #2]
- join_operator             : associa o plano final ao executionId correto.    [P1 #6]
- compute_scenario_hash     : assinatura sha256 do contrato (cadeia de custodia).
- validate_provenance       : rejeita log sintetico gerado de scenario diferente.
"""
import io
import os
import re
import json
import hashlib
import shutil
import subprocess
import statistics
from collections import defaultdict

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
JOIN_OPS = ("BroadcastHashJoin", "SortMergeJoin", "ShuffledHashJoin", "BroadcastNestedLoopJoin")


# ----------------------------------------------------------------------------- leitura
def _rolling_sort_key(path):
    """events_1_, events_2_, ..., events_10_ em ordem numerica (nao lexica)."""
    m = re.search(r"events_(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0


def _resolve_paths(path):
    """Se for diretorio, retorna os arquivos de log em ordem; senao, o proprio arquivo. [P0 #3]"""
    if os.path.isdir(path):
        files = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.startswith("events_") or f.endswith((".ndjson", ".zstd", ".zst"))
        ]
        return sorted(files, key=_rolling_sort_key)
    return [path]


def _open_text_stream(path):
    """Abre um arquivo como stream de texto, descomprimindo zstd em streaming. [P0 #1]"""
    fh = open(path, "rb")
    magic = fh.read(4)
    fh.seek(0)
    if magic == ZSTD_MAGIC:
        try:
            import zstandard
            reader = zstandard.ZstdDecompressor().stream_reader(fh)
            return io.TextIOWrapper(reader, encoding="utf-8", errors="replace")
        except ImportError:
            fh.close()
            if shutil.which("zstd"):
                # fallback sem streaming (carrega na RAM) — avisa o custo
                raw = subprocess.run(
                    ["zstd", "-d", "-c", path], capture_output=True
                ).stdout
                return io.StringIO(raw.decode("utf-8", errors="replace"))
            raise RuntimeError(
                "Log comprimido com zstd. Instale `pip install zstandard` para streaming "
                "ou o binario `zstd`."
            )
    return io.TextIOWrapper(fh, encoding="utf-8", errors="replace")


def iter_events(path):
    """
    Gera eventos um a um (streaming, baixa memoria). Aceita arquivo unico, .zstd,
    ou diretorio de rolling logs. Tolera linhas corrompidas sem derrubar o pipeline.
    """
    for p in _resolve_paths(path):
        stream = _open_text_stream(p)
        try:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
        finally:
            stream.close()


def read_events(path):
    """Compatibilidade: materializa os eventos numa lista. Para logs gigantes, prefira iter_events."""
    return list(iter_events(path))


# ----------------------------------------------------------------------------- proveniencia
def compute_scenario_hash(scenario_path):
    """Assinatura sha256 (truncada) do conteudo do scenario.yaml — a cadeia de custodia."""
    with open(scenario_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    return "sha256:" + digest[:16]


def validate_provenance(events, scenario_path):
    """
    Verifica que um log SINTETICO veio do mesmo scenario que esta sendo usado agora.
    Logs reais (sem evento ApexSyntheticProvenance) passam sem verificacao.
    Levanta ValueError em divergencia (PROVENANCE ERROR).
    """
    prov = next((e for e in events if e.get("Event") == "ApexSyntheticProvenance"), None)
    if prov is None:
        return None  # log real — sem provenance
    current = compute_scenario_hash(scenario_path)
    if prov.get("scenario_hash") != current:
        raise ValueError(
            "PROVENANCE ERROR: log sintetico gerado de scenario diferente do atual.\n"
            f"  hash no log:     {prov.get('scenario_hash')}\n"
            f"  hash do scenario: {current}\n"
            "  Regenere o log sintetico antes de rodar."
        )
    return prov.get("scenario_hash")


# ----------------------------------------------------------------------------- schema
def validate_schema(events):
    warnings = []
    te = next((e for e in events if e.get("Event") == "SparkListenerTaskEnd"), None)
    if te is None:
        warnings.append("nenhum SparkListenerTaskEnd encontrado")
    elif "Task Metrics" not in te:
        warnings.append("TaskEnd sem 'Task Metrics' — schema do Spark pode ter mudado")
    if not any(e.get("Event", "").endswith("SQLExecutionStart") for e in events):
        warnings.append("nenhum SQLExecutionStart — plano fisico indisponivel")
    return warnings


# ----------------------------------------------------------------------------- plano / join
def join_operator(events):
    """
    Operador de join do plano EXECUTADO, associando o plano ao executionId correto. [P1 #6]
    Prefere o plano FINAL (AQE update) sobre o inicial. Procura o join no plano da
    execucao que de fato contem um join, nao apenas o ultimo update visto.
    Retorna (operador | None, usou_plano_final: bool).
    """
    final_by_exec, initial_by_exec = {}, {}
    for e in events:
        ev = e.get("Event", "")
        exec_id = e.get("executionId", e.get("sqlExecutionId"))
        plan = e.get("physicalPlanDescription")
        if not plan:
            continue
        if ev.endswith("SparkListenerSQLAdaptiveExecutionUpdate"):
            final_by_exec[exec_id] = plan
        elif ev.endswith("SparkListenerSQLExecutionStart"):
            initial_by_exec[exec_id] = plan

    for plans, used_final in ((final_by_exec, True), (initial_by_exec, False)):
        for plan in plans.values():
            for op in JOIN_OPS:
                if op in plan:
                    return op, used_final
    return None, bool(final_by_exec)


def _stage_names(events):
    names = {}
    for e in events:
        if e.get("Event", "").endswith("StageSubmitted"):
            si = e.get("Stage Info", {})
            names[si.get("Stage ID")] = si.get("Stage Name", "")
    return names


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


def hottest_reduce_stage(events, join_op=None):
    """
    Isola o stage de reduce do join. Em vez de pegar so o maior volume (que pode ser
    um sort, nao o join), prefere o stage cujo NOME referencia o operador de join. [P0 #2]
    Cai para o maior volume de shuffle se nao houver match por nome.
    Retorna (stage_id, [records desc]).
    """
    by = shuffle_read_by_stage(events)
    if not by:
        return None, []
    if join_op:
        names = _stage_names(events)
        joinish = [sid for sid in by if join_op in names.get(sid, "")]
        if joinish:
            sid = max(joinish, key=lambda s: sum(by[s]))
            return sid, sorted(by[sid], reverse=True)
    sid = max(by, key=lambda s: sum(by[s]))
    return sid, sorted(by[sid], reverse=True)


def skew_metrics(records):
    """hot, median_cold, ratio, n_tasks, collapsed — trata 1 task (colapso) sem /0."""
    if not records:
        return {"hot": 0, "median_cold": 0, "ratio": 0.0, "n_tasks": 0, "collapsed": False}
    n = len(records)
    hot = max(records)
    if n == 1:
        return {"hot": hot, "median_cold": 0, "ratio": float("inf"), "n_tasks": 1, "collapsed": True}
    cold = [r for r in records if r != hot]
    median_cold = statistics.median(cold) if cold else hot
    ratio = round(hot / median_cold, 1) if median_cold else float("inf")
    return {"hot": hot, "median_cold": median_cold, "ratio": ratio, "n_tasks": n, "collapsed": False}
