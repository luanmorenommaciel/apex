package apex

import java.nio.charset.StandardCharsets
import org.scalatest.funsuite.AnyFunSuite

class ApexPayloadLimitsSpec extends AnyFunSuite {
  test("plan_json below the bound is unchanged") {
    val plan = "Project\n+- Filter"
    assert(ApexPayloadLimits.planJson(plan) == plan)
  }

  test("oversized plan_json is marked and bounded in UTF-8 bytes") {
    val plan = ("😀Project\n" * 20000) + "tail"
    val bounded = ApexPayloadLimits.planJson(plan)

    assert(bounded.endsWith("<apex:truncated>"))
    assert(bounded.getBytes(StandardCharsets.UTF_8).length <= ApexPayloadLimits.MaxPlanJsonUtf8Bytes)
    assert(!Character.isHighSurrogate(bounded.charAt(bounded.indexOf("\n<apex:truncated>") - 1)))
  }
}
