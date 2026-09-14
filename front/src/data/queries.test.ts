import { describe, expect, it } from "vitest";
import { PLAN_TRANSITIONS } from "./queries";

describe("PLAN_TRANSITIONS", () => {
  it("does not shadow the source fingerprint inside the ClickHouse CTE", () => {
    expect(PLAN_TRANSITIONS).toContain(
      "any(toString(plan_fingerprint)) AS fingerprint",
    );
    expect(PLAN_TRANSITIONS).toContain(
      "ifNull(any(fp.fingerprint), '')      AS plan_fingerprint",
    );
    expect(PLAN_TRANSITIONS).not.toMatch(
      /any\(toString\(plan_fingerprint\)\)\s+AS plan_fingerprint/,
    );
  });
});
