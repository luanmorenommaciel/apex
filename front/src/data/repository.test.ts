import { describe, expect, it } from "vitest";

import { collectionState, comparisonState, dataState } from "../contract/rules";
import { CURRENT_JOB } from "./fixtures";
import { FixtureRepository } from "./repository";

const repository = new FixtureRepository();

describe("FixtureRepository absence semantics", () => {
  it("returns null for an unknown run rather than a synthetic summary", async () => {
    expect(await repository.run("missing-job")).toBeNull();
    expect(dataState(await repository.run("missing-job"))).toEqual({
      state: "unavailable",
      value: null,
    });
  });

  it("keeps a missing comparison candidate not_comparable", async () => {
    const candidates = await repository.baselineCandidates("missing-job");
    expect(candidates).toEqual([]);
    expect(comparisonState(10, 20, candidates.length > 0)).toEqual({
      state: "not_comparable",
      value: null,
    });
  });

  it("keeps absent memory history unavailable", async () => {
    const history = await repository.shapeRuns("missing-fingerprint");
    expect(collectionState(history)).toEqual({ state: "unavailable", value: null });
  });

  it("keeps an absent verification null", async () => {
    const verification = await repository.fixVerification("missing-finding");
    expect(verification).toBeNull();
    expect(dataState(verification)).toEqual({ state: "unavailable", value: null });
  });

  it("preserves unavailable run cost on a recorded run", async () => {
    const run = await repository.run(CURRENT_JOB);
    expect(run).not.toBeNull();
    expect(run?.task_time_ms).toBeNull();
  });
});
