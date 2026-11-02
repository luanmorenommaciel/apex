import org.apache.spark.sql.catalyst.expressions._
import org.apache.spark.sql.catalyst.plans.logical._
import org.apache.spark.sql.types._
import java.security.MessageDigest

object FingerprintProbe {
  class Positive extends (Long => Boolean) with Serializable {
    def apply(x: Long): Boolean = x > 0L
  }
  def sha(s: String): String = MessageDigest.getInstance("SHA-256").digest(s.getBytes("UTF-8")).map("%02x".format(_)).mkString
  def main(args: Array[String]): Unit = {
    val a=AttributeReference("left_value", LongType, nullable=false)()
    val b=AttributeReference("right_value", LongType, nullable=false)()
    val rel=LocalRelation(a,b)
    def plan(f: Positive,g: Positive): LogicalPlan = {
      val operands=Seq[Expression](ScalaUDF(f,BooleanType,Seq(a)),ScalaUDF(g,BooleanType,Seq(b)),IsNotNull(a),IsNotNull(b),GreaterThan(a,Literal(0L)))
      Filter(operands.reduceLeft(And),rel)
    }
    val stableF=new Positive;val stableG=new Positive
    val stable=(1 to 32).map(_=>apex.ApexPlanFingerprint.fingerprint(plan(stableF,stableG)))
    val attempts=(1 to 128).map { _ =>
      val f=new Positive;val g=new Positive;val p=plan(f,g)
      val normalized=p.transformAllExpressions{case l: Literal=>Literal(null,l.dataType)}.canonicalized.toString
      (apex.ApexPlanFingerprint.fingerprint(p),sha(normalized),f.hashCode,g.hashCode)
    }
    require(stable.distinct.size==1,"fixed-object control was unstable")
    require(attempts.forall(x=>x._1==x._2),"APEX hashing did not match normalized text")
    require(List(-1L,0L,1L,100L).forall(x=>new Positive().apply(x)==new Positive().apply(x)),"pure function controls disagreed")
    val counts=attempts.groupBy(_._1).toSeq.sortBy(_._1).map{case(k,v)=>s"\"$k\":${v.size}"}.mkString(",")
    println(s"RESULT_JSON:{\"spark_version\":\"4.0.1\",\"scope\":\"Catalyst logical plans only; no SparkSession or job\",\"attempts\":128,\"fixed_object_hashes\":${stable.distinct.size},\"new_function_object_hashes\":${attempts.map(_._1).distinct.size},\"sha_recomputation_matches\":true,\"fingerprint_counts\":{$counts}}")
    require(attempts.map(_._1).distinct.size>1,"no variation observed; hypothesis not reproduced in sampled trials")
  }
}
