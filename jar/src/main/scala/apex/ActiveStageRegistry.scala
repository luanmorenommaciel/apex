package apex

import scala.collection.mutable

/** Small lifecycle gate that prevents late callbacks from recreating stage state. */
private[apex] final class ActiveStageRegistry {
  private val active = mutable.Set.empty[(Int, Int)]

  def submit(stageId: Int, attempt: Int): Unit = active += ((stageId, attempt))

  def accepts(stageId: Int, attempt: Int): Boolean = active.contains((stageId, attempt))

  /** Returns true only for the first completion of an active stage attempt. */
  def complete(stageId: Int, attempt: Int): Boolean = active.remove((stageId, attempt))

  /** Discards a stage that Spark registered for a job but never submitted. */
  def discard(stageId: Int, attempt: Int): Boolean = active.remove((stageId, attempt))

  def clear(): Unit = active.clear()

  private[apex] def size: Int = active.size
}
