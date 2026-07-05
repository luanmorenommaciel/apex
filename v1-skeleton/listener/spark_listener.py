"""
Apex V1 — SparkListener (py4j callback)

Captura métricas em tempo real durante a execução do job e envia ao ClickHouse.

Uso:
    spark = SparkSession.builder.getOrCreate()
    from spark_listener import attach_to_spark
    attach_to_spark(spark, ch_host="clickhouse")

Arquitetura (ADR-005 — Mundo B):
    SparkListener in-process via py4j callback.
    Implementa SparkListenerInterface completo (todos os métodos como no-op)
    para evitar AttributeError quando Spark chama eventos não tratados.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from clickhouse_writer import ClickHouseWriter

logger = logging.getLogger("apex.listener")


def _ms_to_dt(ms) -> datetime:
    """Converte epoch milliseconds para datetime UTC."""
    try:
        v = int(ms)
        if v > 0:
            return datetime.fromtimestamp(v / 1000.0, tz=timezone.utc).replace(tzinfo=None)
    except (TypeError, ValueError, OSError):
        pass
    return datetime.utcnow()


def _scala_option(opt) -> Optional[int]:
    """
    Extrai valor de um Scala Option via py4j.
    Usa isDefined()/get() — getOrElse(None) não funciona com tipos primitivos.
    """
    try:
        if opt.isDefined():
            return int(opt.get())
    except Exception:
        pass
    return None


class ApexSparkListener:
    """
    Listener Spark que coleta métricas via py4j e escreve no ClickHouse.

    Implementa TODOS os métodos de SparkListenerInterface como no-op
    para evitar AttributeError quando Spark dispara eventos não monitorados.
    Apenas onJobStart, onStageCompleted e onTaskEnd têm lógica real.
    """

    class Java:
        implements = ["org.apache.spark.scheduler.SparkListenerInterface"]

    def __init__(
        self,
        app_id: str,
        ch_host: str = "clickhouse",
        ch_port: int = 8123,
        ch_user: str = "apex",
        ch_password: str = "apex123",
    ):
        self.app_id = app_id
        self._writer = ClickHouseWriter(
            host=ch_host, port=ch_port, user=ch_user, password=ch_password
        )
        self._job_stage_map: dict = {}  # stage_id -> job_id
        logger.info(f"ApexSparkListener iniciado | app_id={app_id} | ch={ch_host}:{ch_port}")

    # ── Eventos com lógica real ───────────────────────────────────────────────

    def onJobStart(self, jobStart) -> None:
        """Mapeia stage_ids → job_id para enriquecer métricas de stage."""
        try:
            job_id = int(jobStart.jobId())
            stage_ids = jobStart.stageIds()
            for sid in stage_ids:
                self._job_stage_map[int(sid)] = job_id
            logger.debug(f"Job {job_id} iniciado com {stage_ids.size()} stages")
        except Exception as e:
            logger.warning(f"onJobStart error: {e}")

    def onStageCompleted(self, stageCompleted) -> None:
        """Captura métricas completas do stage e persiste no ClickHouse."""
        try:
            info = stageCompleted.stageInfo()
            tm   = info.taskMetrics()

            stage_id = int(info.stageId())
            job_id   = self._job_stage_map.get(stage_id, 0)

            sub_ms  = _scala_option(info.submissionTime()) or 0
            comp_ms = _scala_option(info.completionTime()) or 0
            duration = (comp_ms - sub_ms) if (sub_ms and comp_ms) else 0

            metrics = {
                "app_id":          self.app_id,
                "job_id":          job_id,
                "stage_id":        stage_id,
                "attempt_id":      int(info.attemptNumber()),
                "stage_name":      str(info.name()),
                "submission_time": _ms_to_dt(sub_ms),
                "completion_time": _ms_to_dt(comp_ms),
                "duration_ms":     duration,
                "num_tasks":       int(info.numTasks()),
                "failed_tasks":    0,
                "input_bytes":     int(tm.inputMetrics().bytesRead()),
                "output_bytes":    int(tm.outputMetrics().bytesWritten()),
                "shuffle_read":    int(tm.shuffleReadMetrics().totalBytesRead()),
                "shuffle_write":   int(tm.shuffleWriteMetrics().bytesWritten()),
                "memory_spill":    int(tm.memoryBytesSpilled()),
                "disk_spill":      int(tm.diskBytesSpilled()),
                "gc_time_ms":      int(tm.jvmGCTime()),
                "executor_cpu_ms": int(tm.executorCpuTime()) // 1_000_000,  # ns → ms
            }

            self._writer.write_stage_metrics(metrics)
            logger.info(
                f"Stage {stage_id} gravado | tasks={metrics['num_tasks']} "
                f"| duration={duration}ms "
                f"| shuffle_read={metrics['shuffle_read']//1024//1024}MB "
                f"| disk_spill={metrics['disk_spill']//1024//1024}MB"
            )

        except Exception as e:
            logger.error(f"onStageCompleted error: {e}", exc_info=True)

    def onTaskEnd(self, taskEnd) -> None:
        """Captura métricas por task — detecta skew via distribuição de duration."""
        try:
            info = taskEnd.taskInfo()
            tm   = taskEnd.taskMetrics()

            if tm is None:
                return

            launch_ms  = int(info.launchTime())
            finish_ms  = int(info.finishTime())
            duration   = finish_ms - launch_ms if finish_ms > launch_ms else 0

            # reason().toString() retorna "Success" ou a exceção como string
            reason_str = str(taskEnd.reason().toString()) if taskEnd.reason() else "UNKNOWN"
            status = "SUCCESS" if reason_str == "Success" else "FAILED"

            metrics = {
                "app_id":         self.app_id,
                "stage_id":       int(taskEnd.stageId()),
                "task_id":        int(info.taskId()),
                "attempt_number": int(info.attemptNumber()),
                "executor_id":    str(info.executorId()),
                "launch_time":    _ms_to_dt(launch_ms),
                "finish_time":    _ms_to_dt(finish_ms),
                "duration_ms":    duration,
                "input_bytes":    int(tm.inputMetrics().bytesRead()),
                "output_bytes":   int(tm.outputMetrics().bytesWritten()),
                "shuffle_read":   int(tm.shuffleReadMetrics().totalBytesRead()),
                "shuffle_write":  int(tm.shuffleWriteMetrics().bytesWritten()),
                "memory_spill":   int(tm.memoryBytesSpilled()),
                "disk_spill":     int(tm.diskBytesSpilled()),
                "status":         status,
            }

            self._writer.write_task_metrics(metrics)

        except Exception as e:
            logger.error(f"onTaskEnd error: {e}", exc_info=True)

    # ── No-ops obrigatórios (SparkListenerInterface) ──────────────────────────
    # Sem estes, py4j lança AttributeError quando Spark dispara o evento,
    # o que pode derrubar o job ou logar erros incessantes.

    def onJobEnd(self, jobEnd) -> None: pass
    def onStageSubmitted(self, stageSubmitted) -> None: pass
    def onTaskStart(self, taskStart) -> None: pass
    def onTaskGettingResult(self, taskGettingResult) -> None: pass
    def onEnvironmentUpdate(self, environmentUpdate) -> None: pass
    def onBlockManagerAdded(self, blockManagerAdded) -> None: pass
    def onBlockManagerRemoved(self, blockManagerRemoved) -> None: pass
    def onUnpersistRDD(self, unpersistRDD) -> None: pass
    def onApplicationStart(self, applicationStart) -> None: pass
    def onApplicationEnd(self, applicationEnd) -> None: pass
    def onExecutorMetricsUpdate(self, executorMetricsUpdate) -> None: pass
    def onStageExecutorMetrics(self, executorMetrics) -> None: pass
    def onExecutorAdded(self, executorAdded) -> None: pass
    def onExecutorRemoved(self, executorRemoved) -> None: pass
    def onExecutorExcluded(self, executorExcluded) -> None: pass
    def onExecutorExcludedForStage(self, executorExcludedForStage) -> None: pass
    def onTaskExcluded(self, taskExcluded) -> None: pass
    def onNodeExcluded(self, nodeExcluded) -> None: pass
    def onNodeExcludedForStage(self, nodeExcludedForStage) -> None: pass
    def onExecutorUnexcluded(self, executorUnexcluded) -> None: pass
    def onNodeUnexcluded(self, nodeUnexcluded) -> None: pass
    def onBlockUpdated(self, blockUpdated) -> None: pass
    def onSpeculativeTaskSubmitted(self, speculativeTask) -> None: pass
    def onOtherEvent(self, event) -> None: pass
    def onResourceProfileAdded(self, event) -> None: pass


def attach_to_spark(spark, app_id: str = None, ch_host: str = "clickhouse") -> ApexSparkListener:
    """
    Registra o ApexSparkListener no SparkContext.

    Deve ser chamado ANTES de qualquer ação Spark para capturar todos os eventos.

    Args:
        spark:   SparkSession ativa
        app_id:  ID da aplicação (default: spark.sparkContext.applicationId)
        ch_host: Host do ClickHouse (default: "clickhouse" para docker-compose)

    Returns:
        listener: instância do ApexSparkListener registrada
    """
    sc = spark.sparkContext
    _app_id = app_id or sc.applicationId

    listener = ApexSparkListener(app_id=_app_id, ch_host=ch_host)

    # Registra via py4j no Scala SparkContext
    sc._jvm.org.apache.spark.SparkContext.getOrCreate().addSparkListener(listener)

    logger.info(f"ApexSparkListener registrado | app_id={_app_id} | ch_host={ch_host}")
    return listener
