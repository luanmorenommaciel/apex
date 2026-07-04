"""
Apex V1 — SparkListener
Captura métricas durante a execução do job e envia ao ClickHouse.

Uso no job:
    from listener.spark_listener import ApexListener
    apex = ApexListener(app_id=sc.applicationId, ch_host="clickhouse")
    sc._jvm.org.apache.spark.SparkContext.getOrCreate().addSparkListener(apex._java_listener)

Nota arquitetural:
    Esta abordagem usa py4j para registrar um listener Java no SparkContext.
    É in-process com o driver — diferente da abordagem zero-JAR que lê event logs.
    Ver ADR-005 (pendente) para a decisão final de arquitetura.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from listener.clickhouse_writer import ClickHouseWriter

logger = logging.getLogger("apex.listener")


def _ms_to_dt(ms: Optional[int]) -> datetime:
    """Converte epoch milliseconds para datetime UTC."""
    if ms is None or ms <= 0:
        return datetime.utcnow()
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).replace(tzinfo=None)


class ApexSparkListener:
    """
    Listener Spark que coleta métricas via py4j e envia ao ClickHouse.
    Registrado via sc.addSparkListener() após criar a SparkSession.
    """

    def __init__(
        self,
        app_id: str,
        ch_host: str = "localhost",
        ch_port: int = 8123,
        ch_user: str = "apex",
        ch_password: str = "apex123",
    ):
        self.app_id = app_id
        self._writer = ClickHouseWriter(
            host=ch_host, port=ch_port, user=ch_user, password=ch_password
        )
        self._job_stage_map: dict[int, int] = {}  # stage_id → job_id
        logger.info(f"ApexSparkListener iniciado para app_id={app_id}")

    # ── Job ────────────────────────────────────────────────────────────────

    def onJobStart(self, job_start) -> None:
        """Mapeia stage_ids → job_id para enriquecer métricas de stage."""
        try:
            job_id = job_start.jobId()
            for stage_id in job_start.stageIds():
                self._job_stage_map[stage_id] = job_id
        except Exception as e:
            logger.warning(f"onJobStart error: {e}")

    # ── Stage ──────────────────────────────────────────────────────────────

    def onStageCompleted(self, stage_completed) -> None:
        """Captura métricas completas do stage e persiste no ClickHouse."""
        try:
            info = stage_completed.stageInfo()
            tm = info.taskMetrics()

            stage_id = info.stageId()
            job_id = self._job_stage_map.get(stage_id, 0)

            metrics = {
                "app_id":          self.app_id,
                "job_id":          job_id,
                "stage_id":        stage_id,
                "attempt_id":      info.attemptNumber(),
                "stage_name":      info.name(),
                "submission_time": _ms_to_dt(info.submissionTime().getOrElse(None)),
                "completion_time": _ms_to_dt(info.completionTime().getOrElse(None)),
                "duration_ms":     self._calc_duration(info),
                "num_tasks":       info.numTasks(),
                "failed_tasks":    0,  # calculado via task events se necessário
                "input_bytes":     tm.inputMetrics().bytesRead(),
                "output_bytes":    tm.outputMetrics().bytesWritten(),
                "shuffle_read":    tm.shuffleReadMetrics().totalBytesRead(),
                "shuffle_write":   tm.shuffleWriteMetrics().bytesWritten(),
                "memory_spill":    tm.memoryBytesSpilled(),
                "disk_spill":      tm.diskBytesSpilled(),
                "gc_time_ms":      tm.jvmGCTime(),
                "executor_cpu_ms": tm.executorCpuTime() // 1_000_000,  # ns → ms
            }

            self._writer.write_stage_metrics(metrics)
            logger.debug(
                f"Stage {stage_id} | tasks={metrics['num_tasks']} "
                f"| spill={metrics['disk_spill']//1024//1024}MB "
                f"| duration={metrics['duration_ms']}ms"
            )

        except Exception as e:
            logger.error(f"onStageCompleted error: {e}", exc_info=True)

    # ── Task ───────────────────────────────────────────────────────────────

    def onTaskEnd(self, task_end) -> None:
        """Captura métricas por task — necessário para detectar skew."""
        try:
            info = task_end.taskInfo()
            tm = task_end.taskMetrics()

            if tm is None:
                return  # task failed before producing metrics

            stage_id = task_end.stageId()
            duration_ms = info.finishTime() - info.launchTime()

            metrics = {
                "app_id":         self.app_id,
                "stage_id":       stage_id,
                "task_id":        info.taskId(),
                "attempt_number": info.attemptNumber(),
                "executor_id":    info.executorId(),
                "launch_time":    _ms_to_dt(info.launchTime()),
                "finish_time":    _ms_to_dt(info.finishTime()),
                "duration_ms":    duration_ms,
                "input_bytes":    tm.inputMetrics().bytesRead(),
                "output_bytes":   tm.outputMetrics().bytesWritten(),
                "shuffle_read":   tm.shuffleReadMetrics().totalBytesRead(),
                "shuffle_write":  tm.shuffleWriteMetrics().bytesWritten(),
                "memory_spill":   tm.memoryBytesSpilled(),
                "disk_spill":     tm.diskBytesSpilled(),
                "status":         "SUCCESS" if task_end.reason().toString() == "Success" else "FAILED",
            }

            self._writer.write_task_metrics(metrics)

        except Exception as e:
            logger.error(f"onTaskEnd error: {e}", exc_info=True)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _calc_duration(self, stage_info) -> int:
        try:
            sub = stage_info.submissionTime().getOrElse(0)
            comp = stage_info.completionTime().getOrElse(0)
            if sub and comp:
                return int(comp) - int(sub)
        except Exception:
            pass
        return 0

    # ── Java interface ─────────────────────────────────────────────────────

    class Java:
        implements = ["org.apache.spark.scheduler.SparkListenerInterface"]


def attach_to_spark(spark, app_id: str = None, ch_host: str = "clickhouse"):
    """
    Helper para registrar o listener em uma SparkSession existente.

    Uso:
        spark = SparkSession.builder.getOrCreate()
        from listener.spark_listener import attach_to_spark
        attach_to_spark(spark, ch_host="clickhouse")
    """
    sc = spark.sparkContext
    _app_id = app_id or sc.applicationId

    listener = ApexSparkListener(app_id=_app_id, ch_host=ch_host)
    sc._jvm.org.apache.spark.SparkContext.getOrCreate().addSparkListener(listener)

    logger.info(f"ApexSparkListener registrado | app_id={_app_id} | ch_host={ch_host}")
    return listener
