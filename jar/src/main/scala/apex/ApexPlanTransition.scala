package apex

/**
 * One AQE runtime re-plan, as it crosses the jar → collector boundary
 * (contract v0.2 § "AQE plan transitions"). ADDITIVE: a distinct `apex.plan_transition`
 * span, never touching the `apex.stage` shape.
 *
 * This is Spark's OWN optimization decision captured as ground truth — the signal
 * that turns a heuristic skew finding into a $0 ground-truth one.
 *
 * Keyed by `(job_id, execution_id, update_seq)`. `detail`/`before`/`after` are
 * structured descriptors built from node names + AQE descriptors only — never the
 * raw `physicalPlanDescription` (which carries literals).
 */
final case class PlanTransition(
  job_id: String,
  execution_id: Long,
  update_seq: Int,
  transition_type: String, // join_switch | skew_split | coalesce | local_read | other
  detail: String,
  before: String,
  after: String,
  confidence: String,      // HIGH | BEST_EFFORT
  ts: Long
)

object PlanTransition {
  // transition_type values (contract v0.2)
  val JoinSwitch = "join_switch"
  val SkewSplit  = "skew_split"
  val Coalesce   = "coalesce"
  val LocalRead  = "local_read"
  val Other      = "other"

  // confidence values (contract v0.2)
  val High       = "HIGH"
  val BestEffort = "BEST_EFFORT"
}
