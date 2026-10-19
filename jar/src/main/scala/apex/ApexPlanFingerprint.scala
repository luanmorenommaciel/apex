package apex

import org.apache.spark.sql.catalyst.expressions.Literal
import org.apache.spark.sql.catalyst.plans.logical.LogicalPlan

import java.security.MessageDigest
import scala.util.control.NonFatal

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
 * Canonicalization fallback (Spark 4.1): `QueryPlan.canonicalized` on 4.1 walks
 * `allAttributes` (the children's output) and calls `qualifier` on each one;
 * object-typed plans such as Delta's "Cache Delta Table State" state reconstruction
 * (SerializeFromObject / MapPartitions / DeserializeToObject) still expose an
 * `UnresolvedAttribute` in a child's output there and throw `UnresolvedException`.
 * Reproduced 2026-10-19 on apex_41 with the dev lane: every job lost the fingerprint
 * of one to three Delta executions. When canonicalization throws, the plan is hashed
 * from its literal-normalized text with ExprIds scrubbed, so the fingerprint stays a
 * stable 64-hex value for the same logical shape instead of an empty string.
 *
 * JVM identities (`Foo$$Lambda$5638/0x…@1e546002`, `@6f3a1c…`) printed by object
 * operators (MapElements, MapPartitions) are scrubbed on BOTH paths: `canonicalized`
 * leaves them in place, so the same typed pipeline hashed differently per execution.
 * Plans without such tokens keep their historical fingerprints.
 *
 * The fingerprint is 64 lowercase hex chars → fits ClickHouse `FixedString(64)`.
 * This is the ONLY thing that decides WHAT is hashed; the stage listener decides
 * only WHEN it is attached (buffered per execution_id, flushed at query end).
 */
object ApexPlanFingerprint {

  /** Literal-normalized plan (ExprIds still raw). */
  private def nullLiterals(plan: LogicalPlan): LogicalPlan =
    plan.transformAllExpressions { case l: Literal => Literal(null, l.dataType) }

  /** Literal-normalized, ExprId-normalized logical plan text; see the fallback note. */
  private def normalizedText(plan: LogicalPlan, render: LogicalPlan => String): String = {
    val nulled = nullLiterals(plan)
    try scrubIdentities(render(nulled.canonicalized))
    catch { case NonFatal(_) => scrub(render(nulled)) }
  }

  /** 64 lowercase hex chars. */
  def fingerprint(plan: LogicalPlan): String = sha256(normalizedText(plan, _.toString))

  /** Redacted, literal-free plan text for `plan_json` (never the raw plan). */
  def redactedPlan(plan: LogicalPlan): String = redact(normalizedText(plan, _.treeString))

  /** True when `canonicalized` throws for this plan (diagnostics and tests only). */
  private[apex] def canonicalizationFails(plan: LogicalPlan): Boolean =
    try { nullLiterals(plan).canonicalized; false } catch { case NonFatal(_) => true }

  private def sha256(s: String): String =
    MessageDigest.getInstance("SHA-256").digest(s.getBytes("UTF-8")).map("%02x".format(_)).mkString

  private val ExprIdRe = "#\\d+L?".r
  // JDK 17 prints `Foo$$Lambda$5638/0x00000078025a59a8@1e546002`; JDK 21 drops the
  // counter: `Foo$$Lambda/0x00007f3a1c0b2c40@6f3a1c`. Both carry a per-JVM hidden-class
  // address, so the whole suffix goes; the identity hash is optional here because
  // IdentityRe below also covers it.
  private val LambdaRe = "\\$\\$Lambda(\\$\\d+)?/0x[0-9a-fA-F]+(@[0-9a-fA-F]+)?".r
  private val IdentityRe = "@[0-9a-fA-F]{6,}".r

  /** Both paths: JVM lambda/object identities differ per execution and per JVM. */
  private[apex] def scrubIdentities(s: String): String =
    IdentityRe.replaceAllIn(LambdaRe.replaceAllIn(s, "\\$\\$Lambda"), "@")

  /** Fallback-only: additionally drop the ExprIds `canonicalized` would have normalized. */
  private[apex] def scrub(s: String): String =
    scrubIdentities(ExprIdRe.replaceAllIn(s, "#"))

  private val EmailRe = "(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}".r
  private val PathRe  = "(?i)(file:|hdfs:|s3a?:|gs:|dbfs:)[^ ,)\\]]+".r

  /**
   * Second net (literals are already gone via [[nullLiterals]]): drop emails and
   * file/URI paths that can appear in relation descriptions. `plan_fingerprint`
   * is computed BEFORE redaction and passed as an opaque value — redaction never
   * recomputes it.
   */
  private def redact(s: String): String =
    PathRe.replaceAllIn(EmailRe.replaceAllIn(s, "<email>"), m => s"${m.group(1)}<path>")
}
