"""Run the autonomous Spark 4.1.2 G3/G5 loop end to end.

This runner is intentionally shell-oriented at the boundary and deterministic
inside Python. It records raw command output in one evidence log and fails the
process when the before/after telemetry does not improve.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex import apexlib
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.telemetry import build_telemetry
from apex.commander.telemetry_compare import compare_job_telemetry


COMPOSE_FILE = ROOT / "docker-compose.autonomous.yml"
SCENARIO = ROOT / "pacote-comum" / "scenarios" / "skew_on_join_30x.yaml"
GENERATOR = ROOT / "pacote-comum" / "generators" / "code_generator.py"
SPARK_MASTER_CONTAINER = "apex-autonomous-spark-master"
MINIO_CLIENT_IMAGE = "quay.io/minio/mc:RELEASE.2025-08-13T08-35-41Z"
NETWORK = "apex-autonomous_default"
BEFORE_JOB_ID = "f7-autonomous-before"
AFTER_JOB_ID = "f7-autonomous-after"
LISTENER_JAR = ROOT / "listener-jvm" / "build" / "libs" / "apex-spark-listener-0.1.0.jar"


@dataclass(frozen=True)
class LoopPaths:
    run_dir: Path
    evidence_log: Path
    before_job: Path
    after_job: Path
    before_eventlog: Path
    after_eventlog: Path
    store: Path


def make_paths(run_id: str) -> LoopPaths:
    run_dir = ROOT / "evidence" / "generated" / "f7-autonomous-loop" / run_id
    return LoopPaths(
        run_dir=run_dir,
        evidence_log=ROOT / "evidence" / f"f7-autonomous-stack-loop-{run_id}.log",
        before_job=run_dir / "skew_on_join_30x_before.py",
        after_job=run_dir / "skew_on_join_30x_after.py",
        before_eventlog=run_dir / "before_eventlog.zstd",
        after_eventlog=run_dir / "after_eventlog.zstd",
        store=run_dir / "store.ndjson",
    )


class EvidenceLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def line(self, text: str = "") -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(text + "\n")
        console_encoding = sys.stdout.encoding or "utf-8"
        safe_text = text.encode(console_encoding, errors="replace").decode(
            console_encoding,
            errors="replace",
        )
        print(safe_text)

    def section(self, title: str) -> None:
        self.line()
        self.line(f"## {title}")


def command_to_text(command: list[str]) -> str:
    return " ".join(command)


def run_command(
    command: list[str],
    logger: EvidenceLogger,
    *,
    cwd: Path = ROOT,
    timeout_seconds: int = 600,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    logger.line(f"$ {command_to_text(command)}")
    result = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout_seconds,
    )
    if result.stdout:
        logger.line(result.stdout.rstrip())
    if result.stderr:
        logger.line(result.stderr.rstrip())
    logger.line(f"exit_code={result.returncode}")
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed: {command_to_text(command)}")
    return result


def build_compose_command(*args: str) -> list[str]:
    return ["docker", "compose", "-f", str(COMPOSE_FILE), *args]


def build_listener_jar_command() -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{str((ROOT / 'listener-jvm').resolve())}:/home/gradle/project",
        "-w",
        "/home/gradle/project",
        "gradle:8.10.2-jdk17",
        "gradle",
        "--no-daemon",
        "clean",
        "jar",
    ]


def build_spark_submit_command(container_job_path: str) -> list[str]:
    return [
        "docker",
        "exec",
        SPARK_MASTER_CONTAINER,
        "/opt/spark/bin/spark-submit",
        "--master",
        "spark://spark-master:7077",
        container_job_path,
    ]


def build_fetch_eventlog_command(app_id: str, output_name: str) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "--network",
        NETWORK,
        "-v",
        f"{str((ROOT / 'evidence' / 'generated' / 'f7-autonomous-loop').resolve())}:/out",
        "--entrypoint",
        "/bin/sh",
        MINIO_CLIENT_IMAGE,
        "-lc",
        (
            "mc alias set local http://minio:9000 spv0 spv0spv0 >/dev/null && "
            f"mc cp local/spark-logs/events/eventlog_v2_{app_id}/events_1_{app_id}.zstd /out/{output_name}"
        ),
    ]


def generate_before_job(paths: LoopPaths, logger: EvidenceLogger) -> None:
    paths.run_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = _prepend_pythonpath(env.get("PYTHONPATH"), ROOT)
    logger.section("generate before job")
    result = subprocess.run(
        [sys.executable, str(GENERATOR), str(SCENARIO), str(paths.before_job)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        env=env,
    )
    logger.line(f"$ {sys.executable} {GENERATOR} {SCENARIO} {paths.before_job}")
    if result.stdout:
        logger.line(result.stdout.rstrip())
    if result.stderr:
        logger.line(result.stderr.rstrip())
    logger.line(f"exit_code={result.returncode}")
    if result.returncode != 0:
        raise RuntimeError("code generation failed")


def _prepend_pythonpath(current: str | None, root: Path) -> str:
    parts = [str(root)]
    if current:
        parts.append(current)
    return os.pathsep.join(parts)


def write_after_job(before_path: Path, after_path: Path) -> None:
    text = before_path.read_text(encoding="utf-8")
    text = text.replace(
        "from pyspark.sql.functions import col, rand, when, collect_list",
        "from pyspark.sql.functions import broadcast, col, rand, when, collect_list",
    )
    text = text.replace(
        '.config("spark.sql.adaptive.enabled", "false")',
        '.config("spark.sql.adaptive.enabled", "true")',
    )
    text = text.replace(
        '.config("spark.sql.adaptive.skewJoin.enabled", "false")',
        '.config("spark.sql.adaptive.skewJoin.enabled", "true")',
    )
    text = text.replace(
        '.config("spark.sql.adaptive.autoBroadcastJoinThreshold", "-1")',
        '.config("spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760")',
    )
    text = text.replace(
        'orders.join(customers.hint("shuffle_merge"), "customer_id", "inner")  # APEX::ANTIPATTERN',
        'orders.join(broadcast(customers), "customer_id", "inner")  # APEX::FIXED_BY_F7_LOOP',
    )
    after_path.write_text(text, encoding="utf-8")


def extract_app_id(output: str) -> str:
    app_ids = re.findall(r"app-\d{14}-\d+", output)
    if app_ids:
        return app_ids[-1]
    for line in output.splitlines():
        if "Submitted application" in line:
            return line.rsplit(" ", 1)[-1].strip()
    raise RuntimeError("spark-submit output did not include Submitted application")


def copy_job_to_container(job: Path, container_path: str, logger: EvidenceLogger) -> None:
    run_command(
        ["docker", "cp", str(job), f"{SPARK_MASTER_CONTAINER}:{container_path}"],
        logger,
        timeout_seconds=120,
    )


def submit_job(job: Path, container_path: str, logger: EvidenceLogger) -> str:
    copy_job_to_container(job, container_path, logger)
    result = run_command(
        build_spark_submit_command(container_path),
        logger,
        timeout_seconds=900,
    )
    return extract_app_id((result.stdout or "") + "\n" + (result.stderr or ""))


def fetch_eventlog(app_id: str, destination: Path, logger: EvidenceLogger) -> None:
    output_name = destination.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_destination = ROOT / "evidence" / "generated" / "f7-autonomous-loop" / output_name
    if temp_destination.exists():
        temp_destination.unlink()
    run_command(build_fetch_eventlog_command(app_id, output_name), logger, timeout_seconds=300)
    if not temp_destination.exists():
        raise RuntimeError(f"event log was not fetched for {app_id}")
    shutil.move(str(temp_destination), str(destination))


def append_eventlog_to_store(eventlog: Path, store: Path, job_id: str) -> dict[str, Any]:
    events = apexlib.read_events(str(eventlog))
    envelope = build_telemetry(events, job_id=job_id)
    append_envelope(store, envelope)
    return envelope


def assert_gate(compare: dict[str, Any]) -> None:
    before = compare["before"]
    after = compare["after"]
    if compare["status"] != "improved":
        raise RuntimeError(f"expected improved status, got {compare['status']}")
    if before["metrics"]["finding_count"] < 1:
        raise RuntimeError("before job must have at least one finding")
    if after["metrics"]["finding_count"] != 0:
        raise RuntimeError("after job must be clean")
    if after["metrics"]["max_skew_ratio"] >= before["metrics"]["max_skew_ratio"]:
        raise RuntimeError("after max skew ratio did not improve")
    if after["metrics"]["total_spilled_bytes"] > before["metrics"]["total_spilled_bytes"]:
        raise RuntimeError("after shuffle/spill bytes regressed")


def run_loop(args: argparse.Namespace) -> int:
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    paths = make_paths(run_id)
    logger = EvidenceLogger(paths.evidence_log)
    started = time.perf_counter()
    logger.line("apex autonomous stack loop")
    logger.line(f"run_id={run_id}")
    logger.line("spark_target=4.1.2")
    logger.line(f"compose_file={COMPOSE_FILE}")

    if args.dry_run:
        logger.section("dry run commands")
        logger.line(command_to_text(build_listener_jar_command()))
        logger.line(command_to_text(build_compose_command("build", "spark-master", "spark-worker")))
        logger.line(command_to_text(build_compose_command("up", "-d")))
        logger.line(command_to_text(build_spark_submit_command("/tmp/apex-before.py")))
        logger.line(command_to_text(build_fetch_eventlog_command("app-example", "before_eventlog.zstd")))
        logger.line("dry_run_status=success")
        return 0

    generate_before_job(paths, logger)
    write_after_job(paths.before_job, paths.after_job)

    logger.section("build listener jar")
    if not args.skip_build:
        run_command(build_listener_jar_command(), logger, timeout_seconds=1800)
    if not LISTENER_JAR.exists():
        raise RuntimeError(f"listener jar missing after build: {LISTENER_JAR}")
    logger.line(f"listener_jar={LISTENER_JAR}")

    logger.section("compose build/up")
    if not args.skip_build:
        run_command(build_compose_command("build", "spark-master", "spark-worker"), logger, timeout_seconds=1800)
    run_command(build_compose_command("up", "-d"), logger, timeout_seconds=600)
    run_command(build_compose_command("ps"), logger, timeout_seconds=120)

    logger.section("submit before")
    before_app_id = submit_job(paths.before_job, "/tmp/apex-f7-before.py", logger)
    logger.line(f"before_app_id={before_app_id}")
    fetch_eventlog(before_app_id, paths.before_eventlog, logger)
    before_envelope = append_eventlog_to_store(paths.before_eventlog, paths.store, BEFORE_JOB_ID)
    before_findings = diagnose_findings(paths.store, BEFORE_JOB_ID)
    logger.line("before_envelope=" + json.dumps(before_envelope, sort_keys=True))
    logger.line("before_findings=" + json.dumps(before_findings, sort_keys=True))

    logger.section("submit after")
    after_app_id = submit_job(paths.after_job, "/tmp/apex-f7-after.py", logger)
    logger.line(f"after_app_id={after_app_id}")
    fetch_eventlog(after_app_id, paths.after_eventlog, logger)
    after_envelope = append_eventlog_to_store(paths.after_eventlog, paths.store, AFTER_JOB_ID)
    after_findings = diagnose_findings(paths.store, AFTER_JOB_ID)
    logger.line("after_envelope=" + json.dumps(after_envelope, sort_keys=True))
    logger.line("after_findings=" + json.dumps(after_findings, sort_keys=True))

    logger.section("compare")
    compare = compare_job_telemetry(paths.store, BEFORE_JOB_ID, AFTER_JOB_ID)
    logger.line("compare=" + json.dumps(compare, sort_keys=True))
    assert_gate(compare)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    logger.line(f"loop_status=success elapsed_ms={elapsed_ms}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", help="stable evidence run id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    return run_loop(parse_args(argv or sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
