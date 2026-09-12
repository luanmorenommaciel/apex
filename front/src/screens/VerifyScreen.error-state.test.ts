import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./VerifyScreen.tsx", import.meta.url), "utf8");

describe("VerifyScreen query-error state", () => {
  it("handles a rejected verification query before genuine absence", () => {
    const errorBranch = source.indexOf("if (fixQ.error && finding)");
    const absentFindingBranch = source.indexOf("if (!finding)");
    const absentVerificationBranch = source.indexOf("if (!v)");

    expect(errorBranch).toBeGreaterThan(-1);
    expect(errorBranch).toBeLessThan(absentFindingBranch);
    expect(errorBranch).toBeLessThan(absentVerificationBranch);
    expect(source).toContain('title="Verification data unavailable"');
    expect(source).toContain("No missing-row conclusion can be drawn");
    expect(source).not.toContain("{fixQ.error.name");
    expect(source).not.toContain("{fixQ.error.message}");
    expect(source).not.toContain("{fixQ.error.stack}");
  });

  it("preserves the real zero-row state", () => {
    expect(source).toContain('title="No verification for this finding"');
    expect(source).toContain("apex.fix_verifications");
    expect(source).toContain("does not establish why the row is absent");
    expect(source).not.toContain("This is a gap in the pipeline, not a failure of the query");
  });
});
