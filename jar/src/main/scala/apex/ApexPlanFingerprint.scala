package apex

import org.apache.spark.sql.catalyst.expressions.Literal
import org.apache.spark.sql.catalyst.plans.logical.LogicalPlan

import java.security.MessageDigest

/**
 * Computes the contract `plan_fingerprint` — a SHA-256 of the normalized LOGICAL
 * plan, deliberately NOT the physical plan.
 *
 * Two normalizations stack here:
 *   1. `optimizedPlan.canonicalized` — Catalyst normalizes ExprIds and commutative
 *      ordering, so semantically-identical plans agree. It survives AQE, which
 *      rewrites the PHYSICAL plan at runtime (SMJ→BHJ, skew splits) — the exact
 *      reason we must never fingerprint `executedPlan`/`sparkPlan`.
 *   2. Literal normalization — `canonicalized` does NOT normalize literal VALUES,
 *      so `WHERE id > 100` and `WHERE id > 900` would otherwise hash differently.
 *      The contract requires "same query, different literals → identical
 *      fingerprint" (contract v0.2, 5344f18), so we replace every `Literal` with a
 *      typed placeholder before hashing.
 *
 * The fingerprint is 64 lowercase hex chars → fits ClickHouse `FixedString(64)`.
 * This is the ONLY thing that decides WHAT is hashed; the stage listener decides
 * only WHEN it is attached (buffered per execution_id, flushed at query end).
 */
object ApexPlanFingerprint {

  /** Literal-normalized, ExprId-normalized logical plan. */
  private def normalize(plan: LogicalPlan): LogicalPlan =
    plan.transformAllExpressions { case l: Literal => Literal(null, l.dataType) }.canonicalized

  /** 64 lowercase hex chars. */
  def fingerprint(plan: LogicalPlan): String = sha256(normalize(plan).toString)

  /** Redacted, literal-free plan text for `plan_json` (never the raw plan). */
  def redactedPlan(plan: LogicalPlan): String = redact(normalize(plan).treeString)

  private def sha256(s: String): String =
    MessageDigest.getInstance("SHA-256").digest(s.getBytes("UTF-8")).map("%02x".format(_)).mkString

  private val EmailRe = "(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}".r
  private val PathRe  = "(?i)(file:|hdfs:|s3a?:|gs:|dbfs:)[^ ,)\\]]+".r

  /**
   * Second net (literals are already gone via [[normalize]]): drop emails and
   * file/URI paths that can appear in relation descriptions. `plan_fingerprint`
   * is computed BEFORE redaction and passed as an opaque value — redaction never
   * recomputes it.
   */
  private def redact(s: String): String =
    PathRe.replaceAllIn(EmailRe.replaceAllIn(s, "<email>"), m => s"${m.group(1)}<path>")
}
