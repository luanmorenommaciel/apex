package apexdev;

import org.apache.spark.sql.catalyst.expressions.Expression;
import org.apache.spark.sql.catalyst.expressions.Literal;
import org.apache.spark.sql.catalyst.plans.logical.LogicalPlan;
import scala.runtime.AbstractPartialFunction;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * Dev-lane twin of the jar's {@code apex.ApexPlanFingerprint}.
 *
 * The dev Python listener MUST produce the SAME plan_fingerprint as the Scala jar
 * for the same query (contract: that is what lets compare_runs work across the
 * pipeline). A pure-Python re-implementation of Catalyst's tree-string would never
 * stay byte-identical across Spark versions, so instead we run the IDENTICAL JVM
 * Catalyst operations the jar runs:
 *
 *   plan.transformAllExpressions { case l: Literal => Literal(null, l.dataType) }
 *       .canonicalized.toString  ->  SHA-256  ->  64 lowercase hex
 *
 * Two normalizations stack: (1) canonicalized normalizes ExprIds / commutative
 * ordering and survives AQE (which only rewrites the PHYSICAL plan); (2) literal
 * nulling makes "id > 100" and "id > 900" hash identically. Purely logical, never
 * physical. 64 hex chars -> fits ClickHouse FixedString(64).
 */
public final class PlanFingerprint {

    /** case l: Literal => Literal(null, l.dataType) — same as the jar's rule. */
    private static final class LiteralNuller extends AbstractPartialFunction<Expression, Expression> {
        @Override public boolean isDefinedAt(Expression e) { return e instanceof Literal; }
        @Override public Expression apply(Expression e) {
            return new Literal(null, ((Literal) e).dataType());
        }
    }

    private static LogicalPlan nullLiterals(LogicalPlan plan) {
        return (LogicalPlan) plan.transformAllExpressions(new LiteralNuller());
    }

    /**
     * Mirrors the jar's canonicalization fallback (Spark 4.1): when
     * {@code canonicalized} throws (UnresolvedException on object-typed plans
     * such as Delta's state reconstruction), hash the literal-normalized text
     * with ExprIds and JVM lambda identities scrubbed instead of failing.
     */
    private static String normalizedText(LogicalPlan plan, boolean tree) {
        LogicalPlan nulled = nullLiterals(plan);
        try {
            LogicalPlan canon = (LogicalPlan) nulled.canonicalized();
            return scrubIdentities(tree ? canon.treeString() : canon.toString());
        } catch (RuntimeException e) {
            return scrub(tree ? nulled.treeString() : nulled.toString());
        }
    }

    /** Both paths: JVM lambda/object identities differ per execution and per JVM. */
    static String scrubIdentities(String s) {
        // JDK 17: Foo$$Lambda$5638/0x…@hash — JDK 21: Foo$$Lambda/0x…@hash (no counter).
        String noLambda = s.replaceAll("\\$\\$Lambda(\\$\\d+)?/0x[0-9a-fA-F]+(@[0-9a-fA-F]+)?", "\\$\\$Lambda");
        return noLambda.replaceAll("@[0-9a-fA-F]{6,}", "@");
    }

    /** 64 lowercase hex chars. */
    public static String fingerprint(LogicalPlan plan) {
        return sha256(normalizedText(plan, false));
    }

    /** Redacted, literal-free plan text for plan_json (never the raw plan). */
    public static String redactedPlan(LogicalPlan plan) {
        return redact(normalizedText(plan, true));
    }

    /** Fallback-only: additionally drop the ExprIds canonicalized would have normalized. */
    static String scrub(String s) {
        return scrubIdentities(s.replaceAll("#\\d+L?", "#"));
    }

    private static String redact(String s) {
        String noEmail = s.replaceAll("(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}", "<email>");
        return noEmail.replaceAll("(?i)(file:|hdfs:|s3a?:|gs:|dbfs:)[^ ,)\\]]+", "$1<path>");
    }

    private static String sha256(String s) {
        try {
            byte[] d = MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(64);
            for (byte b : d) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("apexdev fingerprint sha256 failed", e);
        }
    }

    private PlanFingerprint() {}
}
