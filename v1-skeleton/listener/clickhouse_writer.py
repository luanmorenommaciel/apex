"""
Apex V1 — ClickHouse Writer
Envia métricas capturadas pelo SparkListener para o ClickHouse.
"""
import clickhouse_connect
from datetime import datetime
from typing import Optional


class ClickHouseWriter:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8123,
        user: str = "apex",
        password: str = "apex123",
        database: str = "apex",
    ):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database,
        )

    def write_stage_metrics(self, metrics: dict) -> None:
        """Insere uma linha em apex.stage_metrics."""
        self.client.insert(
            "stage_metrics",
            [[
                metrics.get("app_id", ""),
                metrics.get("job_id", 0),
                metrics.get("stage_id", 0),
                metrics.get("attempt_id", 0),
                metrics.get("stage_name", ""),
                metrics.get("submission_time", datetime.utcnow()),
                metrics.get("completion_time", datetime.utcnow()),
                metrics.get("duration_ms", 0),
                metrics.get("num_tasks", 0),
                metrics.get("failed_tasks", 0),
                metrics.get("input_bytes", 0),
                metrics.get("output_bytes", 0),
                metrics.get("shuffle_read", 0),
                metrics.get("shuffle_write", 0),
                metrics.get("memory_spill", 0),
                metrics.get("disk_spill", 0),
                metrics.get("gc_time_ms", 0),
                metrics.get("executor_cpu_ms", 0),
            ]],
            column_names=[
                "app_id", "job_id", "stage_id", "attempt_id", "stage_name",
                "submission_time", "completion_time", "duration_ms", "num_tasks",
                "failed_tasks", "input_bytes", "output_bytes", "shuffle_read",
                "shuffle_write", "memory_spill", "disk_spill", "gc_time_ms",
                "executor_cpu_ms",
            ],
        )

    def write_task_metrics(self, metrics: dict) -> None:
        """Insere uma linha em apex.task_metrics."""
        self.client.insert(
            "task_metrics",
            [[
                metrics.get("app_id", ""),
                metrics.get("stage_id", 0),
                metrics.get("task_id", 0),
                metrics.get("attempt_number", 0),
                metrics.get("executor_id", ""),
                metrics.get("launch_time", datetime.utcnow()),
                metrics.get("finish_time", datetime.utcnow()),
                metrics.get("duration_ms", 0),
                metrics.get("input_bytes", 0),
                metrics.get("output_bytes", 0),
                metrics.get("shuffle_read", 0),
                metrics.get("shuffle_write", 0),
                metrics.get("memory_spill", 0),
                metrics.get("disk_spill", 0),
                metrics.get("status", "SUCCESS"),
            ]],
            column_names=[
                "app_id", "stage_id", "task_id", "attempt_number", "executor_id",
                "launch_time", "finish_time", "duration_ms", "input_bytes",
                "output_bytes", "shuffle_read", "shuffle_write", "memory_spill",
                "disk_spill", "status",
            ],
        )

    def write_finding(self, finding: dict) -> None:
        """Persiste um finding gerado pelo LLM."""
        self.client.insert(
            "findings",
            [[
                finding.get("app_id", ""),
                finding.get("stage_id"),
                finding.get("pattern", "unknown"),
                finding.get("severity", "medium"),
                finding.get("confidence", 0.0),
                finding.get("root_cause", ""),
                finding.get("recommendation", ""),
                finding.get("llm_model", ""),
            ]],
            column_names=[
                "app_id", "stage_id", "pattern", "severity", "confidence",
                "root_cause", "recommendation", "llm_model",
            ],
        )
