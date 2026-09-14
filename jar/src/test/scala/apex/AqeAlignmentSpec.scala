package apex

import org.scalatest.funsuite.AnyFunSuite

class AqeAlignmentSpec extends AnyFunSuite {
  private val Smj = "SortMergeJoin"
  private val Bhj = "BroadcastHashJoin"
  private val Shj = "ShuffledHashJoin"

  private def shape(
      joins: List[String],
      reads: List[String] = Nil,
      skewAccumIds: Set[Long] = Set.empty): ApexAqeListener.PlanShape =
    ApexAqeListener.PlanShape(joins, reads, skewAccumIds, (joins ++ reads).mkString("/"))

  private def switches(before: List[String], after: List[String]) =
    ApexAqeListener.diff(shape(before), shape(after)).filter(_.kind == PlanTransition.JoinSwitch)

  test("join insertion is an edit, not a cascade of positional replacements") {
    assert(switches(List(Smj, Bhj), List(Bhj, Smj, Bhj)).isEmpty)
  }

  test("join removal is an edit, not a cascade of positional replacements") {
    assert(switches(List(Bhj, Smj, Bhj), List(Smj, Bhj)).isEmpty)
  }

  test("a genuine join strategy substitution remains visible") {
    val found = switches(List(Smj, Bhj), List(Bhj, Bhj))
    assert(found.map(t => t.before -> t.after) == List(Smj -> Bhj))
    assert(found.forall(_.confidence == PlanTransition.High))
  }

  test("identical and empty join lists have no replacements") {
    assert(switches(List(Smj, Bhj), List(Smj, Bhj)).isEmpty)
    assert(switches(Nil, Nil).isEmpty)
    assert(switches(Nil, List(Smj)).isEmpty)
    assert(switches(List(Smj), Nil).isEmpty)
  }

  test("repeated joins align deterministically without false switches") {
    val before = List(Smj, Bhj, Smj, Bhj)
    val after = List(Smj, Smj, Bhj)
    assert(switches(before, after).isEmpty)
    assert(ApexAqeListener.joinReplacements(before, after).isEmpty)
  }

  test("skew accumulator ids and partition-count inputs survive edit alignment") {
    val previous = shape(List(Smj, Bhj), List(""), Set(11L))
    val current = shape(List(Bhj, Smj, Bhj), List("", "skewed"), Set(11L, 22L))

    val transitions = ApexAqeListener.diff(previous, current)
    val skew = transitions.filter(_.kind == PlanTransition.SkewSplit)

    assert(transitions.forall(_.kind != PlanTransition.JoinSwitch))
    assert(skew.size == 1)
    assert(skew.head.skewAccumIds == Set(22L))
    assert(skew.head.readCount == 1)
    assert(skew.head.before == "0 skewed")
    assert(skew.head.after == "1 skewed")
  }

  test("coalesce and local-read transitions retain their existing semantics") {
    val transitions = ApexAqeListener.diff(
      shape(Nil),
      shape(Nil, List("coalesced", "local")))
    assert(transitions.map(_.kind).toSet == Set(PlanTransition.Coalesce, PlanTransition.LocalRead))
  }
}
