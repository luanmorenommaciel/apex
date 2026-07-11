#!/usr/bin/env python3
"""
Apex — Event Log Ingestor
Bridge between Spark event logs and ClickHouse (V1 schema).

Reads a zstd-compressed Spark event log (already written to /spark-logs)
and populates apex.stage_metrics + apex.task_metrics with the exact same
schema that the SparkListener would have used in real-time.

Usage:
    python ingest/event_log_ingest.py <app_id>
    python ingest/event_log_ingest.py app-20260706010516-0004

Env vars (optional, defaults to plat-v0):
    APEX_CH_HOST, APEX_CH_PORT, APEX_CH_USER, APEX_CH_PASSWORD
    SPARK_LOGS_DIR (default: /spark-logs)
"""
import os
import sys
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import clickhouse_connect

# ── Config ─────────────────────────────────────────────────────────────────────

CH_HOST      = os.getenv("APEX_CH_HOST",     "localhost")
CH_PORT      = int(os.getenv("APEX_CH_PORT", "28123"))
CH_USER      = os.getenv("APEX_CH_USER",     "spv0")
CH_PASSWORD  = os.getenv("APEX_CH_PASSWORD", "spv0clickhouse123")
SPARK_LOGS   = os.getenv("SPARK_LOGS_DIR",   "spark-logs-local")


# ── Event log reader ────────────────────────────────────────────────────────────

def read_events(log_path: str):
    """Read events from a (possibly zstd-compressed) Spark event log."""
    with open(log_path, "rb") as f:
        data = f.read()

    if data[:4] == b"\x28\xb5\x2f\xfd":
        try:
            import zstandard as zstd
            import io
            ctx = zstd.ZstdDecompressor()
            # Use stream_reader: handles frames without embedded content size
            # (Spark event log writer doesn't embed content size in the zstd header)
            with ctx.stream_reader(io.BytesIO(data)) as reader:
                data = reader.read()
        except ImportError:
            print("zstandard not available, trying zstd CLI...")
            import subprocess, tempfile
            with tempfile.NamedTemporaryFile(suffix=".zstd", delete=False) as tf:
                tf.write(data)
                tf_path = tf.name
            result = subprocess.run(["zstd", "-d", "-c", tf_path], capture_output=True)
            if result.returncode != 0:
                raise RuntimeError(f"zstd decompression failed: {result.stderr.decode()}")
            data = result.stdout
            os.unlink(tf_path)

    for line in data.decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            pass


# ── Core ingest ────────────────────────────────────────────────────────────────

def ingest(log_path: str, app_id: str) -> None:
    """Parse event log and insert into ClickHouse."""
    now = datetime.now(timezone.utc)

    stages: dict[int, dict] = {}
    tasks_by_stage: dict[int, list] = defaultdict(list)
    stage_to_job: dict[int, int] = {}

    print(f"[ingest] Reading: {log_path}")
    event_count = 0

    for event in read_events(log_path):
        etype = event.get("Event", "")
        event_count += 1

        # ── Job → Stage mapping ─────────────────────────────────────────────
        if etype == "SparkListenerJobStart":
            job_id = event.get("Job ID", 0)
            for sid in event.get("Stage IDs", []):
                stage_to_job[sid] = job_id

        # ── Stage completion ────────────────────────────────────────────────
        elif etype == "SparkListenerStageCompleted":
            info = event.get("Stage Info", {})
            sid        = info.get("Stage ID", 0)
            submit_ms  = info.get("Submission Time") or 0
            complete_ms= info.get("Completion Time") or 0
            dur_ms     = max(0, complete_ms - submit_ms)

            stages[sid] = {
                "stage_id":        sid,
                "attempt_id":      info.get("Stage Attempt ID", 0),
                "stage_name":      info.get("Stage Name", ""),
                "num_tasks":       info.get("Number of Tasks", 0),
                "duration_ms":     dur_ms,
                "submission_time": (
                    datetime.fromtimestamp(submit_ms / 1000, tz=timezone.utc)
                    if submit_ms else now
                ),
                "completion_time": (
                    datetime.fromtimestamp(complete_ms / 1000, tz=timezone.utc)
                    if complete_ms else now
                ),
            }

        # ── Task completion ─────────────────────────────────────────────────
        elif etype == "SparkListenerTaskEnd":
            sid = event.get("Stage ID", 0)
            ti  = event.get("Task Info", {})
            tm  = event.get("Task Metrics", {})

            launch_ms  = ti.get("Launch Time") or 0
            finish_ms  = ti.get("Finish Time") or 0
            dur_ms     = max(0, finish_ms - launch_ms)
            failed     = ti.get("Failed", False)

            sr  = tm.get("Shuffle Read Metrics",  {})
            sw  = tm.get("Shuffle Write Metrics", {})
            inp = tm.get("Input Metrics",         {})
            out = tm.get("Output Metrics",        {})

            tasks_by_stage[sid].append({
                "task_id":       ti.get("Task ID", 0),
                "attempt_number":ti.get("Attempt", 0),
                "executor_id":   ti.get("Executor ID", ""),
                "launch_time":   (
                    datetime.fromtimestamp(launch_ms / 1000, tz=timezone.utc)
                    if launch_ms else now
                ),
                "finish_time":   (
                    datetime.fromtimestamp(finish_ms / 1000, tz=timezone.utc)
                    if finish_ms else now
                ),
                "duration_ms":   dur_ms,
                "input_bytes":   inp.get("Bytes Read", 0) or 0,
                "output_bytes":  out.get("Bytes Written", 0) or 0,
                "shuffle_read":  (
                    (sr.get("Remote Bytes Read", 0) or 0) +
                    (sr.get("Local Bytes Read",  0) or 0)
                ),
                "shuffle_records": sr.get("Total Records Read", 0) or 0,
                "shuffle_write": sw.get("Shuffle Bytes Written", 0) or 0,
                "memory_spill":  tm.get("Memory Bytes Spilled", 0) or 0,
                "disk_spill":    tm.get("Disk Bytes Spilled",   0) or 0,
                "status":        "FAILED" if failed else "SUCCESS",
            })

    print(f"[ingest] Processed {event_count} events | "
          f"stages={len(stages)} | tasks={sum(len(v) for v in tasks_by_stage.values())}")

    if not stages:
        print("[ERROR] No SparkListenerStageCompleted events found. "
              "Check that the job finished and the correct log path was used.")
        sys.exit(1)

    # ── Connect ─────────────────────────────────────────────────────────────
    ch = clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT,
        username=CH_USER, password=CH_PASSWORD,
    )

    # ── Stage rows (aggregated from tasks) ───────────────────────────────────
    STAGE_COLS = [
        "app_id", "job_id", "stage_id", "attempt_id", "stage_name",
        "submission_time", "completion_time", "duration_ms", "num_tasks",
        "failed_tasks", "input_bytes", "output_bytes",
        "shuffle_read", "shuffle_write", "memory_spill", "disk_spill",
        "gc_time_ms", "executor_cpu_ms",
    ]
    stage_rows = []
    for sid, s in stages.items():
        tasks = tasks_by_stage.get(sid, [])
        stage_rows.append([
            app_id,
            stage_to_job.get(sid, 0),
            s["stage_id"],
            s["attempt_id"],
            s["stage_name"],
            s["submission_time"],
            s["completion_time"],
            s["duration_ms"],
            s["num_tasks"],
            sum(1 for t in tasks if t["status"] == "FAILED"),
            sum(t["input_bytes"]   for t in tasks),
            sum(t["output_bytes"]  for t in tasks),
            sum(t["shuffle_read"]  for t in tasks),
            sum(t["shuffle_write"] for t in tasks),
            sum(t["memory_spill"]  for t in tasks),
            sum(t["disk_spill"]    for t in tasks),
            0,   # gc_time_ms (not aggregated at stage level in event log)
            0,   # executor_cpu_ms
        ])

    # ── Task rows ────────────────────────────────────────────────────────────
    TASK_COLS = [
        "app_id", "stage_id", "task_id", "attempt_number", "executor_id",
        "launch_time", "finish_time", "duration_ms",
        "input_bytes", "output_bytes",
        "shuffle_read", "shuffle_records", "shuffle_write", "memory_spill", "disk_spill", "status",
    ]
    task_rows = []
    for sid, tasks in tasks_by_stage.items():
        for t in tasks:
            task_rows.append([
                app_id, sid,
                t["task_id"], t["attempt_number"], t["executor_id"],
                t["launch_time"], t["finish_time"], t["duration_ms"],
                t["input_bytes"], t["output_bytes"],
                t["shuffle_read"], t["shuffle_records"], t["shuffle_write"],
                t["memory_spill"], t["disk_spill"], t["status"],
            ])

    # ── Insert ────────────────────────────────────────────────────────────────
    print(f"[ingest] Inserting {len(stage_rows)} stage rows, {len(task_rows)} task rows...")
    if stage_rows:
        ch.insert("apex.stage_metrics", stage_rows, column_names=STAGE_COLS)
        print(f"  ✓ apex.stage_metrics: {len(stage_rows)} rows")
    if task_rows:
        ch.insert("apex.task_metrics", task_rows, column_names=TASK_COLS)
        print(f"  ✓ apex.task_metrics: {len(task_rows)} rows")

    # ── Verify ────────────────────────────────────────────────────────────────
    print(f"\n[verify] Top stages for app_id={app_id}:")
    rows = ch.query(
        "SELECT stage_id, stage_name, num_tasks, duration_ms, shuffle_read, shuffle_write "
        "FROM apex.stage_metrics "
        "WHERE app_id = {app_id:String} "
        "ORDER BY duration_ms DESC LIMIT 5",
        parameters={"app_id": app_id},
    ).result_rows
    for r in rows:
        print(f"  stage={r[0]} ({r[1][:40]}) | tasks={r[2]} | {r[3]}ms "
              f"| sr={r[4]:,} sw={r[5]:,}")

    print(f"\n[verify] Task distribution for slowest stage:")
    if rows:
        slowest_sid = rows[0][0]
        dist = ch.query(
            "SELECT count(), max(duration_ms), min(duration_ms), avg(duration_ms) "
            "FROM apex.task_metrics "
            "WHERE app_id = {app_id:String} AND stage_id = {sid:UInt32}",
            parameters={"app_id": app_id, "sid": slowest_sid},
        ).result_rows
        if dist:
            r = dist[0]
            ratio = (r[1] / r[3]) if r[3] else 0
            print(f"  tasks={r[0]} | max={r[1]}ms min={r[2]}ms avg={r[3]:.0f}ms | max/avg={ratio:.1f}x")
            if ratio > 3:
                print(f"  ⚠ SKEW DETECTED: max/avg ratio {ratio:.1f}x > 3x threshold")

    print(f"\n[ingest] Complete. Run crew_diagnose.py --app-id {app_id}")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app_id = sys.argv[1] if len(sys.argv) > 1 else "app-20260706010516-0004"

    log_base = Path(SPARK_LOGS)
    candidates = list(log_base.glob(f"eventlog_v2_{app_id}"))
    if not candidates:
        dirs = [d.name for d in log_base.iterdir() if d.is_dir()]
        print(f"[ERROR] No log dir found for {app_id}")
        print(f"Available: {dirs}")
        sys.exit(1)

    log_dir = candidates[0]
    event_files = sorted(log_dir.glob("events_*.zstd"))
    if not event_files:
        event_files = sorted(log_dir.glob("events_*"))
    if not event_files:
        print(f"[ERROR] No event files in {log_dir}")
        sys.exit(1)

    ingest(str(event_files[0]), app_id)
