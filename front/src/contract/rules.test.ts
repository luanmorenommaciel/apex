import { describe, expect, it } from "vitest";
import { fixVerifications } from "@/data/fixtures";

import {
  assessStage,
  bytesPerTask,
  bytesPerTaskState,
  collectionState,
  comparisonState,
  dataState,
  fmt,
  parseProposal,
  successfulTaskDurationState,
  VOLUME_FLOOR_BYTES_PER_TASK,
} from "./rules";
import {
  CONTRACT_VERSION, SEVERITY_ORDER, severityRank,
  type JobConfRow, type Severity, type SparkEventContractV05,
} from "./types";

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

describe("the volume floor is engine's, not a shuffle-only approximation", () => {
  /**
   * The regression this locks down.
   *
   * LATEST_STAGES did not select input_bytes, so a scan stage reached the UI
   * with the field absent and `?? 0` inside bytesPerTask swallowed it. A stage
   * moving 400 MiB of INPUT over 200 tasks — comfortably over the 1 MiB floor
   * for the engine — measured 0 B/task here and was refused as unmeasurable.
   * The two lanes disagreed about which stages a ratio may describe, with
   * nothing on screen to say so.
   */
  const scanStage = {
    ...canonicalEvent,
    stage_id: 1,
    task_count: 200,
    shuffle_read_bytes: 0,
    shuffle_write_bytes: 0,
    input_bytes: 400 * 1024 * 1024,
    task_duration_p50_ms: 100,
    task_duration_p99_ms: 900,
    stage_name: null,
  };
  const conf: JobConfRow[] = [
    { job_id: "job-1", key: "spark.executor.instances", value: "4", ts: "" },
    { job_id: "job-1", key: "spark.executor.cores", value: "4", ts: "" },
  ];

  it("counts input_bytes toward bytes/task", () => {
    expect(bytesPerTask(scanStage)).toBe((400 * 1024 * 1024) / 200);
    expect(bytesPerTask(scanStage)).toBeGreaterThan(VOLUME_FLOOR_BYTES_PER_TASK);
  });

  it("clears the floor on input alone, as the engine does", () => {
    const assessed = assessStage(scanStage, conf);
    expect(assessed.aboveVolumeFloor).toBe(true);
    expect(assessed.refusal?.code).not.toBe("below_volume_floor");
  });

  it("would have refused the same stage on shuffle alone", () => {
    // The pre-fix behaviour, written out so the regression is legible.
    const shuffleOnly = { ...scanStage, input_bytes: 0 };
    expect(assessStage(shuffleOnly, conf).refusal?.code).toBe("below_volume_floor");
  });
});

describe("the severity ladder", () => {
  it("puts blocker at the top, not alongside info", () => {
    expect(SEVERITY_ORDER).toEqual(["info", "warning", "critical", "blocker"]);
    expect(severityRank("blocker")).toBeGreaterThan(severityRank("critical"));
    expect(severityRank("critical")).toBeGreaterThan(severityRank("warning"));
    expect(severityRank("warning")).toBeGreaterThan(severityRank("info"));
  });

  it("does not rank an unknown rung as the quietest", () => {
    // A rung outside the Enum8 means this projection is behind the store.
    // Sorting it to the bottom would hide it under every info finding.
    expect(severityRank("catastrophe" as Severity)).toBeGreaterThan(severityRank("blocker"));
  });
});

describe("parseProposal", () => {
  it("reads the live shape: proposed_config as canonical JSON", () => {
    expect(parseProposal('{"spark.sql.shuffle.partitions":"200"}')).toEqual({
      kind: "overlay",
      config: { "spark.sql.shuffle.partitions": "200" },
    });
  });

  it("reads scalars of any JSON type, because conf values are strings on the wire", () => {
    expect(parseProposal('{"a":200,"b":true,"c":"x"}')).toEqual({
      kind: "overlay",
      config: { a: "200", b: "true", c: "x" },
    });
  });

  it("preserves __proto__ as an own key so the caller can reject its namespace", () => {
    const proposal = parseProposal('{"spark.sql.shuffle.partitions":800,"__proto__":"outside namespace"}');
    expect(proposal.kind).toBe("overlay");
    if (proposal.kind !== "overlay") throw new Error("expected overlay");
    expect(Object.getPrototypeOf(proposal.config)).toBe(Object.prototype);
    expect(Object.hasOwn(proposal.config, "__proto__")).toBe(true);
    expect(proposal.config["__proto__"]).toBe("outside namespace");
    expect(Object.keys(proposal.config)).toEqual(["spark.sql.shuffle.partitions", "__proto__"]);
  });

  it.each([
    ['{"a":{"nested":1}}', "nested object"],
    ['{"a":[1]}', "array"],
    ['{"a":null}', "null"],
    ['{"a":"keep","b":{"nested":1}}', "mixed valid and invalid values"],
    ["[]", "top-level array"],
  ])("rejects a %s without accepting a partial overlay", (text) => {
    expect(parseProposal(text)).toEqual({ kind: "invalid-overlay" });
  });

  it("recognises the recorded shape: a unified diff", () => {
    const diff = [
      "--- a/conf/spark-defaults.conf",
      "+++ b/conf/spark-defaults.conf",
      "@@ -1,2 +1,3 @@",
      "- spark.sql.shuffle.partitions            200",
      "+ spark.sql.shuffle.partitions            800",
      "+ spark.memory.fraction                   0.75",
      "  spark.sql.adaptive.enabled              true",
      "",
    ].join("\n");
    expect(parseProposal(diff)).toEqual({ kind: "diff" });
  });

  it("recognises a deletion-only unified diff without treating it as an overlay", () => {
    expect(parseProposal([
      "--- a/conf/spark-defaults.conf",
      "+++ b/conf/spark-defaults.conf",
      "@@ -1 +0,0 @@",
      "- spark.sql.shuffle.partitions 200",
      "",
    ].join("\n"))).toEqual({ kind: "diff" });
  });

  it("does not call an EOF-truncated hunk a unified diff", () => {
    const truncated = [
      "--- a/x",
      "+++ b/x",
      "@@ -1 +1 @@",
      "-a",
      "+b",
    ].join("\n");
    expect(parseProposal(truncated)).toEqual({ kind: "unknown" });
    expect(parseProposal(`${truncated}\n`)).toEqual({ kind: "diff" });
  });

  it.each([
    "@@ -1 +1 @@\n+ spark.sql.shuffle.partitions 800",
    fixVerifications[0].proposed_diff,
    "+++ b/conf\n--- a/conf\n@@ -1 +1 @@\n-old\n+new",
    "--- a/conf\n+++ b/conf\n@@ conf/spark-defaults.conf @@\n-old\n+new",
    "--- a/conf\n+++ b/conf\n@@ -1 +1 @@\n+new",
  ])("keeps incomplete or legacy diff text unknown: %s", (proposal) => {
    expect(parseProposal(proposal)).toEqual({ kind: "unknown" });
  });

  it("preserves multiple hunks and files with git headers and an added file", () => {
    expect(parseProposal([
      "diff --git a/conf b/conf", "index abc..def 100644",
      "--- a/conf", "+++ b/conf", "@@ -1 +1 @@", "-old", "+new",
      "@@ -3 +3 @@ context", "-before", "+after",
      "diff --git a/new b/new", "new file mode 100644",
      "--- /dev/null", "+++ b/new", "@@ -0,0 +1 @@", "+added",
      "\\ No newline at end of file", "",
    ].join("\n"))).toEqual({ kind: "diff" });
  });

  it("distinguishes malformed JSON and unknown text", () => {
    expect(parseProposal("{not json")).toEqual({ kind: "invalid-json" });
    expect(parseProposal("")).toEqual({ kind: "unknown" });
    expect(parseProposal("enable AQE skew join")).toEqual({ kind: "unknown" });
    expect(parseProposal("+ spark.sql.shuffle.partitions 800")).toEqual({ kind: "unknown" });
    expect(parseProposal("@@ -1 +1 @@")).toEqual({ kind: "unknown" });
  });
});

describe("fmt renders absence as absence", () => {
  it("never prints undefined% for a Nullable column", () => {
    expect(fmt.pctOrDash(null)).toBe("—");
    expect(fmt.pctOrDash(undefined)).toBe("—");
    expect(fmt.pctOrDash(17.37)).toBe("17.4%");
  });

  it("keeps a missing count distinct from a counted zero", () => {
    expect(fmt.countOrDash(null)).toBe("—");
    expect(fmt.countOrDash(0)).toBe("0");
  });

  it("keeps an unsourced verdict distinct from a false one", () => {
    // mechanism_confirmed has no column in v0.5 and arrives null. Rendering it
    // as "false" convicts a fix on the strength of a column that does not exist.
    expect(fmt.verdict(null)).toBe("no source");
    expect(fmt.verdict(false)).toBe("false");
    expect(fmt.verdict(true)).toBe("true");
  });
});
