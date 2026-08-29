import { describe, expect, it } from "vitest";

import {
  bytesPerTask,
  bytesPerTaskState,
  collectionState,
  comparisonState,
  dataState,
  successfulTaskDurationState,
} from "./rules";
import { CONTRACT_VERSION, type SparkEventContractV05 } from "./types";

const canonicalEvent: SparkEventContractV05 = {
  job_id: "job-1",
  app_id: "app-1",
  app_name: "contract-test",
  stage_id: 7,
  stage_attempt: 0,
  ts: "2026-08-28 00:00:00",
  shuffle_read_bytes: 120,
  shuffle_write_bytes: 60,
  spill_disk_bytes: 0,
  spill_mem_bytes: 0,
  gc_time_ms: 5,
  executor_run_time_ms: 100,
  input_bytes: 120,
  output_bytes: 0,
  peak_execution_mem_bytes: 1,
  task_count: 3,
  task_duration_p50_ms: 10,
  task_duration_p99_ms: 30,
  task_duration_max_ms: 40,
  task_duration_sample_count: 3,
  successful_task_duration_p50_ms: 10,
  successful_task_duration_p99_ms: 20,
  successful_task_duration_max_ms: 25,
  successful_task_sample_count: 3,
  successful_task_shuffle_read_bytes_p50: 40,
  successful_task_shuffle_read_bytes_max: 60,
  successful_task_shuffle_read_bytes_sample_count: 3,
  task_attempt_count: 4,
  task_failed_attempt_count: 1,
  task_counted_failure_attempt_count: 1,
  task_killed_attempt_count: 0,
  task_speculative_attempt_count: 0,
  plan_fingerprint: "f".repeat(64),
  plan_json: "Project [id]",
  attributes: {},
};

describe("frozen contract", () => {
  it("identifies the current contract and requires every additive task field", () => {
    expect(CONTRACT_VERSION).toBe("0.5");
    expect(canonicalEvent.task_duration_sample_count).toBe(3);
    expect(canonicalEvent.successful_task_shuffle_read_bytes_sample_count).toBe(3);
    expect(canonicalEvent.task_attempt_count).toBe(4);
  });

  it("matches Engine bytes-per-task semantics", () => {
    expect(bytesPerTask(canonicalEvent)).toBe(100);
    expect(bytesPerTask({ ...canonicalEvent, input_bytes: 0 })).toBe(60);
    expect(bytesPerTask({ ...canonicalEvent, task_count: 0 })).toBe(0);
  });

  it("does not present the Engine zero-on-no-tasks value as an available metric", () => {
    expect(bytesPerTaskState({ ...canonicalEvent, task_count: 0 })).toEqual({
      state: "unavailable",
      value: null,
    });
  });

  it("uses sample_count rather than zero values to decide availability", () => {
    expect(successfulTaskDurationState(canonicalEvent)).toEqual({
      state: "available",
      value: { p50Ms: 10, p99Ms: 20, maxMs: 25, sampleCount: 3 },
    });
    expect(successfulTaskDurationState({
      successful_task_duration_p50_ms: 0,
      successful_task_duration_p99_ms: 0,
      successful_task_duration_max_ms: 0,
      successful_task_sample_count: 0,
    })).toEqual({ state: "unavailable", value: null });
  });
});

describe("absence and comparability", () => {
  it("keeps a measured zero distinct from unavailable", () => {
    expect(dataState(0)).toEqual({ state: "available", value: 0 });
    expect(dataState(null)).toEqual({ state: "unavailable", value: null });
  });

  it("keeps incompatible distinct from unavailable", () => {
    expect(comparisonState(10, 20, false)).toEqual({
      state: "not_comparable",
      value: null,
    });
    expect(comparisonState(10, null, true)).toEqual({
      state: "unavailable",
      value: null,
    });
  });

  it("does not turn an empty history into an observed zero", () => {
    expect(collectionState([])).toEqual({ state: "unavailable", value: null });
  });
});
