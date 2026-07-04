"""
Apex V1 — Diagnóstico LLM
Lê métricas do ClickHouse para um app_id e gera um finding via Anthropic API.

Uso:
    python analysis/diagnose.py --app-id <app_id>
    python analysis/diagnose.py --app-id <app_id> --model claude-sonnet-4-6

Este é o "Passo 4" da arquitetura V1 desenhada pelo Luan.
Em V2: substituir Anthropic API por Crew.ai multi-agent.
"""
import argparse
import json
import os
import sys
import logging
from datetime import datetime

import clickhouse_connect
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apex.diagnose")

# Config
CH_HOST     = os.getenv("APEX_CH_HOST", "localhost")
CH_PORT     = int(os.getenv("APEX_CH_PORT", "8123"))
CH_USER     = os.getenv("APEX_CH_USER", "apex")
CH_PASSWORD = os.getenv("APEX_CH_PASSWORD", "apex123")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")  # obrigatório

DEFAULT_MODEL = "claude-sonnet-4-6"


def fetch_stage_metrics(client, app_id: str) -> list[dict]:
    """Busca métricas de stage do ClickHouse para o app_id."""
    rows = client.query("""
        SELECT
            stage_id, stage_name, num_tasks, duration_ms,
            input_bytes, shuffle_read, shuffle_write,
            memory_spill, disk_spill, gc_time_ms
        FROM apex.stage_metrics
        WHERE app_id = {app_id:String}
        ORDER BY duration_ms DESC
        LIMIT 20
    """, parameters={"app_id": app_id}).named_results()

    return list(rows)


def fetch_task_distribution(client, app_id: str, stage_id: int) -> dict:
    """Busca distribuição de tasks para detectar skew."""
    row = client.query("""
        SELECT
            count()          AS total_tasks,
            max(duration_ms) AS max_task_ms,
            min(duration_ms) AS min_task_ms,
            avg(duration_ms) AS avg_task_ms,
            sum(disk_spill)  AS total_spill_bytes
        FROM apex.task_metrics
        WHERE app_id = {app_id:String} AND stage_id = {stage_id:UInt32}
    """, parameters={"app_id": app_id, "stage_id": stage_id}).named_results()

    return list(row)[0] if row else {}


def build_prompt(app_id: str, stages: list[dict], task_dist: dict) -> str:
    """Constrói o prompt para o LLM com os dados coletados."""
    stages_summary = json.dumps(stages, indent=2, default=str)
    task_summary = json.dumps(task_dist, indent=2, default=str)

    return f"""Você é um especialista em performance Spark. Analise as métricas abaixo e gere um diagnóstico estruturado.

APP ID: {app_id}

MÉTRICAS DE STAGE (top 20 por duração):
{stages_summary}

DISTRIBUIÇÃO DE TASKS (stage mais lento):
{task_summary}

Identifique:
1. O principal problema de performance (skew, parallelism collapse, spill, broadcast miss, etc.)
2. Qual stage é o bottleneck e por quê
3. Qual a causa raiz provável (com base nos dados)
4. Uma recomendação concreta e aplicável

Responda em JSON com este schema exato:
{{
  "pattern": "skew|parallelism_collapse|spill|broadcast_miss|small_files|other",
  "severity": "critical|high|medium|low",
  "confidence": 0.0-1.0,
  "bottleneck_stage_id": <int ou null>,
  "root_cause": "<string descritiva>",
  "recommendation": "<string com o fix concreto>",
  "evidence": {{
    "key_metric": "<nome da métrica que evidencia o problema>",
    "key_value": "<valor observado>",
    "expected_value": "<valor esperado em condições normais>"
  }}
}}"""


def call_llm(prompt: str, model: str) -> dict:
    """Chama a API Anthropic e parseia o JSON retornado."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Remove markdown code fences se presentes
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def persist_finding(ch_client, app_id: str, finding: dict, model: str) -> None:
    """Salva o finding no ClickHouse."""
    ch_client.insert(
        "apex.findings",
        [[
            app_id,
            finding.get("bottleneck_stage_id"),
            finding.get("pattern", "unknown"),
            finding.get("severity", "medium"),
            float(finding.get("confidence", 0.0)),
            finding.get("root_cause", ""),
            finding.get("recommendation", ""),
            model,
        ]],
        column_names=[
            "app_id", "stage_id", "pattern", "severity", "confidence",
            "root_cause", "recommendation", "llm_model",
        ],
    )


def diagnose(app_id: str, model: str = DEFAULT_MODEL) -> dict:
    """Pipeline completo: ClickHouse → LLM → Finding."""

    if not ANTHROPIC_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY não configurada")

    ch = clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT,
        username=CH_USER, password=CH_PASSWORD,
    )

    logger.info(f"Buscando métricas para app_id={app_id}")
    stages = fetch_stage_metrics(ch, app_id)

    if not stages:
        logger.error(f"Nenhuma métrica encontrada para app_id={app_id}")
        sys.exit(1)

    # Pega o stage mais lento para task distribution
    slowest_stage_id = stages[0]["stage_id"]
    task_dist = fetch_task_distribution(ch, app_id, slowest_stage_id)

    logger.info(f"{len(stages)} stages encontrados | analisando stage {slowest_stage_id}")

    prompt = build_prompt(app_id, stages, task_dist)

    logger.info(f"Chamando {model}...")
    finding = call_llm(prompt, model)
    finding["llm_model"] = model
    finding["app_id"] = app_id

    # Persiste o finding
    persist_finding(ch, app_id, finding, model)

    return finding


def main():
    parser = argparse.ArgumentParser(description="Apex V1 — Diagnóstico LLM")
    parser.add_argument("--app-id", required=True, help="Spark application ID")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modelo Anthropic")
    args = parser.parse_args()

    finding = diagnose(args.app_id, args.model)

    print("\n" + "=" * 60)
    print("APEX FINDING")
    print("=" * 60)
    print(json.dumps(finding, indent=2, ensure_ascii=False))
    print("=" * 60)

    # Exit code baseado em severidade
    exit_codes = {"critical": 2, "high": 1, "medium": 0, "low": 0}
    sys.exit(exit_codes.get(finding.get("severity", "low"), 0))


if __name__ == "__main__":
    main()
