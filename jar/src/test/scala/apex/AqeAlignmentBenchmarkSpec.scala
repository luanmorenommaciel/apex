package apex

import org.scalatest.funsuite.AnyFunSuite

class AqeAlignmentBenchmarkSpec extends AnyFunSuite {
  test("edit alignment benchmark: 100 joins on the JVM") {
    val names = Vector(
      "SortMergeJoin", "BroadcastHashJoin",
      "ShuffledHashJoin", "BroadcastNestedLoopJoin")
    val before = List.tabulate(100)(i => names(i % names.size))
    val after = before.patch(50, List("BroadcastHashJoin"), 0)

    // Warm the JIT before measuring. The benchmark is reproducible evidence,
    // not a production latency claim and intentionally has no fragile time gate.
    (1 to 100).foreach(_ => ApexAqeListener.joinReplacements(before, after))
    val iterations = 1000
    val started = System.nanoTime()
    var replacements = List.empty[(String, String)]
    (1 to iterations).foreach { _ =>
      replacements = ApexAqeListener.joinReplacements(before, after)
    }
    val elapsedMs = (System.nanoTime() - started) / 1000000.0
    val perRunMs = elapsedMs / iterations

    info(f"100-join edit alignment: $perRunMs%.4f ms/run ($iterations iterations)")
    assert(replacements.isEmpty)
    assert(perRunMs >= 0.0)
  }
}
