import { describe, expect, it } from "vitest";

import { assessStage, collectionState, comparisonState, dataState } from "../contract/rules";
import { SEVERITY_ORDER, type FindingConfidence } from "../contract/types";
import { CURRENT_JOB, findingsByJob, jobConfByJob, stagesByJob } from "./fixtures";
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

describe("the recording conforms to the contract it claims", () => {
  const allStages = Object.values(stagesByJob).flat();
  const allFindings = Object.values(findingsByJob).flat();

  it("carries input_bytes on every stage row", () => {
    // It is CORE in the projection now. If the recording stopped supplying it,
    // bytesPerTask would silently measure on shuffle alone again — the exact
    // divergence from engine's bytes_touched that this field exists to close.
    expect(allStages.length).toBeGreaterThan(0);
    for (const s of allStages) {
      expect(typeof s.input_bytes).toBe("number");
    }
  });

  it("uses only findings.confidence tiers, never the transition vocabulary", () => {
    // BEST_EFFORT belongs to plan_transitions. It reached a finding here once,
    // through an `as FindingRow[]` cast, and rendered as a low-confidence tier
    // that the engine's Enum8 has no member for.
    const tiers: FindingConfidence[] = ["LOW", "MEDIUM", "HIGH"];
    expect(allFindings.length).toBeGreaterThan(0);
    for (const f of allFindings) {
      expect(tiers).toContain(f.confidence);
    }
  });

  it("uses only rungs on the contract ladder", () => {
    for (const f of allFindings) {
      expect(SEVERITY_ORDER).toContain(f.severity);
    }
  });

  it("assesses every recorded stage without throwing or producing a NaN", () => {
    for (const [job, stages] of Object.entries(stagesByJob)) {
      const conf = jobConfByJob[job] ?? [];
      for (const stage of stages) {
        const a = assessStage(stage, conf);
        expect(Number.isFinite(a.ratio)).toBe(true);
        expect(Number.isFinite(a.bytesPerTask)).toBe(true);
        // reportable is the only place a claim is licensed; a refusal must
        // always carry the text explaining it.
        if (!a.reportable) expect(a.refusal?.text).toBeTruthy();
      }
    }
  });
});
