import { describe, expect, it } from "vitest";
import * as fx from "@/data/fixtures";
import type { JobConfRow, SparkEventRow } from "./types";
import {
  assessStage, ratioOf, readSlots, refusedInSample, TAIL_SAMPLE, VOLUME_FLOOR_BYTES_PER_TASK,
} from "./rules";

/**
 * The run rollup's `refused` CTE (serve/src/apex_mcp/ch.py, behind the API) computes
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

  /**
   * The SAME six stages serve's parity gate seeds (REFUSED_STAGES in
   * serve/tools/console_parity_gate.py), held here to assessStage(). The gate
   * holds the CTE's answer, through both doors, to the same expected count;
   * a change to a rule that one side does not follow fails on one of the two.
   * p50 is 100 ms, so p99 is the ratio x100; 8 x 4 = 32 slots, bar 6.42.
   */
  it("counts 3 refusals on the six-stage fixture serve's gate seeds", () => {
    const template = fx.stagesByJob[fx.CURRENT_JOB][0];
    const stage = (stage_id: number, task_count: number, shuffle_read_bytes: number, p99: number): SparkEventRow => ({
      ...template, job_id: "gate", stage_id, stage_attempt: 0, task_count, shuffle_read_bytes,
      shuffle_write_bytes: 0, input_bytes: 0, task_duration_p50_ms: 100, task_duration_p99_ms: p99,
    });
    const stages = [
      stage(1, 200, 4_000_000_000, 1500), // 15x, 20 MiB/task, over the bar -> reportable
      stage(2, 200, 4_000_000_000, 120),  // 1.2x, not among the five loudest
      stage(3, 2, 4_000_000, 900),        // 9x, two tasks -> rule 6, refused
      stage(4, 200, 1_000, 800),          // 8x, 5 B/task -> under the floor, refused
      stage(5, 200, 4_000_000_000, 700),  // 7x, over the 6.42 bar -> reportable
      stage(6, 200, 4_000_000_000, 600),  // 6x, under the bar -> rule 1 work-bound, refused
    ];
    const conf: JobConfRow[] = [
      { job_id: "gate", key: "spark.executor.instances", value: "8", ts: template.ts },
      { job_id: "gate", key: "spark.executor.cores", value: "4", ts: template.ts },
      { job_id: "gate", key: "spark.sql.shuffle.partitions", value: "200", ts: template.ts },
    ];
    expect(refusedInSample(stages, conf)).toBe(3);
    expect(cteRefusedCount(stages, conf)).toBe(3);
    // Stage 2 is work-bound on its own (1.2x under the bar) but is not among
    // the five loudest, so it never enters the count either way.
    expect(stages.map((s) => assessStage(s, conf).refusal?.code ?? "reportable")).toEqual([
      "reportable", "work_bound", "not_a_distribution", "below_volume_floor", "reportable", "work_bound",
    ]);
  });

  it("treats an unknown cluster width as a refusal, never an assumed width", () => {
    const stages = fx.stagesByJob[fx.CURRENT_JOB];
    expect(cteRefusedCount(stages, [])).toBe(refusedInSample(stages, []));
    expect(cteRefusedCount(stages, [])).toBe(TAIL_SAMPLE);
  });
});
