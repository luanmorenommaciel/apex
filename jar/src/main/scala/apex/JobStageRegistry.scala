package apex

import scala.collection.mutable

/**
 * Tracks the stage attempts mentioned by each live Spark job.
 *
 * A completed shuffle stage may be listed again in a later JobStart even though
 * Spark will not submit or complete it again. JobEnd is therefore the only
 * bounded point at which that skipped registration can be released. Reference
 * tracking prevents one concurrent job from releasing a stage still used by
 * another.
 */
private[apex] final class JobStageRegistry {
  private val stagesByJob = mutable.Map.empty[Int, Set[(Int, Int)]]

  def register(jobId: Int, stages: Iterable[(Int, Int)]): Unit =
    stagesByJob.update(jobId, stages.toSet)

  /** Returns only stage attempts no longer referenced by another live job. */
  def release(jobId: Int): Set[(Int, Int)] = {
    val released = stagesByJob.remove(jobId).getOrElse(Set.empty)
    released.diff(stagesByJob.valuesIterator.flatten.toSet)
  }

  def referencesStageId(stageId: Int): Boolean =
    stagesByJob.valuesIterator.exists(_.exists(_._1 == stageId))

  def clear(): Unit = stagesByJob.clear()

  def size: Int = stagesByJob.size
}
