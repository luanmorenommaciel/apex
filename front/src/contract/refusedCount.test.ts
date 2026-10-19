import { describe, expect, it } from "vitest";
import * as fx from "@/data/fixtures";
import type { JobConfRow, SparkEventRow } from "./types";
import {
  assessStage, ratioOf, readSlots, refusedInSample, TAIL_SAMPLE, VOLUME_FLOOR_BYTES_PER_TASK,
} from "./rules";

/**
 * The run rollup's `refused` CTE (queries.ts, mirrored in serve) computes
 * refused_count in SQL. This evaluates that CTE's arithmetic - the same
 * booleans, in the same order, over the same inputs - in TypeScript, and
 * holds it to assessStage(), the rules' home, over every recorded run. A
 * change to a rule in rules.ts that the SQL does not follow fails here; the
 * live parity gate is what proves the SQL text itself.
 */
function cteRefusedCount(stages: SparkEventRow[], conf: JobConfRow[]): number {
  // readSlots(): instances x cores, both present and numeric and > 0, else NULL.
  const slots = readSlots(conf);
  const perStage = stages.map((s) => {
    const ratio = s.task_duration_p50_ms <= 0 ? 0 : s.task_duration_p99_ms / s.task_duration_p50_ms;
    const bytesPerTask = s.task_count <= 0
      ? 0
      : (s.shuffle_read_bytes + s.shuffle_write_bytes + s.input_bytes) / s.task_count;
    const notADistribution =
      s.task_count <= 1 || (slots !== null && s.task_count <= slots) || s.task_count <= 2;
    const aboveFloor = bytesPerTask >= 1048576;
    const tailBound = slots !== null && slots > 1 && ratio > (s.task_count - 1) / (slots - 1);
    return { stage_id: s.stage_id, ratio, reportable: !notADistribution && aboveFloor && tailBound };
  });
  return perStage
    .sort((a, b) => b.ratio - a.ratio || a.stage_id - b.stage_id)
    .slice(0, 5)
    .filter((s) => !s.reportable).length;
}

describe("refused_count arithmetic", () => {
  const jobs = Object.keys(fx.stagesByJob);

  it("covers every recorded run", () => {
    expect(jobs.length).toBeGreaterThan(0);
    expect(VOLUME_FLOOR_BYTES_PER_TASK).toBe(1048576);
    expect(TAIL_SAMPLE).toBe(5);
  });

  it.each(jobs)("%s: the CTE's booleans count what assessStage() refuses", (jobId) => {
    const stages = fx.stagesByJob[jobId];
    const conf = fx.jobConfByJob[jobId] ?? [];
    expect(cteRefusedCount(stages, conf)).toBe(refusedInSample(stages, conf));
  });

  it("agrees stage by stage, not only in total", () => {
    for (const jobId of jobs) {
      const conf = fx.jobConfByJob[jobId] ?? [];
      for (const s of fx.stagesByJob[jobId]) {
        const a = assessStage(s, conf);
        const sql = cteRefusedCount([s], conf) === 1;
        expect(sql, `${jobId} stage ${s.stage_id} ratio ${ratioOf(s).toFixed(2)}`).toBe(a.refusal !== null);
      }
    }
  });

  it("treats an unknown cluster width as a refusal, never an assumed width", () => {
    const stages = fx.stagesByJob[fx.CURRENT_JOB];
    expect(cteRefusedCount(stages, [])).toBe(refusedInSample(stages, []));
    expect(cteRefusedCount(stages, [])).toBe(TAIL_SAMPLE);
  });
});
