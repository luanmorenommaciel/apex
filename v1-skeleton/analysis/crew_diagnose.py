"""
Apex V1 — Diagnóstico Crew.ai (crewai >= 1.0)

Pipeline multi-agent sequencial:
  MetricsAnalyzer  → lê ClickHouse, identifica padrão e bottleneck
  RecommendationWriter → recebe análise, escreve fix concreto

Uso:
    python analysis/crew_diagnose.py --app-id <app_id>
    python analysis/crew_diagnose.py --app-id <app_id> --model claude-sonnet-4-6

Import em outros módulos:
    from analysis.crew_diagnose import diagnose, persist_finding
"""
import argparse
import json
import os
import re
import sys
import logging
from typing import Optional

# Desabilita telemetria do crewai 1.x (evita conexão de rede na importação)
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

import clickhouse_connect
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apex.crew")

# ── Config ───────────────────────────────────────────────────────────────────

CH_HOST     = os.getenv("APEX_CH_HOST", "localhost")
CH_PORT     = int(os.getenv("APEX_CH_PORT", "8123"))
CH_USER     = os.getenv("APEX_CH_USER", "apex")
CH_PASSWORD = os.getenv("APEX_CH_PASSWORD", "apex123")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("APEX_LLM_MODEL", "claude-sonnet-4-6")

# ── Schema de saída (Pydantic — anti-alucinação) ─────────────────────────────

class Evidence(BaseModel):
    key_metric:     str = Field(description="Nome da métrica principal que evidencia o problema")
    key_value:      str = Field(description="Valor observado")
    expected_value: str = Field(description="Valor esperado em condições normais")

class ApexFinding(BaseModel):
    pattern:             str            = Field(description="skew|parallelism_collapse|spill|broadcast_miss|small_files|other")
    severity:            str            = Field(description="critical|high|medium|low")
    confidence:          float          = Field(ge=0.0, le=1.0, description="Confiança 0.0–1.0")
    bottleneck_stage_id: Optional[int]  = Field(default=None, description="Stage ID do bottleneck ou null")
    root_cause:          str            = Field(max_length=500, description="Causa raiz em até 500 chars")
    recommendation:      str            = Field(max_length=500, description="Fix concreto e aplicável em até 500 chars")
    evidence:            Evidence       = Field(description="Evidência quantitativa")

# ── Padrões válidos e contratos ───────────────────────────────────────────────

KNOWN_PATTERNS = ["skew", "parallelism_collapse", "spill", "broadcast_miss", "small_files", "other"]
SEVERITY_LEVELS = ["critical", "high", "medium", "low"]

PATTERN_KEYWORDS = {
    "skew":                 ["salting", "repartition", "skewhint", "adaptive"],
    "spill":                ["spark.executor.memory", "spark.memory.fraction", "repartition", "persist"],
    "parallelism_collapse": ["repartition", "spark.default.parallelism", "spark.sql.shuffle.partitions"],
    "broadcast_miss":       ["broadcast", "hint", "autobroadcastjointhreshold"],
    "small_files":          ["coalesce", "repartition", "compact"],
}

# ── ClickHouse tools ──────────────────────────────────────────────────────────

def _get_ch():
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT,
        username=CH_USER, password=CH_PASSWORD,
    )


@tool("fetch_stage_metrics")
def fetch_stage_metrics(app_id: str) -> str:
    """
    Busca métricas de stage do ClickHouse para o app_id informado.
    Retorna os top 20 stages por duração em formato JSON.
    Use como primeiro passo da análise de performance.
    """
    try:
        ch = _get_ch()
        rows = ch.query("""
            SELECT
                stage_id, stage_name, num_tasks, duration_ms,
                input_bytes, shuffle_read, shuffle_write,
                memory_spill, disk_spill, gc_time_ms
            FROM apex.stage_metrics
            WHERE app_id = {app_id:String}
            ORDER BY duration_ms DESC
            LIMIT 20
        """, parameters={"app_id": app_id}).named_results()
        result = list(rows)
        if not result:
            return f"NENHUMA MÉTRICA encontrada para app_id={app_id}"
        return json.dumps(result, default=str)
    except Exception as e:
        return f"ERRO ao buscar stage metrics: {e}"


@tool("fetch_task_distribution")
def fetch_task_distribution(app_id: str, stage_id: int) -> str:
    """
    Busca distribuição de tasks de um stage para detectar skew.
    Retorna min/max/avg de duration_ms e total de disk_spill.
    Use após identificar o stage mais lento com fetch_stage_metrics.
    """
    try:
        ch = _get_ch()
        rows = ch.query("""
            SELECT
                count()           AS total_tasks,
                max(duration_ms)  AS max_task_ms,
                min(duration_ms)  AS min_task_ms,
                avg(duration_ms)  AS avg_task_ms,
                sum(disk_spill)   AS total_spill_bytes,
                sum(memory_spill) AS total_memory_spill
            FROM apex.task_metrics
            WHERE app_id = {app_id:String}
              AND stage_id = {stage_id:UInt32}
        """, parameters={"app_id": app_id, "stage_id": stage_id}).named_results()
        result = list(rows)
        return json.dumps(result[0] if result else {}, default=str)
    except Exception as e:
        return f"ERRO ao buscar task distribution: {e}"


# ── LLM ──────────────────────────────────────────────────────────────────────

def _get_llm(model: str) -> LLM:
    if not ANTHROPIC_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY não configurada")
    # crewai 1.x usa litellm internamente — prefixo "anthropic/" para o provider
    return LLM(
        model=f"anthropic/{model}",
        api_key=ANTHROPIC_KEY,
        max_tokens=1024,
    )


# ── Agents ───────────────────────────────────────────────────────────────────

def build_metrics_analyzer(llm: LLM) -> Agent:
    return Agent(
        role="Spark Performance Analyst",
        goal=(
            "Identificar o principal anti-pattern de performance em um job Spark "
            "analisando métricas de stage e task do ClickHouse. "
            "Produzir análise estruturada com: padrão, bottleneck, evidências quantitativas e confiança."
        ),
        backstory=(
            "Especialista em Spark internals com 8 anos de experiência. "
            "Conhece skew, spill, parallelism collapse, broadcast miss e small files. "
            "Baseia conclusões SEMPRE em dados observados — nunca assume sem evidência. "
            f"Padrões válidos: {KNOWN_PATTERNS}. "
            "Se dados insuficientes, reporta 'other' com confidence < 0.5."
        ),
        tools=[fetch_stage_metrics, fetch_task_distribution],
        llm=llm,
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )


def build_recommendation_writer(llm: LLM) -> Agent:
    return Agent(
        role="Spark Fix Engineer",
        goal=(
            "Converter análise de performance em recomendação concreta e aplicável. "
            "Fix específico com código de exemplo quando possível. "
            "Saída no formato JSON exato do schema ApexFinding."
        ),
        backstory=(
            "Senior Spark engineer que escreve código, não apenas conselhos. "
            "Skew → sugere salting com exemplo concreto de salt + repartition. "
            "Spill → sugere configuração de memória com valores específicos. "
            "NUNCA inventa dados que não estavam na análise. "
            "Sempre respeita o schema: pattern, severity, confidence, "
            "bottleneck_stage_id, root_cause, recommendation, evidence."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )


# ── Tasks ─────────────────────────────────────────────────────────────────────

def build_analyze_task(agent: Agent, app_id: str) -> Task:
    return Task(
        description=(
            f"Analise o job Spark app_id='{app_id}'.\n\n"
            "Passos obrigatórios:\n"
            "1. Chame fetch_stage_metrics para obter os stages\n"
            "2. Identifique o stage mais lento (maior duration_ms)\n"
            "3. Chame fetch_task_distribution no stage mais lento\n"
            f"4. Classifique usando APENAS: {KNOWN_PATTERNS}\n"
            "5. Sinais por padrão:\n"
            "   skew: max_task_ms/avg_task_ms > 3\n"
            "   spill: disk_spill > 0\n"
            "   parallelism_collapse: num_tasks < 8 com input_bytes > 1GB\n"
        ),
        expected_output=(
            "JSON com: pattern, confidence (0.0-1.0), bottleneck_stage_id, "
            "evidências numéricas do que foi observado vs esperado, "
            "e resumo em 2-3 frases."
        ),
        agent=agent,
    )


def build_recommendation_task(agent: Agent, app_id: str, analyze_task: Task) -> Task:
    return Task(
        description=(
            f"Com base na análise do job '{app_id}', produza o finding final.\n\n"
            "Regras:\n"
            "1. Use APENAS dados da análise — não invente métricas\n"
            "2. recommendation: fix concreto, max 500 chars\n"
            "3. skew → inclua exemplo de salting\n"
            "4. spill → inclua configuração de memória\n"
            "5. severity: critical=job falha ou 10x+ lento, high=3-10x, medium=1.5-3x, low<1.5x\n"
            "6. Retorne SOMENTE JSON válido, sem texto adicional\n\n"
            "Schema obrigatório:\n"
            '{"pattern": "skew|spill|...", "severity": "high|...", "confidence": 0.0-1.0, '
            '"bottleneck_stage_id": 2, "root_cause": "...", "recommendation": "...", '
            '"evidence": {"key_metric": "...", "key_value": "...", "expected_value": "..."}}'
        ),
        expected_output=(
            "JSON válido com todos os campos: pattern, severity, confidence, "
            "bottleneck_stage_id, root_cause, recommendation, evidence."
        ),
        agent=agent,
        context=[analyze_task],
        output_json=ApexFinding,
    )


# ── Validação de contrato ─────────────────────────────────────────────────────

def _validate_against_contract(finding: dict) -> dict:
    """
    Valida o finding contra contratos dos listener_*.yaml.
    Aplica: override de padrão inválido, escalação para Judge, e check de keywords.
    """
    # 1. Padrão reconhecido
    if finding.get("pattern") not in KNOWN_PATTERNS:
        logger.warning(f"[CONTRATO] Padrão '{finding.get('pattern')}' inválido → 'other'")
        finding["pattern"] = "other"

    # 2. Severity válida
    if finding.get("severity") not in SEVERITY_LEVELS:
        logger.warning(f"[CONTRATO] Severity '{finding.get('severity')}' inválida → 'medium'")
        finding["severity"] = "medium"

    # 3. Confidence < 0.6 → Judge
    confidence = float(finding.get("confidence", 0.0))
    if confidence < 0.6:
        logger.warning(f"[CONTRATO] Confidence {confidence:.2f} < 0.6 → escala para Tier 4 (Judge)")
        finding["needs_judge"] = True
        finding["judge_reason"] = f"confidence={confidence:.2f} < 0.6"
    else:
        finding["needs_judge"] = False

    # 4. Evidence presente
    evidence = finding.get("evidence")
    if not evidence or not isinstance(evidence, dict):
        logger.warning("[CONTRATO] Evidence ausente → possível alucinação")
        finding["contract_warning"] = "evidence_missing"
        finding["needs_judge"] = True

    # 5. Keywords obrigatórias na recommendation
    pattern = finding.get("pattern", "other")
    recommendation = finding.get("recommendation", "").lower()
    required_kws = PATTERN_KEYWORDS.get(pattern, [])
    if required_kws and not any(kw.lower() in recommendation for kw in required_kws):
        warn = finding.get("contract_warning", "")
        finding["contract_warning"] = (warn + " recommendation_keywords_missing").strip()
        logger.warning(f"[CONTRATO] Recommendation para '{pattern}' não menciona {required_kws}")

    return finding


# ── Pipeline principal ────────────────────────────────────────────────────────

def diagnose(app_id: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Pipeline Crew.ai: ClickHouse → MetricsAnalyzer → RecommendationWriter → finding validado.
    """
    logger.info(f"Iniciando diagnóstico Crew.ai | app_id={app_id} | model={model}")

    llm = _get_llm(model)

    analyzer  = build_metrics_analyzer(llm)
    writer    = build_recommendation_writer(llm)

    analyze_task = build_analyze_task(analyzer, app_id)
    rec_task     = build_recommendation_task(writer, app_id, analyze_task)

    crew = Crew(
        agents=[analyzer, writer],
        tasks=[analyze_task, rec_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # Extrair JSON do output
    raw = result.raw if hasattr(result, "raw") else str(result)
    raw = raw.strip()

    # Remove markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        finding = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            finding = json.loads(match.group())
        else:
            logger.error(f"Output inválido do Crew.ai: {raw[:300]}")
            raise ValueError(f"Crew.ai não retornou JSON válido: {raw[:200]}")

    # Validação de contrato
    finding = _validate_against_contract(finding)

    finding["app_id"]   = app_id
    finding["llm_model"] = model
    finding["pipeline"] = "crewai-1x"

    logger.info(f"Diagnóstico concluído: {finding.get('pattern')} | {finding.get('severity')} | confidence={finding.get('confidence')}")
    return finding


def persist_finding(finding: dict) -> None:
    """Persiste o finding no ClickHouse (apex.findings)."""
    try:
        ch = _get_ch()
        ch.insert(
            "apex.findings",
            [[
                finding["app_id"],
                finding.get("bottleneck_stage_id"),
                finding.get("pattern", "other"),
                finding.get("severity", "medium"),
                float(finding.get("confidence", 0.0)),
                finding.get("root_cause", ""),
                finding.get("recommendation", ""),
                finding.get("llm_model", DEFAULT_MODEL),
            ]],
            column_names=[
                "app_id", "stage_id", "pattern", "severity", "confidence",
                "root_cause", "recommendation", "llm_model",
            ],
        )
        logger.info("Finding persistido no ClickHouse")
    except Exception as e:
        logger.error(f"Erro ao persistir finding: {e}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Apex V1 — Diagnóstico Crew.ai")
    parser.add_argument("--app-id",    required=True,        help="Spark application ID")
    parser.add_argument("--model",     default=DEFAULT_MODEL, help="Modelo Anthropic")
    parser.add_argument("--no-persist",action="store_true",  help="Não salva no ClickHouse")
    args = parser.parse_args()

    finding = diagnose(args.app_id, args.model)
    if not args.no_persist:
        persist_finding(finding)

    print("\n" + "=" * 60)
    print("APEX FINDING (Crew.ai 1.x)")
    print("=" * 60)
    print(json.dumps(finding, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
