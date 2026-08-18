#!/usr/bin/env python3
"""R9D orchestrator: JAR on/off overhead A/B + driver/listener soak.

Predeclared in docs/convergence/C54-R9D-OVERHEAD-SOAK-AB-PLANO-2026-07-31.md.

Metric separation (per C54):
- PRIMARY: submit-to-exit duration of each spark-submit job, measured by the
  harness at the SAME point in both arms (Stopwatch around the docker compose
  exec spark-submit call), reported as APEX_SUBMIT_RESULT submit_to_exit_ms.
  Per-run primary = sum of the run's job durations (generate_data + scenarios).
- FUNCTIONAL GATES (outside the clocked window): ON arm keeps the canonical
  ClickHouse assertions; OFF arm checks scenario exit codes + APEX_SESSION.
- SECONDARY (ON only, never added to overhead): telemetry-delivery latency
  of the ClickHouse assertions (APEX_TELEMETRY_RESULT delivery_latency_ms)
  and the soak ClickHouse delivery wait (delivery_waited_seconds).
- Soak PRIMARY: the job-internal APEX_SOAK_COMPLETE elapsed_ms.

- Checkpoints to dev/out/r9d-state.json after every unit; reruns skip
  completed units, so a timed-out run can resume.
- Writes ONLY ignored local logs plus one sanitized evidence manifest.
- Never prints secrets: .apex/*.env values are only forwarded to subprocesses.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "dev"
OUT = DEV / "out"
EVIDENCE = ROOT / "evidence" / "r9d-overhead-soak-2026-07-31.json"
STATE = OUT / "r9d-state.json"

REPS = int(os.environ.get("R9D_REPS", "10"))
WARMUP = int(os.environ.get("R9D_WARMUP", "2"))
SOAK_CYCLES = int(os.environ.get("R9D_SOAK_CYCLES", "30"))
SAMPLE_SECONDS = int(os.environ.get("R9D_SAMPLE_SECONDS", "5"))
EXPECTED_BRANCH = os.environ.get("R9D_EXPECTED_BRANCH")
EXECUTE_TOKEN = os.environ.get("R9D_EXECUTE", "")
ACCEPT_BANDS = os.environ.get("R9D_ACCEPT_PROPOSED_BANDS", "") == "1"
STATS_CONTAINERS = ["apex-dev-spark-master-1", "apex-dev-spark-worker-1", "apex-otel-collector"]
DOCKER_BIN_DIRS = ["/Applications/Docker.app/Contents/Resources/bin", "/usr/local/bin", "/opt/homebrew/bin"]

SUBMIT_RE = re.compile(r"APEX_SUBMIT_RESULT name=(\S+) exit=(-?\d+) submit_to_exit_ms=(\d+)")
TELEMETRY_RE = re.compile(r"APEX_TELEMETRY_RESULT .*?delivery_latency_ms=(\d+)")
SOAK_COMPLETE_RE = re.compile(r"APEX_SOAK_COMPLETE .*?elapsed_ms=(\d+)")
SESSION_RE = re.compile(r"APEX_SESSION job_id=")

# P2: every e2e repetition must contain exactly these five uniquely named
# submit markers; a partial set invalidates the repetition's primary metric.
EXPECTED_JOBS = ("generate_data", "skew_join", "spill", "bad_shuffle", "driver_oom")
# P1: the checkpoint is only reusable within the identical run fingerprint.
HARNESS_FILES = (
    DEV / "scripts" / "e2e_canonical.ps1",
    DEV / "scripts" / "r9d_e2e_canonical_noplugin.ps1",
    DEV / "scripts" / "soak_driver_listener.sh",
    Path(__file__).resolve(),
)
# Containers whose images execute the matrix workload and its telemetry path.
MATRIX_CONTAINERS = (
    "apex-dev-spark-master-1",
    "apex-dev-spark-worker-1",
    "apex-dev-spark-history-1",
    "apex-dev-minio-1",
    "apex-otel-collector",
    "apex-infra-clickhouse",
    "apex-infra-mongodb",
    "apex-infra-hyperdx",
)
COMPOSE_FILES = (
    DEV / "docker-compose.yml",
    DEV / "docker-compose.c3-otlp.yml",
    DEV / "docker-compose.package.yml",
)


def log(msg: str) -> None:
    print(f"[r9d {datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    env = kwargs.pop("env", os.environ.copy())
    env["PATH"] = ":".join(DOCKER_BIN_DIRS) + ":" + env.get("PATH", "")
    return subprocess.run(cmd, env=env, **kwargs)


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = ":".join(DOCKER_BIN_DIRS) + ":" + env.get("PATH", "")
    env["APEX_SPARK_DEFAULTS_PATH"] = str(ROOT / ".apex" / "spark-defaults.conf")
    return env


def runtime_identity() -> dict:
    """Immutable runtime identifiers for the matrix. Stores only image
    digests, image names and a HASH of the effective Compose configuration;
    never env values, .env content or secrets."""
    digests: dict[str, str] = {}
    env = base_env()
    for name in MATRIX_CONTAINERS:
        proc = run(["docker", "inspect", "-f", "{{.Image}}", name], env=env, capture_output=True, text=True)
        if proc.returncode != 0 or not proc.stdout.strip():
            raise SystemExit(f"preflight: could not inspect image digest of {name}")
        digests[name] = proc.stdout.strip()
    compose_cmd = ["docker", "compose"]
    for compose_file in COMPOSE_FILES:
        compose_cmd += ["-f", str(compose_file)]
    compose_cmd += ["--env-file", str(ROOT / ".apex" / "dev.env"), "config"]
    cfg = run(compose_cmd, cwd=DEV, env=env, capture_output=True, text=True)
    if cfg.returncode != 0:
        raise SystemExit("preflight: docker compose config failed for the dev matrix")
    images = run(compose_cmd + ["--images"], cwd=DEV, env=env, capture_output=True, text=True)
    server = run(["docker", "version", "-f", "{{.Server.Version}}"], env=env, capture_output=True, text=True)
    return {
        "container_image_digests": digests,
        "compose_config_sha256": hashlib.sha256(cfg.stdout.encode()).hexdigest(),
        "compose_image_names": sorted(images.stdout.split()) if images.returncode == 0 else [],
        "docker_server_version": server.stdout.strip(),
    }


def preflight() -> tuple[str, dict]:
    if EXECUTE_TOKEN != "1":
        raise SystemExit(
            "preflight: R9D_EXECUTE=1 is required after explicit operator "
            "authorization; refusing to start the matrix"
        )
    branch = run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if EXPECTED_BRANCH and branch != EXPECTED_BRANCH:
        raise SystemExit(f"preflight: branch {branch!r} != {EXPECTED_BRANCH!r}")
    dirty = run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SystemExit(
            "preflight: git worktree is dirty; commit or stash before running "
            "so the checkpoint binds to an exact HEAD\n" + dirty
        )
    head = run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    for tool in ("pwsh", "uv", "docker", "bash"):
        if run(["which", tool], capture_output=True).returncode != 0:
            raise SystemExit(f"preflight: {tool} not found on PATH")
    ps = run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True).stdout.split()
    for name in ("apex-dev-spark-master-1", "apex-otel-collector", "apex-infra-clickhouse"):
        if name not in ps:
            raise SystemExit(f"preflight: container {name} is not running")
    if any(name.startswith("apex-r9d-") for name in ps):
        raise SystemExit("preflight: leftover apex-r9d-* container found")
    required_apex_files = (
        ROOT / ".apex" / "infra.env",
        ROOT / ".apex" / "dev.env",
        ROOT / ".apex" / "spark-defaults.conf",
    )
    missing_files = [f.name for f in required_apex_files if not f.exists()]
    if missing_files:
        raise SystemExit(
            f"preflight: required .apex file(s) missing ({', '.join(missing_files)}); "
            "run make bootstrap first"
        )
    OUT.mkdir(parents=True, exist_ok=True)
    identity = runtime_identity()
    return head, identity


def canonical_env() -> dict[str, str]:
    env = base_env()
    infra = load_env_file(ROOT / ".apex" / "infra.env")
    port = infra.get("CLICKHOUSE_HTTP_HOST_PORT", "8123")
    # Secrets are forwarded to the subprocess only; never logged or printed.
    env["APEX_CANONICAL_CH_PASSWORD"] = infra.get("CLICKHOUSE_PASSWORD", "")
    env["APEX_CANONICAL_CH_USER"] = infra.get("CLICKHOUSE_USER", "default")
    env["APEX_CANONICAL_CH_URL"] = f"http://127.0.0.1:{port}"
    env["CLICKHOUSE_HOST"] = "127.0.0.1"
    env["CLICKHOUSE_PORT"] = port
    env["CLICKHOUSE_USER"] = env["APEX_CANONICAL_CH_USER"]
    env["CLICKHOUSE_PASSWORD"] = env["APEX_CANONICAL_CH_PASSWORD"]
    env["CLICKHOUSE_DATABASE"] = "apex"
    return env


class StatsSampler(threading.Thread):
    def __init__(self, csv_path: Path):
        super().__init__(daemon=True)
        self.csv_path = csv_path
        # NOTE: named _stop_event, not _stop: threading.Thread.join() calls the
        # internal self._stop() method; an instance attribute with that name
        # shadows it and crashes with "TypeError: 'Event' object is not callable".
        self._stop_event = threading.Event()

    def run(self) -> None:
        with self.csv_path.open("w") as fh:
            fh.write("timestamp_utc,container,cpu_percent,mem_usage,mem_percent\n")
            while not self._stop_event.is_set():
                stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                result = run(
                    ["docker", "stats", "--no-stream", "--format",
                     "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}"] + STATS_CONTAINERS,
                    capture_output=True, text=True,
                )
                for line in result.stdout.splitlines():
                    if line.strip():
                        fh.write(f"{stamp},{line}\n")
                fh.flush()
                self._stop_event.wait(SAMPLE_SECONDS)

    def stop(self) -> None:
        self._stop_event.set()


def run_fingerprint(head: str, identity: dict) -> str:
    """Binds a checkpoint to the exact measurement run: HEAD, matrix
    parameters, the byte content of every harness file and the effective
    runtime identity (image digests, Compose config hash, Docker server)."""
    digest = hashlib.sha256()
    digest.update(head.encode())
    digest.update(
        f"reps={REPS};warmup={WARMUP};soak_cycles={SOAK_CYCLES};"
        f"sample_seconds={SAMPLE_SECONDS};branch={EXPECTED_BRANCH}".encode()
    )
    for path in HARNESS_FILES:
        digest.update(str(path.name).encode())
        digest.update(path.read_bytes())
    digest.update(json.dumps(identity, sort_keys=True).encode())
    return digest.hexdigest()


def load_state(fingerprint: str, started_at_iso: str) -> dict:
    if STATE.exists():
        state = json.loads(STATE.read_text())
        if state.get("units") and "first_started_at_utc" not in state:
            raise SystemExit(
                "Legacy checkpoint found (has units but no first_started_at_utc). "
                "Refusing to incorrectly timestamp a resumed run as a fresh start. "
                "Archive or delete the state file to start a new matrix."
            )
        if state.get("fingerprint") != fingerprint:
            drop_units_raw = os.environ.get("R9D_RESUME_DROP_UNITS", "")
            reason = os.environ.get("R9D_RESUME_REASON", "")
            if drop_units_raw and reason:
                drop_ids = [u.strip() for u in drop_units_raw.split(",") if u.strip()]
                for drop_id in drop_ids:
                    unit = next((u for u in state.get("units", []) if u["unit_id"] == drop_id), None)
                    if not unit:
                        raise SystemExit(f"Cannot drop {drop_id}: not found in state.")
                    if unit.get("exit_code") != 0:
                        continue
                    if unit["unit_id"].startswith("e2e-"):
                        if unit.get("primary_total_s") is None or unit.get("measurement_error"):
                            continue
                    elif unit["unit_id"].startswith("soak-"):
                        log_path = ROOT / unit["log"]
                        if not log_path.exists():
                            raise SystemExit(f"Refusing to drop {drop_id}: required soak log {log_path} is missing.")
                        soak_res = parse_soak(log_path)
                        if soak_res.get("status") != "passed":
                            continue
                    raise SystemExit(f"Refusing to drop valid unit {drop_id}")

                prev_fingerprint = state.get("fingerprint")
                state["units"] = [u for u in state.get("units", []) if u["unit_id"] not in drop_ids]
                state["fingerprint"] = fingerprint
                state.setdefault("provenance", []).append({
                    "recovery": {
                        "previous_fingerprint": prev_fingerprint,
                        "new_fingerprint": fingerprint,
                        "dropped_unit_ids": drop_ids,
                        "reason": reason,
                        "timestamp": started_at_iso
                    }
                })
                log(f"Recovered checkpoint: dropped {drop_ids} due to {reason!r}")
                return state

            raise SystemExit(
                "checkpoint fingerprint mismatch: dev/out/r9d-state.json belongs "
                "to a different HEAD, parameter set or harness version. Refusing "
                "to mix measurements; archive or delete the state file to start "
                "a fresh run."
            )
        return state
    return {"fingerprint": fingerprint, "units": []}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2))


def unit_done(state: dict, unit_id: str) -> bool:
    return any(u["unit_id"] == unit_id for u in state["units"])


def run_unit(state: dict, unit_id: str, cmd: list[str], cwd: Path, env: dict[str, str]) -> dict:
    if unit_done(state, unit_id):
        log(f"skip {unit_id} (already completed)")
        return next(u for u in state["units"] if u["unit_id"] == unit_id)
    log_path = OUT / f"r9d-{unit_id}.log"
    csv_path = OUT / f"r9d-{unit_id}-stats.csv"
    log(f"start {unit_id}")
    sampler = StatsSampler(csv_path)
    sampler.start()
    started = time.monotonic()
    with log_path.open("w") as fh:
        proc = run(cmd, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT)
    duration_s = round(time.monotonic() - started, 3)
    sampler.stop()
    sampler.join(timeout=SAMPLE_SECONDS + 5)
    record = {
        "unit_id": unit_id,
        "exit_code": proc.returncode,
        "harness_wall_s": duration_s,
        "log": str(log_path.relative_to(ROOT)),
        "stats": str(csv_path.relative_to(ROOT)),
    }
    state["units"].append(record)
    save_state(state)
    log(f"done {unit_id} exit={proc.returncode} harness_wall_s={duration_s}")
    return record


def attach_e2e_metrics(state: dict, record: dict) -> None:
    """Parse the unit log: PRIMARY submit-to-exit timings and, on the ON arm,
    SECONDARY telemetry-gate latencies. Gates are outside the clocked window.
    A repetition only yields a primary metric when it contains exactly the
    five expected, uniquely named submit markers (P2)."""
    text = (ROOT / record["log"]).read_text(errors="replace")
    markers = [(name, int(ms)) for name, _, ms in SUBMIT_RE.findall(text)]
    names = [name for name, _ in markers]
    telemetry_ms = [int(m) for m in TELEMETRY_RE.findall(text)]
    record["primary_jobs"] = names
    record["primary_submit_ms"] = [ms for _, ms in markers]
    markers_ok = (
        len(markers) == len(EXPECTED_JOBS)
        and len(set(names)) == len(names)
        and sorted(names) == sorted(EXPECTED_JOBS)
    )
    if markers_ok:
        record["primary_total_s"] = round(sum(ms for _, ms in markers) / 1000, 3)
        record.pop("measurement_error", None)
    else:
        record["primary_total_s"] = None
        record["measurement_error"] = (
            f"expected exactly {len(EXPECTED_JOBS)} unique markers "
            f"{list(EXPECTED_JOBS)}, got {names}"
        )
    record["telemetry_gate_ms"] = telemetry_ms or None
    record["session_marker_present"] = bool(SESSION_RE.search(text))
    save_state(state)


def e2e_command(arm: str) -> list[str]:
    script = "e2e_canonical.ps1" if arm == "on" else "r9d_e2e_canonical_noplugin.ps1"
    return [
        "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
        str(DEV / "scripts" / script),
        "-EnvFile", str(ROOT / ".apex" / "dev.env"),
        "-AdditionalComposeFile", str(DEV / "docker-compose.package.yml"),
    ]


def parse_soak(unit_log: Path) -> dict:
    fields: dict[str, str] = {}
    for line in reversed(unit_log.read_text(errors="replace").splitlines()):
        if "SOAK_RESULT" in line:
            fields = dict(
                (k, v) for k, _, v in
                (token.partition("=") for token in line.split() if "=" in token)
            )
            break
    inner = fields.get("log")
    if inner:
        inner_text = (DEV / inner).read_text(errors="replace") if (DEV / inner).exists() else ""
        match = SOAK_COMPLETE_RE.search(inner_text)
        if match:
            fields["job_elapsed_ms"] = match.group(1)
    return fields


def summarize(durations: list[float]) -> dict:
    if not durations:
        return {"n": 0}
    q1 = q3 = None
    if len(durations) >= 4:
        q1, _, q3 = statistics.quantiles(durations, n=4)
    return {
        "n": len(durations),
        "median_s": statistics.median(durations),
        "min_s": min(durations),
        "max_s": max(durations),
        "iqr_s": (q3 - q1) if q1 is not None else None,
    }



def classify(
    *,
    functional_failures: list[str],
    measurement_missing: list[str],
    overhead_pct: float | None,
    accept_bands: bool,
) -> str:
    """Regra de decisão predeclarada em C54. Pura: sem I/O, sem globais."""
    if functional_failures:
        return "rejected"
    if measurement_missing or overhead_pct is None:
        return "inconclusive"
    if not accept_bands:
        return "measurement_complete_pending_operator_threshold_approval"
    if overhead_pct <= 10:
        return "approved"
    if overhead_pct <= 20:
        return "inconclusive"
    return "rejected"


def main() -> int:
    started_at = datetime.now(timezone.utc)
    started_at_iso = started_at.isoformat()
    head, identity = preflight()
    log(f"preflight ok branch={EXPECTED_BRANCH} head={head[:12]} reps={REPS} warmup={WARMUP} soak_cycles={SOAK_CYCLES}")
    fingerprint = run_fingerprint(head, identity)
    state = load_state(fingerprint, started_at_iso)
    state.setdefault("first_started_at_utc", started_at_iso)
    state.setdefault("provenance", []).append({
        "invocation_started_utc": started_at_iso,
        "fingerprint": fingerprint,
        "units_present_at_start": len(state.get("units", [])),
    })
    save_state(state)
    env = canonical_env()

    sequence: list[tuple[str, str, int]] = []
    for i in range(1, WARMUP + 1):
        for arm in ("off", "on"):
            sequence.append(("warmup", arm, i))
    for i in range(1, REPS + 1):
        for arm in ("on", "off"):
            sequence.append(("valid", arm, i))

    functional_failures: list[str] = []
    measurement_missing: list[str] = []
    for phase, arm, i in sequence:
        unit_id = f"e2e-{arm}-{phase}-{i:02d}"
        record = run_unit(state, unit_id, e2e_command(arm), DEV, env)
        attach_e2e_metrics(state, record)
        if record["exit_code"] != 0:
            functional_failures.append(unit_id)
        if phase == "valid" and record.get("primary_total_s") is None:
            measurement_missing.append(unit_id)

    soak_results: dict[str, dict] = {}
    for arm in ("on", "off"):
        unit_id = f"soak-{arm}"
        soak_env = dict(env)
        soak_env["APEX_SOAK_CYCLES"] = str(SOAK_CYCLES)
        soak_env["APEX_SOAK_PLUGIN"] = arm
        record = run_unit(
            state, unit_id,
            ["bash", "scripts/soak_driver_listener.sh"], DEV, soak_env,
        )
        soak_results[arm] = parse_soak(ROOT / record["log"])
        soak_results[arm]["exit_code"] = record["exit_code"]
        soak_results[arm]["harness_wall_s"] = record["harness_wall_s"]
        if record["exit_code"] != 0 or soak_results[arm].get("status") != "passed":
            functional_failures.append(unit_id)

    def primaries(arm: str) -> list[float]:
        return [
            u["primary_total_s"] for u in state["units"]
            if u["unit_id"].startswith(f"e2e-{arm}-valid") and u.get("primary_total_s") is not None
        ]

    stats_on, stats_off = summarize(primaries("on")), summarize(primaries("off"))
    overhead_pct = None
    if stats_on.get("median_s") and stats_off.get("median_s"):
        overhead_pct = round((stats_on["median_s"] - stats_off["median_s"]) / stats_off["median_s"] * 100, 2)

    decision = classify(
        functional_failures=functional_failures,
        measurement_missing=measurement_missing,
        overhead_pct=overhead_pct,
        accept_bands=ACCEPT_BANDS,
    )

    completed_at = datetime.now(timezone.utc)
    completed_at_iso = completed_at.isoformat()

    artifact = {
        "gate": "R9D",
        "date": "2026-07-31",
        "started_at_utc": state["first_started_at_utc"],
        "completed_at_utc": completed_at_iso,
        "branch": EXPECTED_BRANCH,
        "base_sha": head,
        "metrics": {
            "primary": (
                "per-run total of APEX_SUBMIT_RESULT submit_to_exit_ms "
                "(generate_data + scenarios); clock starts immediately before the "
                "spark-submit process and stops at its return, same point both arms"
            ),
            "secondary_on_only": (
                "APEX_TELEMETRY_RESULT delivery_latency_ms and soak "
                "delivery_waited_seconds; telemetry-delivery latency, never added "
                "to the JAR overhead"
            ),
            "functional_gates_outside_clock": {
                "on": "canonical ClickHouse assertions per scenario",
                "off": "scenario exit codes + APEX_SESSION marker",
            },
        },
        "config": {
            "reps_per_arm": REPS, "warmup_per_arm": WARMUP,
            "soak_cycles_per_arm": SOAK_CYCLES, "sample_seconds": SAMPLE_SECONDS,
            "load": "canonical four-pathology fixture (generate_data + 4 jobs)",
            "toggle": "spark.plugins=apex.ApexPlugin (on) vs explicit empty spark.plugins= (off)",
            "execute_token_present": True,
            "proposed_bands_accepted_by_operator": ACCEPT_BANDS,
            "run_fingerprint": fingerprint,
            "required_markers_per_repetition": list(EXPECTED_JOBS),
        },
        "runtime": identity,
        "e2e_on": stats_on,
        "e2e_off": stats_off,
        "overhead_median_pct": overhead_pct,
        "soak": soak_results,
        "functional_failures": functional_failures,
        "measurement_missing": measurement_missing,
        "decision": decision,
        "units": state["units"],
        "provenance": state.get("provenance", []),
        "external_llm_called": False,
        "secrets_included": False,
        "automatic_fix_applied": False,
        "limitations": [
            "Local controlled benchmark (macOS, Docker Desktop), not production.",
            "GC not measured unless exposed by the JAR without product changes.",
            "Arm off skips telemetry-dependent ClickHouse assertions by design; "
            "telemetry latency exists only on the ON arm and is secondary.",
            f"Medians from {REPS} repetitions do not characterize rare tails.",
            "Raw logs and stats CSVs stay ignored under dev/out/.",
        ],
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(artifact, indent=2))
    log(f"decision={decision} overhead_median_pct={overhead_pct} evidence={EVIDENCE.relative_to(ROOT)}")
    print(f"R9D_RESULT decision={decision} overhead_median_pct={overhead_pct} "
          f"on_median_s={stats_on.get('median_s')} off_median_s={stats_off.get('median_s')} "
          f"functional_failures={len(functional_failures)} measurement_missing={len(measurement_missing)} "
          f"evidence={EVIDENCE.relative_to(ROOT)}")
    return 0 if decision == "approved" else 1


if __name__ == "__main__":
    sys.exit(main())
