package apex

private[apex] final case class StageDurationSummary(
  p50Ms: Long,
  p99Ms: Long,
  maxMs: Long
)

/** Deterministic duration summary shared by the listener and its unit tests. */
private[apex] object StageDurationStats {
  def summarize(durations: Seq[Long]): StageDurationSummary = {
    val sorted = durations.sorted.toIndexedSeq
    StageDurationSummary(
      p50Ms = percentile(sorted, 0.50),
      p99Ms = percentile(sorted, 0.99),
      maxMs = sorted.lastOption.getOrElse(0L)
    )
  }

  /** Nearest-rank percentile over a pre-sorted ascending sequence; 0 if empty. */
  private def percentile(sorted: IndexedSeq[Long], q: Double): Long =
    if (sorted.isEmpty) 0L
    else {
      val rank = math.ceil(q * sorted.length).toInt
      sorted(math.min(sorted.length - 1, math.max(0, rank - 1)))
    }
}
