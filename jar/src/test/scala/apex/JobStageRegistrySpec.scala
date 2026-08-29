package apex

import org.scalatest.funsuite.AnyFunSuite

class JobStageRegistrySpec extends AnyFunSuite {
  test("a shared stage is released only after the last live job ends") {
    val registry = new JobStageRegistry
    registry.register(jobId = 1, Seq((7, 0), (8, 0)))
    registry.register(jobId = 2, Seq((7, 0), (9, 0)))

    assert(registry.release(1) == Set((8, 0)))
    assert(registry.referencesStageId(7))
    assert(registry.size == 1)

    assert(registry.release(2) == Set((7, 0), (9, 0)))
    assert(!registry.referencesStageId(7))
    assert(registry.size == 0)
  }

  test("duplicate or unknown JobEnd is idempotent") {
    val registry = new JobStageRegistry
    registry.register(jobId = 4, Seq((11, 2)))

    assert(registry.release(4) == Set((11, 2)))
    assert(registry.release(4).isEmpty)
    assert(registry.release(999).isEmpty)
  }
}
