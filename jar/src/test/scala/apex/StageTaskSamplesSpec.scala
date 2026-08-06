package apex

import org.scalatest.funsuite.AnyFunSuite

class StageTaskSamplesSpec extends AnyFunSuite {
  test("successful sample keeps the first success per partition and legacy keeps every attempt") {
    val samples = new StageTaskSamples
    (1 to 4).foreach(_ => samples.recordStart())
    samples.record(0, Some(900L), successful = false, failed = true, killed = false, speculative = false, countedFailure = true)
    samples.record(0, Some(120L), successful = true, failed = false, killed = false, speculative = false)
    samples.record(0, Some(80L), successful = true, failed = false, killed = false, speculative = true)
    samples.record(1, Some(100L), successful = true, failed = false, killed = false, speculative = false)

    val summary = samples.summary
    assert(summary.taskAttemptCount == 4)
    assert(summary.taskDurationSampleCount == 4)
    assert(summary.taskFailedAttemptCount == 1)
    assert(summary.taskCountedFailureAttemptCount == 1)
    assert(summary.taskKilledAttemptCount == 0)
    assert(summary.taskSpeculativeAttemptCount == 1)
    assert(summary.successfulTaskSampleCount == 2)
    assert(summary.allAttempts == StageDurationSummary(100L, 900L, 900L))
    assert(summary.successfulTasks == StageDurationSummary(100L, 120L, 120L))
    assert(!samples.hasPendingAttempts)
  }

  test("legacy failed and scheduler-counted failure remain independent") {
    val samples = new StageTaskSamples
    (1 to 3).foreach(_ => samples.recordStart())
    samples.record(
      0, Some(100L), successful = false, failed = true, killed = false,
      speculative = false, countedFailure = false)
    samples.record(
      1, Some(110L), successful = false, failed = true, killed = false,
      speculative = false, countedFailure = true)
    samples.record(
      2, Some(90L), successful = true, failed = false, killed = false,
      speculative = false, countedFailure = false)

    val summary = samples.summary
    assert(summary.taskFailedAttemptCount == 2)
    assert(summary.taskCountedFailureAttemptCount == 1)
  }

  test("a stage with no successful task exposes zero successful sample without changing legacy") {
    val samples = new StageTaskSamples
    samples.recordStart()
    samples.record(0, Some(300L), successful = false, failed = true, killed = false, speculative = false)

    val summary = samples.summary
    assert(summary.allAttempts == StageDurationSummary(300L, 300L, 300L))
    assert(summary.successfulTasks == StageDurationSummary(0L, 0L, 0L))
    assert(summary.successfulTaskSampleCount == 0)
  }

  test("active stage registry rejects duplicate completion and late callbacks") {
    val registry = new ActiveStageRegistry
    registry.submit(stageId = 7, attempt = 1)
    assert(registry.accepts(stageId = 7, attempt = 1))
    assert(registry.complete(stageId = 7, attempt = 1))
    assert(!registry.accepts(stageId = 7, attempt = 1))
    assert(!registry.complete(stageId = 7, attempt = 1))
  }

  test("failed and killed attempts are separate and late termination closes pending state") {
    val samples = new StageTaskSamples
    (1 to 3).foreach(_ => samples.recordStart())
    samples.record(0, Some(100L), successful = true, failed = false, killed = false, speculative = false)
    samples.record(1, Some(110L), successful = true, failed = false, killed = false, speculative = true)

    assert(samples.hasPendingAttempts)
    samples.record(1, Some(130L), successful = false, failed = false, killed = true, speculative = false)

    val summary = samples.summary
    assert(!samples.hasPendingAttempts)
    assert(summary.taskAttemptCount == 3)
    assert(summary.taskFailedAttemptCount == 0)
    assert(summary.taskKilledAttemptCount == 1)
    assert(summary.taskSpeculativeAttemptCount == 1)
  }

  test("missing duration counts the attempt without contaminating duration percentiles") {
    val samples = new StageTaskSamples
    samples.recordStart()
    samples.record(0, None, successful = false, failed = true, killed = false, speculative = false)

    val summary = samples.summary
    assert(summary.taskAttemptCount == 1)
    assert(summary.taskDurationSampleCount == 0)
    assert(summary.allAttempts == StageDurationSummary(0L, 0L, 0L))
    assert(samples.missingDurationCount == 1)
  }

  test("logical partition identity prefers partitionId and falls back for historical minus one") {
    assert(TaskIdentity.logicalPartitionId(partitionId = 41, taskSetIndex = 7) == 41)
    assert(TaskIdentity.logicalPartitionId(partitionId = -1, taskSetIndex = 7) == 7)
  }

  test("shuffle volume sample keeps one successful value per logical partition") {
    val samples = new StageTaskSamples
    (1 to 4).foreach(_ => samples.recordStart())
    samples.record(
      0, Some(900L), successful = false, failed = true, killed = false,
      speculative = false, shuffleReadBytes = Some(9000L))
    samples.record(
      0, Some(120L), successful = true, failed = false, killed = false,
      speculative = false, shuffleReadBytes = Some(1200L))
    samples.record(
      0, Some(80L), successful = true, failed = false, killed = false,
      speculative = true, shuffleReadBytes = Some(800L))
    samples.record(
      1, Some(100L), successful = true, failed = false, killed = false,
      speculative = false, shuffleReadBytes = Some(100L))

    val summary = samples.summary
    assert(summary.successfulTaskShuffleReadBytesSampleCount == 2)
    assert(summary.successfulTaskShuffleReadBytesP50 == 100L)
    assert(summary.successfulTaskShuffleReadBytesMax == 1200L)
  }
}
