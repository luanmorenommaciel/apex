package apex

import scala.collection.mutable

private[apex] final case class StageTaskSampleSummary(
  allAttempts: StageDurationSummary,
  successfulTasks: StageDurationSummary,
  successfulTaskShuffleReadBytesP50: Long,
  successfulTaskShuffleReadBytesMax: Long,
  successfulTaskShuffleReadBytesSampleCount: Int,
  taskDurationSampleCount: Int,
  successfulTaskSampleCount: Int,
  taskAttemptCount: Int,
  taskFailedAttemptCount: Int,
  taskCountedFailureAttemptCount: Int,
  taskKilledAttemptCount: Int,
  taskSpeculativeAttemptCount: Int
)

private[apex] object TaskIdentity {
  def logicalPartitionId(partitionId: Int, taskSetIndex: Int): Int =
    if (partitionId >= 0) partitionId else taskSetIndex
}

/**
 * Stage-local task samples.
 *
 * Legacy duration metrics retain every TaskEnd attempt. The additive successful
 * sample accepts only the first successful attempt observed for each logical
 * partition, so retries and speculative winners cannot overweight a task.
 */
private[apex] final class StageTaskSamples {
  private val allAttemptDurations = mutable.ArrayBuffer.empty[Long]
  private val firstSuccessByPartition = mutable.Map.empty[Int, Long]
  private val firstSuccessShuffleReadBytesByPartition = mutable.Map.empty[Int, Long]
  private var startedAttempts = 0
  private var endedAttempts = 0
  private var failedAttempts = 0
  private var countedFailureAttempts = 0
  private var killedAttempts = 0
  private var speculativeAttempts = 0
  private var missingDurationAttempts = 0

  def recordStart(): Unit =
    startedAttempts += 1

  def record(
      logicalPartitionId: Int,
      durationMs: Option[Long],
      successful: Boolean,
      failed: Boolean,
      killed: Boolean,
      speculative: Boolean,
      countedFailure: Boolean = false,
      shuffleReadBytes: Option[Long] = None): Unit = {
    endedAttempts += 1
    if (startedAttempts < endedAttempts) startedAttempts = endedAttempts
    if (durationMs.isEmpty) missingDurationAttempts += 1
    durationMs.foreach(value => allAttemptDurations += math.max(0L, value))
    if (failed) failedAttempts += 1
    if (countedFailure) countedFailureAttempts += 1
    if (killed) killedAttempts += 1
    if (speculative) speculativeAttempts += 1
    if (successful && !firstSuccessByPartition.contains(logicalPartitionId)) {
      durationMs.foreach { value =>
        firstSuccessByPartition.update(logicalPartitionId, math.max(0L, value))
      }
    }
    if (successful && !firstSuccessShuffleReadBytesByPartition.contains(logicalPartitionId)) {
      shuffleReadBytes.foreach { value =>
        firstSuccessShuffleReadBytesByPartition.update(logicalPartitionId, math.max(0L, value))
      }
    }
  }

  def hasPendingAttempts: Boolean =
    startedAttempts > endedAttempts

  def missingDurationCount: Int = missingDurationAttempts

  def summary: StageTaskSampleSummary = {
    val sortedShuffleReadBytes =
      firstSuccessShuffleReadBytesByPartition.values.toIndexedSeq.sorted
    val shuffleReadP50 =
      if (sortedShuffleReadBytes.isEmpty) 0L
      else sortedShuffleReadBytes((sortedShuffleReadBytes.length - 1) / 2)
    StageTaskSampleSummary(
      allAttempts = StageDurationStats.summarize(allAttemptDurations.toSeq),
      successfulTasks = StageDurationStats.summarize(firstSuccessByPartition.values.toSeq),
      successfulTaskShuffleReadBytesP50 = shuffleReadP50,
      successfulTaskShuffleReadBytesMax = sortedShuffleReadBytes.lastOption.getOrElse(0L),
      successfulTaskShuffleReadBytesSampleCount = sortedShuffleReadBytes.size,
      taskDurationSampleCount = allAttemptDurations.size,
      successfulTaskSampleCount = firstSuccessByPartition.size,
      taskAttemptCount = endedAttempts,
      taskFailedAttemptCount = failedAttempts,
      taskCountedFailureAttemptCount = countedFailureAttempts,
      taskKilledAttemptCount = killedAttempts,
      taskSpeculativeAttemptCount = speculativeAttempts
    )
  }
}

private[apex] object StageTaskSamples {
  val EmptySummary: StageTaskSampleSummary = StageTaskSampleSummary(
    allAttempts = StageDurationSummary(0L, 0L, 0L),
    successfulTasks = StageDurationSummary(0L, 0L, 0L),
    successfulTaskShuffleReadBytesP50 = 0L,
    successfulTaskShuffleReadBytesMax = 0L,
    successfulTaskShuffleReadBytesSampleCount = 0,
    taskDurationSampleCount = 0,
    successfulTaskSampleCount = 0,
    taskAttemptCount = 0,
    taskFailedAttemptCount = 0,
    taskCountedFailureAttemptCount = 0,
    taskKilledAttemptCount = 0,
    taskSpeculativeAttemptCount = 0
  )
}
