#!/usr/bin/env python3
"""
Inventario empirico de cobertura do Spark event log.

O relatorio separa:

  [A] campos consumidos pelo Apex atual;
  [B*] campos observados e valiosos ainda nao consumidos;
  [B] demais campos observados ainda nao consumidos;
  [C] informacoes que dependem de configuracao ou runtime;
  [D] sinais esperados que nao apareceram neste corpus;
  [E] informacoes ausentes do event log padrao;
  [F] diagnosticos inferiveis, mas sem causalidade comprovada.

Uso:
    python3 tools/coverage_inventory.py LOG [LOG ...]
    python3 tools/coverage_inventory.py LOG [LOG ...] --md docs/coverage/report.md
"""

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apex import apexlib


CONSUMED = {
    "Event",
    "executionId",
    "sqlExecutionId",
    "physicalPlanDescription",
    "Stage ID",
    "Stage Info.Stage ID",
    "Stage Info.Stage Name",
    "Task Metrics.Shuffle Read Metrics.Total Records Read",
    "scenario_hash",
    "scenario_id",
}

HIGH_VALUE = {
    "Task Metrics.Executor CPU Time": "comparar CPU time com run time",
    "Task Metrics.Executor Run Time": "tempo de execucao por task",
    "Task Metrics.JVM GC Time": "pressao de GC",
    "Task Metrics.Memory Bytes Spilled": "spill em memoria",
    "Task Metrics.Disk Bytes Spilled": "spill em disco",
    "Task Metrics.Peak Execution Memory": "indicador parcial de pressao de memoria",
    "Task Metrics.Result Size": "volume devolvido ao driver",
    "Task Metrics.Result Serialization Time": "custo de serializacao do resultado",
    "Task Metrics.Input Metrics.Bytes Read": "volume de scan",
    "Task Metrics.Input Metrics.Records Read": "volume de registros por task",
    "Task Metrics.Output Metrics.Bytes Written": "volume de escrita",
    "Task Metrics.Output Metrics.Records Written": "registros escritos",
    "Task Metrics.Shuffle Write Metrics.Shuffle Bytes Written": "distribuicao do shuffle write",
    "Task Metrics.Shuffle Write Metrics.Shuffle Records Written": "registros no shuffle write",
    "Task Metrics.Shuffle Read Metrics.Fetch Wait Time": "espera por fetch de shuffle",
    "Task Metrics.Shuffle Read Metrics.Remote Bytes Read": "shuffle remoto",
    "Task Info.Getting Result Time": "inicio do fetch de resultado pelo driver",
    "Task End Reason.Reason": "motivo registrado para termino ou falha",
    "Stage Info.Number of Tasks": "paralelismo do stage",
    "Stage Info.Stage Attempt ID": "retries do stage",
    "Stage Info.RDD Info.Callsite": "local de criacao do RDD",
    "Stage Info.RDD Info.Scope": "escopo e operacao do RDD",
    "sparkPlanInfo": "arvore estruturada do plano e metricas SQL por no",
}

DYNAMIC_MAP_NAMES = {
    "Classpath Entries",
    "Hadoop Properties",
    "Metrics Properties",
    "Spark Properties",
    "System Properties",
    "driverAttributes",
    "driverLogs",
    "modifiedConfigs",
}

OBSERVATION_VALUE_FIELDS = {
    "Stage Info.Stage Attempt ID",
    "Task Info.Attempt",
    "Task End Reason.Reason",
    "Task Metrics.Memory Bytes Spilled",
    "Task Metrics.Disk Bytes Spilled",
}

RUNTIME_DEPENDENT = [
    (
        "metricas de processo e host",
        "dependem das configuracoes de executor metrics e process tree metrics",
    ),
    (
        "perfil detalhado de Python UDF",
        "depende do profiler e das opcoes disponiveis na versao do Spark",
    ),
    (
        "campos especificos de Databricks Runtime e Photon",
        "o schema e a disponibilidade variam por runtime",
    ),
    (
        "telemetria de Databricks Serverless",
        "compute event logs nao sao a fonte padrao; exige Query Profile ou system tables",
    ),
    (
        "detalhes longos de callsite",
        "dependem de spark.eventLog.longForm.enabled",
    ),
]

STRUCTURALLY_ABSENT = [
    (
        "implementacao interna de UDF Python, Scala ou Java",
        "o plano registra o operador, nao o corpo executado",
    ),
    (
        "corpo das closures de RDD",
        "RDD Info registra lineage, scope e callsite, nao a funcao serializada",
    ),
    (
        "valores das linhas e da chave quente",
        "as metricas registram volumes e tempos, nao os dados do cliente",
    ),
    (
        "codigo do driver entre actions Spark",
        "nao existe evento de task para codigo local comum",
    ),
    (
        "alternativas descartadas e trilha completa de regras do Catalyst",
        "o log padrao registra planos, nao todo o processo de busca",
    ),
    (
        "codigo Java gerado pelo whole-stage codegen",
        "o plano indica codegen, mas nao inclui o codigo gerado completo",
    ),
    (
        "contencao de threads e lock waits detalhados da JVM",
        "exige profiler ou telemetria complementar",
    ),
]

INFERRED_NOT_CAUSAL = [
    (
        "CPU-bound versus espera",
        "CPU time dividido por run time e um indicador, nao prova saturacao do host",
    ),
    (
        "small files",
        "muitas tasks com poucos bytes ou registros sugerem o problema",
    ),
    (
        "pressao de memoria ou risco de OOM",
        "GC, spill e peak memory sao sinais parciais",
    ),
    (
        "espera em JDBC, S3 ou API",
        "task lenta pode indicar espera externa, mas o event log nao prova a origem",
    ),
    (
        "causa externa da perda de executor",
        "reason e stack trace podem existir, mas spot, OOM killer ou falha do no podem ficar ambiguos",
    ),
    (
        "valor da hot key",
        "a distribuicao aponta a particao quente, nao identifica o valor sem outra fonte",
    ),
    (
        "motivo exato da decisao do AQE",
        "o update mostra o novo plano, nao toda a conta que levou a decisao",
    ),
]


@dataclass
class InventoryResult:
    by_event: dict
    counts: dict
    total: int
    source_count: int
    application_ids: set
    plan_texts: list
    values_by_field: dict


def _is_dynamic_map(prefix):
    return bool(prefix) and prefix.rsplit(".", 1)[-1] in DYNAMIC_MAP_NAMES


def _canonical_path(path):
    if path.startswith("sparkPlanInfo."):
        return re.sub(r"(?:\.children){2,}", ".children", path)
    return path


def _walk_values(obj, prefix="", list_sample_limit=5):
    if isinstance(obj, dict):
        if _is_dynamic_map(prefix):
            values = list(obj.values())
            if not values:
                return
            for value in values[:list_sample_limit]:
                yield from _walk_values(value, f"{prefix}.<entry>", list_sample_limit)
            return
        for key, value in obj.items():
            child = _canonical_path(f"{prefix}.{key}" if prefix else key)
            yield from _walk_values(value, child, list_sample_limit)
    elif isinstance(obj, list):
        for item in obj[:list_sample_limit]:
            yield from _walk_values(item, prefix, list_sample_limit)
    else:
        yield _canonical_path(prefix), type(obj).__name__, obj


def walk(obj, prefix="", list_sample_limit=5):
    """Gera caminhos de folhas sem transformar chaves dinamicas em schema."""
    for path, value_type, _ in _walk_values(obj, prefix, list_sample_limit):
        yield path, value_type


def _matches_root(field, root):
    return field == root or field.startswith(root + ".")


def signal_for(field):
    matches = [
        (root, description)
        for root, description in HIGH_VALUE.items()
        if _matches_root(field, root)
    ]
    if not matches:
        return None
    return max(matches, key=lambda match: len(match[0]))[1]


def classify(field):
    if any(_matches_root(field, consumed) for consumed in CONSUMED):
        return "A"
    if signal_for(field):
        return "B*"
    return "B"


def inventory(paths):
    by_event = defaultdict(lambda: defaultdict(set))
    counts = defaultdict(int)
    application_ids = set()
    plan_texts = []
    values_by_field = defaultdict(set)
    total = 0

    for source_index, source in enumerate(paths):
        application_without_id = 0
        for event in apexlib.iter_events(source):
            total += 1
            event_type = event.get("Event", "<sem Event>")
            counts[event_type] += 1

            if event_type.endswith("ApplicationStart"):
                app_id = event.get("App ID") or event.get("appId")
                if not app_id:
                    application_without_id += 1
                    app_id = f"source-{source_index + 1}-app-{application_without_id}"
                application_ids.add(str(app_id))

            plan = event.get("physicalPlanDescription")
            if isinstance(plan, str):
                plan_texts.append(plan)

            for field, value_type, value in _walk_values(event):
                by_event[event_type][field].add(value_type)
                if field in OBSERVATION_VALUE_FIELDS and len(values_by_field[field]) < 20:
                    values_by_field[field].add(value)

    return InventoryResult(
        by_event=dict(by_event),
        counts=dict(counts),
        total=total,
        source_count=len(paths),
        application_ids=application_ids,
        plan_texts=plan_texts,
        values_by_field=dict(values_by_field),
    )


def _all_fields(result):
    fields = {}
    for event_type, event_fields in result.by_event.items():
        short_event = event_type.split(".")[-1]
        for field in event_fields:
            fields.setdefault(field, [classify(field), set()])[1].add(short_event)
    return fields


def _has_event(result, suffix):
    return any(event_type.endswith(suffix) for event_type in result.counts)


def _missing_observations(result, fields):
    plans = "\n".join(result.plan_texts)
    spill_values = (
        result.values_by_field.get("Task Metrics.Memory Bytes Spilled", set())
        | result.values_by_field.get("Task Metrics.Disk Bytes Spilled", set())
    )
    reasons = {
        str(reason).lower()
        for reason in result.values_by_field.get("Task End Reason.Reason", set())
    }
    attempts = (
        result.values_by_field.get("Stage Info.Stage Attempt ID", set())
        | result.values_by_field.get("Task Info.Attempt", set())
    )
    exercised_failure_or_retry = (
        any(reason not in {"success", ""} for reason in reasons)
        or any(isinstance(attempt, (int, float)) and attempt > 0 for attempt in attempts)
        or _has_event(result, "SparkListenerSpeculativeTaskSubmitted")
    )
    checks = [
        (
            "AQE com atualizacao de plano final",
            _has_event(result, "SparkListenerSQLAdaptiveExecutionUpdate"),
        ),
        (
            "Structured Streaming QueryProgressEvent",
            any("QueryProgressEvent" in event_type for event_type in result.counts),
        ),
        (
            "perda ou remocao de executor",
            _has_event(result, "SparkListenerExecutorRemoved")
            or "ExecutorLostFailure" in plans,
        ),
        (
            "Python UDF ou Pandas UDF no plano",
            "BatchEvalPython" in plans or "ArrowEvalPython" in plans,
        ),
        (
            "RDD Callsite e Scope",
            "Stage Info.RDD Info.Callsite" in fields
            and "Stage Info.RDD Info.Scope" in fields,
        ),
        (
            "mais de uma execucao SQL na mesma amostra",
            sum(
                count
                for event_type, count in result.counts.items()
                if event_type.endswith("SparkListenerSQLExecutionStart")
            )
            > 1,
        ),
        (
            "spill efetivo (> 0)",
            any(
                isinstance(value, (int, float)) and value > 0
                for value in spill_values
            ),
        ),
        (
            "falha, retry ou tentativa especulativa real",
            exercised_failure_or_retry,
        ),
    ]
    return [label for label, observed in checks if not observed]


def _write_table(lines, rows):
    lines.append("| caso | interpretacao |")
    lines.append("|---|---|")
    for case, explanation in rows:
        lines.append(f"| {case} | {explanation} |")


def report(result):
    lines = ["# Cobertura do event log - Spark emite x Apex consome x falta", ""]
    app_count = len(result.application_ids)
    lines.append(
        f"Fontes analisadas: **{result.source_count}** | "
        f"aplicacoes: **{app_count}** | eventos: **{result.total}** | "
        f"tipos de evento: **{len(result.counts)}**"
    )
    if app_count < 2:
        lines.extend(
            [
                "",
                f"> Corpus parcial: {app_count} aplicacao e "
                f"{len(result.counts)} tipos de evento. "
                "A ausencia de um sinal neste relatorio nao prova que o Spark nao o emite.",
            ]
        )

    lines.extend(["", "## Tipos de evento observados", "", "| evento | ocorrencias |", "|---|---|"])
    for event_type, count in sorted(result.counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{event_type.split('.')[-1]}` | {count} |")

    fields = _all_fields(result)
    extracted = sorted(field for field, (kind, _) in fields.items() if kind == "A")
    valuable = sorted(field for field, (kind, _) in fields.items() if kind == "B*")
    available = sorted(field for field, (kind, _) in fields.items() if kind == "B")

    lines.extend(["", f"## [A] Consumido pelo Apex atual - {len(extracted)} campos", ""])
    lines.extend(f"- `{field}`" for field in extracted)

    lines.extend(
        [
            "",
            f"## [B*] Observado e valioso, ainda nao consumido - {len(valuable)} campos",
            "",
            "| campo observado | uso potencial |",
            "|---|---|",
        ]
    )
    for field in valuable:
        lines.append(f"| `{field}` | {signal_for(field)} |")

    lines.extend(
        [
            "",
            f"## [B] Demais campos observados, ainda nao consumidos - {len(available)} campos",
            "",
        ]
    )
    preview = available[:60]
    lines.append(", ".join(f"`{field}`" for field in preview))
    if len(available) > len(preview):
        lines.append(f"\n_Lista resumida: {len(available) - len(preview)} campos omitidos._")

    lines.extend(["", "## [C] Depende de configuracao ou runtime", ""])
    _write_table(lines, RUNTIME_DEPENDENT)

    missing = _missing_observations(result, fields)
    lines.extend(["", "## [D] Nao observado neste corpus", ""])
    lines.append(
        "Estes sinais precisam de outros cenarios antes de qualquer conclusao sobre cobertura:"
    )
    lines.extend(f"- {item}" for item in missing)

    lines.extend(["", "## [E] Ausente do event log padrao", ""])
    _write_table(lines, STRUCTURALLY_ABSENT)

    lines.extend(["", "## [F] Inferivel, sem causalidade comprovada", ""])
    _write_table(lines, INFERRED_NOT_CAUSAL)

    lines.extend(
        [
            "",
            "## Leitura correta deste resultado",
            "",
            f"- O corpus comprova que o Apex consumiu **{len(extracted)}** campos observados.",
            f"- O corpus revelou **{len(valuable)}** campos valiosos ainda nao consumidos.",
            f"- O corpus revelou **{len(available)}** outros caminhos de campo apos agrupar mapas dinamicos.",
            "- A secao [D] registra lacunas do corpus, nao limites do Spark.",
            "- As secoes [C], [E] e [F] sao conhecimento arquitetural versionado no script.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", help="arquivos ou diretorios de event log")
    parser.add_argument("--md", help="arquivo Markdown de saida")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    result = inventory(args.logs)
    text = report(result)
    if args.md:
        output = Path(args.md)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"relatorio escrito: {output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
