"""
apexlib (v4) — funcoes compartilhadas para ler e analisar event logs do Spark.

Correcoes nesta versao (sobre a v3):
- read_events / iter_events : streaming zstd (sem OOM) + leitura de diretorio de
                              rolling logs (events_1_, events_2_, ...).        [P0 #1, #3]
- hottest_reduce_stage      : prefere acumuladores do operador, depois nome,
                              e expoe fallback de maior volume.                [P0 #2]
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


def _task_succeeded(event):
    task_info = event.get("Task Info") or {}
    if task_info.get("Failed") is True:
        return False

    reason = (event.get("Task End Reason") or {}).get("Reason")
    if reason is None:
        return True
    return reason == "Success"


def _task_partition(event):
    task_info = event.get("Task Info") or {}
    return task_info.get("Index", task_info.get("Partition ID", task_info.get("Task ID")))


def _task_accumulator_ids(event):
    task_info = event.get("Task Info") or {}
    ids = set()
    for accumulable in task_info.get("Accumulables") or []:
        value = accumulable.get("ID", accumulable.get("id"))
        if value is not None:
            ids.add(value)
    return ids


def _effective_task(candidates):
    successful = [event for event in candidates if _task_succeeded(event)]
    if not successful:
        return None

    def completion_key(event):
        task_info = event.get("Task Info") or {}
        finish_time = task_info.get("Finish Time")
        return (
            finish_time if isinstance(finish_time, (int, float)) else float("inf"),
            task_info.get("Attempt", 0),
            task_info.get("Task ID", 0),
        )

    return min(successful, key=completion_key)


def shuffle_tasks_by_stage(events):
    """Return one effective task per stage partition, preserving zero-record tasks."""
    by_stage_attempt = defaultdict(lambda: defaultdict(list))
    for event in events:
        if event.get("Event") != "SparkListenerTaskEnd":
            continue
        stage_id = event.get("Stage ID")
        if stage_id is None:
            continue
        stage_attempt = event.get("Stage Attempt ID", 0)
        by_stage_attempt[stage_id][stage_attempt].append(event)

    result = {}
    for stage_id, attempts in by_stage_attempt.items():
        stage_attempt = max(attempts)
        by_partition = defaultdict(list)
        for event in attempts[stage_attempt]:
            partition = _task_partition(event)
            if partition is not None:
                by_partition[partition].append(event)

        effective = []
        for partition, candidates in by_partition.items():
            event = _effective_task(candidates)
            if event is None:
                continue
            task_info = event.get("Task Info") or {}
            shuffle_read = (event.get("Task Metrics") or {}).get("Shuffle Read Metrics") or {}
            effective.append(
                {
                    "stage_id": stage_id,
                    "stage_attempt": stage_attempt,
                    "partition": partition,
                    "task_attempt": task_info.get("Attempt", 0),
                    "task_id": task_info.get("Task ID"),
                    "finish_time": task_info.get("Finish Time"),
                    "records": shuffle_read.get("Total Records Read", 0) or 0,
                    "task_type": event.get("Task Type"),
                    "accumulator_ids": _task_accumulator_ids(event),
                }
            )
        result[stage_id] = sorted(effective, key=lambda task: task["partition"])
    return result


def shuffle_read_by_stage(events):
    """{stage_id: [records by partition]}, using only the effective successful attempt."""
    return {
        stage_id: [task["records"] for task in tasks]
        for stage_id, tasks in shuffle_tasks_by_stage(events).items()
    }


def _operator_accumulator_ids(events, join_op):
    ids = set()

    def visit(node):
        if not isinstance(node, dict):
            return
        if join_op in str(node.get("nodeName", "")):
            for metric in node.get("metrics") or []:
                value = metric.get("accumulatorId", metric.get("accumulatorID"))
                if value is not None:
                    ids.add(value)
        for child in node.get("children") or []:
            visit(child)

    for event in events:
        visit(event.get("sparkPlanInfo"))
    return ids


def hottest_reduce_stage_details(events, join_op=None):
    """Select a reduce stage and expose the evidence used for that selection."""
    by = shuffle_tasks_by_stage(events)
    if not by:
        return {
            "stage_id": None,
            "tasks": [],
            "records": [],
            "correlation_method": "none",
        }

    if join_op:
        operator_accumulators = _operator_accumulator_ids(events, join_op)
        if operator_accumulators:
            matches = {}
            for stage_id, tasks in by.items():
                matched_tasks = sum(
                    bool(task["accumulator_ids"] & operator_accumulators)
                    for task in tasks
                )
                if matched_tasks:
                    matches[stage_id] = matched_tasks
            if matches:
                stage_id = max(
                    matches,
                    key=lambda value: (matches[value], sum(task["records"] for task in by[value])),
                )
                tasks = sorted(by[stage_id], key=lambda task: task["records"], reverse=True)
                return {
                    "stage_id": stage_id,
                    "tasks": tasks,
                    "records": [task["records"] for task in tasks],
                    "correlation_method": "operator_accumulator",
                }

        names = _stage_names(events)
        joinish = [stage_id for stage_id in by if join_op in names.get(stage_id, "")]
        if joinish:
            stage_id = max(
                joinish,
                key=lambda value: sum(task["records"] for task in by[value]),
            )
            tasks = sorted(by[stage_id], key=lambda task: task["records"], reverse=True)
            return {
                "stage_id": stage_id,
                "tasks": tasks,
                "records": [task["records"] for task in tasks],
                "correlation_method": "stage_name",
            }

    stage_id = max(by, key=lambda value: sum(task["records"] for task in by[value]))
    tasks = sorted(by[stage_id], key=lambda task: task["records"], reverse=True)
    return {
        "stage_id": stage_id,
        "tasks": tasks,
        "records": [task["records"] for task in tasks],
        "correlation_method": "largest_shuffle_fallback",
    }


def hottest_reduce_stage(events, join_op=None):
    """
    Isola o stage de reduce do join. Prefere acumuladores do operador, depois
    nome de stage, e por fim o maior volume como fallback explicito.
    Retorna (stage_id, [records desc]).
    """
    selected = hottest_reduce_stage_details(events, join_op=join_op)
    return selected["stage_id"], selected["records"]


def skew_metrics(records):
    """Compute skew metrics and classify whether the distribution is usable evidence."""
    if not records:
        return {
            "hot": 0,
            "median_cold": 0,
            "ratio": 0.0,
            "n_tasks": 0,
            "n_nonzero_tasks": 0,
            "n_zero_tasks": 0,
            "collapsed": False,
            "evidence_status": "indeterminate",
            "quality_issues": ["no_task_records"],
        }
    n = len(records)
    hot = max(records)
    n_nonzero = sum(record > 0 for record in records)
    n_zero = n - n_nonzero
    if n == 1:
        return {
            "hot": hot,
            "median_cold": 0,
            "ratio": float("inf"),
            "n_tasks": 1,
            "n_nonzero_tasks": n_nonzero,
            "n_zero_tasks": n_zero,
            "collapsed": True,
            "evidence_status": "invalid",
            "quality_issues": ["single_task_collapse"],
        }

    ordered = sorted(records, reverse=True)
    cold = ordered[1:]
    median_cold = statistics.median(cold)
    ratio = round(hot / median_cold, 1) if median_cold else float("inf")
    quality_issues = []
    if median_cold == 0:
        quality_issues.append("zero_cold_median")
    return {
        "hot": hot,
        "median_cold": median_cold,
        "ratio": ratio,
        "n_tasks": n,
        "n_nonzero_tasks": n_nonzero,
        "n_zero_tasks": n_zero,
        "collapsed": False,
        "evidence_status": "invalid" if quality_issues else "valid",
        "quality_issues": quality_issues,
    }
