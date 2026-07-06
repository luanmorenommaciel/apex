#!/usr/bin/env python3
"""
Apex V1 — Rolling Log Poller
Bridge para "real-time": watch MinIO a cada N segundos, detecta novos jobs,
ingesta no ClickHouse e dispara diagnóstico Crew.ai automaticamente.

Uso:
    python ingest/log_poller.py
    python ingest/log_poller.py --interval 30 --no-diagnose

Env vars:
    APEX_CH_HOST, APEX_CH_PORT, APEX_CH_USER, APEX_CH_PASSWORD
    MINIO_ENDPOINT  (default: http://localhost:19000)
    MINIO_ACCESS_KEY (default: minioadmin)
    MINIO_SECRET_KEY (default: minioadmin)
    SPARK_LOGS_BUCKET (default: spark-logs)
    POLL_INTERVAL_SECONDS (default: 15)
    ANTHROPIC_API_KEY (para trigger do diagnóstico)

Fluxo:
    1. A cada POLL_INTERVAL segundos, lista prefixos eventlog_v2_* no MinIO
    2. Compara com app_ids já processados (estado em memória + ClickHouse)
    3. Para cada app_id novo:
       a. Baixa o event log para /tmp/apex/
       b. Chama event_log_ingest.py (popula stage_metrics + task_metrics)
       c. Chama crew_diagnose.py (gera ApexFinding e persiste em apex.findings)
       d. Imprime o finding no terminal
"""
import os
import sys
import time
import signal
import logging
import argparse
import tempfile
from pathlib import Path
from datetime import datetime

import clickhouse_connect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("apex.poller")

# ── Config ─────────────────────────────────────────────────────────────────────
CH_HOST      = os.getenv("APEX_CH_HOST",       "localhost")
CH_PORT      = int(os.getenv("APEX_CH_PORT",   "8123"))
CH_USER      = os.getenv("APEX_CH_USER",       "spv0")
CH_PASSWORD  = os.getenv("APEX_CH_PASSWORD",   "spv0clickhouse123")

MINIO_ENDPOINT   = os.getenv("MINIO_ENDPOINT",      "http://localhost:19000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY",    "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY",    "minioadmin")
SPARK_BUCKET     = os.getenv("SPARK_LOGS_BUCKET",   "spark-logs")
POLL_INTERVAL    = int(os.getenv("POLL_INTERVAL_SECONDS", "15"))

SPARK_LOGS_DIR   = os.getenv("SPARK_LOGS_DIR",      "/spark-logs")

# ── MinIO client ───────────────────────────────────────────────────────────────

def _get_minio():
    try:
        from minio import Minio
        endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
        secure = MINIO_ENDPOINT.startswith("https://")
        return Minio(endpoint, access_key=MINIO_ACCESS_KEY,
                     secret_key=MINIO_SECRET_KEY, secure=secure)
    except ImportError:
        return None


def list_app_ids_minio(mc) -> list[str]:
    """Lista app_ids disponíveis no MinIO via prefixo eventlog_v2_."""
    try:
        objects = mc.list_objects(SPARK_BUCKET, prefix="events/eventlog_v2_",
                                  recursive=False)
        app_ids = []
        for obj in objects:
            # Nome: events/eventlog_v2_app-20260706010516-0004/
            name = obj.object_name.rstrip("/").split("/")[-1]
            if name.startswith("eventlog_v2_"):
                app_id = name[len("eventlog_v2_"):]
                app_ids.append(app_id)
        return app_ids
    except Exception as e:
        logger.warning(f"MinIO listing failed: {e}")
        return []


def list_app_ids_local() -> list[str]:
    """Fallback: lista app_ids nos event logs montados localmente."""
    base = Path(SPARK_LOGS_DIR)
    if not base.exists():
        return []
    return [
        d.name[len("eventlog_v2_"):]
        for d in base.iterdir()
        if d.is_dir() and d.name.startswith("eventlog_v2_")
    ]


# ── ClickHouse helpers ─────────────────────────────────────────────────────────

def get_ch():
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT,
        username=CH_USER, password=CH_PASSWORD,
    )


def already_ingested(ch, app_id: str) -> bool:
    """Verifica se app_id já tem dados em stage_metrics."""
    rows = ch.query(
        "SELECT count() FROM apex.stage_metrics WHERE app_id = {app_id:String}",
        parameters={"app_id": app_id},
    ).result_rows
    return rows[0][0] > 0


def already_diagnosed(ch, app_id: str) -> bool:
    """Verifica se app_id já tem finding em apex.findings."""
    rows = ch.query(
        "SELECT count() FROM apex.findings WHERE app_id = {app_id:String}",
        parameters={"app_id": app_id},
    ).result_rows
    return rows[0][0] > 0


# ── Ingest + Diagnose ──────────────────────────────────────────────────────────

def ingest_app(app_id: str) -> bool:
    """Chama event_log_ingest.py para popular ClickHouse."""
    here = Path(__file__).parent
    ingest_script = here / "event_log_ingest.py"

    import subprocess
    env = os.environ.copy()
    env.update({
        "APEX_CH_HOST":     CH_HOST,
        "APEX_CH_PORT":     str(CH_PORT),
        "APEX_CH_USER":     CH_USER,
        "APEX_CH_PASSWORD": CH_PASSWORD,
        "SPARK_LOGS_DIR":   SPARK_LOGS_DIR,
    })
    result = subprocess.run(
        [sys.executable, str(ingest_script), app_id],
        capture_output=True, text=True, env=env,
    )
    if result.returncode != 0:
        logger.error(f"[ingest] {app_id} FAILED:\n{result.stderr[-500:]}")
        return False
    logger.info(f"[ingest] {app_id} OK")
    if result.stdout:
        for line in result.stdout.splitlines():
            if any(k in line for k in ["stage=", "tasks=", "SKEW", "✓", "Complete"]):
                logger.info(f"  {line.strip()}")
    return True


def diagnose_app(app_id: str) -> dict | None:
    """Chama crew_diagnose.py e retorna o finding."""
    here = Path(__file__).parent.parent
    diagnose_script = here / "analysis" / "crew_diagnose.py"

    import subprocess, json
    env = os.environ.copy()
    env.update({
        "APEX_CH_HOST":     CH_HOST,
        "APEX_CH_PORT":     str(CH_PORT),
        "APEX_CH_USER":     CH_USER,
        "APEX_CH_PASSWORD": CH_PASSWORD,
        "CREWAI_DISABLE_TELEMETRY": "true",
        "OTEL_SDK_DISABLED":        "true",
    })
    result = subprocess.run(
        [sys.executable, str(diagnose_script), "--app-id", app_id],
        capture_output=True, text=True, env=env,
    )
    if result.returncode != 0:
        logger.error(f"[diagnose] {app_id} FAILED:\n{result.stderr[-500:]}")
        return None

    # Extrai JSON do output (após a linha de separadores)
    import re
    match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    logger.warning(f"[diagnose] {app_id}: output não é JSON válido")
    return None


# ── Print Finding ──────────────────────────────────────────────────────────────

SEVERITY_COLORS = {
    "critical": "\033[91m",  # red
    "high":     "\033[93m",  # yellow
    "medium":   "\033[94m",  # blue
    "low":      "\033[92m",  # green
}
RESET = "\033[0m"


def print_finding(finding: dict):
    sev   = finding.get("severity", "medium")
    color = SEVERITY_COLORS.get(sev, "")
    print(f"\n{'='*60}")
    print(f"{color}⚡ APEX FINDING — {finding.get('app_id', '?')}{RESET}")
    print(f"{'='*60}")
    print(f"  Pattern:     {finding.get('pattern', '?').upper()}")
    print(f"  Severity:    {color}{sev.upper()}{RESET}")
    print(f"  Confidence:  {finding.get('confidence', 0):.0%}")
    print(f"  Stage:       {finding.get('bottleneck_stage_id', 'N/A')}")
    print(f"\n  Root cause:  {finding.get('root_cause', '')}")
    print(f"\n  Fix:         {finding.get('recommendation', '')}")
    ev = finding.get("evidence", {})
    if ev:
        print(f"\n  Evidence:    {ev.get('key_metric')} = {ev.get('key_value')}")
        print(f"               expected: {ev.get('expected_value')}")
    if finding.get("needs_judge"):
        print(f"\n  ⚠️  Escalado para Tier 4 (Judge): {finding.get('judge_reason')}")
    print(f"{'='*60}\n")


# ── Main poll loop ─────────────────────────────────────────────────────────────

def poll_once(ch, seen: set, diagnose: bool) -> set:
    """Uma iteração do poll. Retorna set atualizado de app_ids vistos."""
    mc = _get_minio()
    if mc:
        app_ids = list_app_ids_minio(mc)
        source = "MinIO"
    else:
        app_ids = list_app_ids_local()
        source = "local"

    if not app_ids:
        logger.debug(f"[poll] Nenhum app_id encontrado via {source}")
        return seen

    new_ids = [a for a in app_ids if a not in seen]
    if not new_ids:
        logger.debug(f"[poll] {len(app_ids)} apps conhecidos, nenhum novo")
        return seen

    logger.info(f"[poll] {len(new_ids)} novo(s) app_id via {source}: {new_ids}")

    for app_id in new_ids:
        seen.add(app_id)

        # Já ingerido?
        if already_ingested(ch, app_id):
            logger.info(f"[poll] {app_id} já está no ClickHouse — skip ingest")
        else:
            if not ingest_app(app_id):
                continue

        # Já diagnosticado?
        if already_diagnosed(ch, app_id):
            logger.info(f"[poll] {app_id} já tem finding — skip diagnose")
            continue

        if diagnose:
            logger.info(f"[poll] Disparando diagnóstico para {app_id}...")
            finding = diagnose_app(app_id)
            if finding:
                print_finding(finding)
        else:
            logger.info(f"[poll] {app_id} ingerido. Use --diagnose para análise LLM.")

    return seen


def run_poller(interval: int, diagnose: bool):
    ch = get_ch()
    seen: set = set()

    # Seed: app_ids já no ClickHouse (não processa histórico ao iniciar)
    rows = ch.query("SELECT DISTINCT app_id FROM apex.stage_metrics").result_rows
    for r in rows:
        seen.add(r[0])
    logger.info(f"[poll] Iniciando — {len(seen)} app_ids já conhecidos no ClickHouse")
    logger.info(f"[poll] Intervalo: {interval}s | Diagnóstico automático: {diagnose}")
    logger.info(f"[poll] Ctrl+C para parar\n")

    def _shutdown(sig, frame):
        logger.info("[poll] Encerrando...")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        try:
            seen = poll_once(ch, seen, diagnose)
        except Exception as e:
            logger.error(f"[poll] Erro inesperado: {e}")
        time.sleep(interval)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apex — Rolling Log Poller")
    parser.add_argument("--interval",    type=int, default=POLL_INTERVAL,
                        help=f"Segundos entre polls (default: {POLL_INTERVAL})")
    parser.add_argument("--no-diagnose", action="store_true",
                        help="Só ingesta, não dispara diagnóstico LLM")
    parser.add_argument("--once",        action="store_true",
                        help="Roda uma vez e sai (útil para testes)")
    args = parser.parse_args()

    diagnose = not args.no_diagnose

    if args.once:
        ch = get_ch()
        seen: set = set()
        poll_once(ch, seen, diagnose)
    else:
        run_poller(args.interval, diagnose)
