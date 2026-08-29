/**
 * The seven contract rules, as pure functions.
 *
 * Every refusal the UI shows is the return value of something in this file.
 * No screen re-derives a threshold, and no screen softens one: the same
 * function answers for engine, verify and serve, which is the only reason two
 * lanes cannot disagree about which stages a ratio may describe.
 */
import type { JobConfRow, PlanTransitionRow, SparkEventRow } from "./types";

/**
 * The measurability floor: 1 MiB per task.
 *
 * Below this volume, p99/p50 describes JVM warm-up and scheduler dispatch, not
 * a data distribution. This is a bound on what the measurement can mean — it is
 * NOT a tunable threshold, and softening it in one lane re-opens the
 * contradiction class the contract exists to close.
 */
export const VOLUME_FLOOR_BYTES_PER_TASK = 1024 * 1024;

export type RuleVerdict =
  | { held: true; reason: string }
  | { held: false; reason: string }
  | { vacant: true; reason: string };

export const isVacant = (v: RuleVerdict): v is { vacant: true; reason: string } =>
  "vacant" in v;

export type DataState<T> =
  | { state: "available"; value: T }
  | { state: "unavailable"; value: null }
  | { state: "not_comparable"; value: null };

/** Null and undefined are unavailable; zero remains a real available value. */
export function dataState<T>(value: T | null | undefined): DataState<T> {
  return value === null || value === undefined
    ? { state: "unavailable", value: null }
    : { state: "available", value };
}

/** An empty collection means no observation, not an observed count of zero. */
export function collectionState<T>(values: readonly T[]): DataState<readonly T[]> {
  return values.length === 0
    ? { state: "unavailable", value: null }
    : { state: "available", value: values };
}

/** Incompatibility wins over absence, so Compare can explain why no delta exists. */
export function comparisonState<T>(
  current: T | null | undefined,
  baseline: T | null | undefined,
  comparable: boolean,
): DataState<{ current: T; baseline: T }> {
  if (!comparable) return { state: "not_comparable", value: null };
  if (current === null || current === undefined || baseline === null || baseline === undefined)
    return { state: "unavailable", value: null };
  return { state: "available", value: { current, baseline } };
}

/* ------------------------------------------------------------------ rule 1 */

/**
 * RULE 1 — the tail-bound gate is computed, not configured.
 *
 *     p99/p50 > (n_tasks - 1) / (slots - 1)
 *
 * A fixed 5x or 10x threshold is WRONG: the bar depends on how many task slots
 * the cluster has. With one slot per task, any ratio is scheduling noise; with
 * one slot total, tasks queue and the ratio means something else entirely.
 */
export function tailBoundBar(nTasks: number, slots: number): number {
  if (slots <= 1) return Number.POSITIVE_INFINITY;
  return (nTasks - 1) / (slots - 1);
}

/**
 * The number of slots at which an observed ratio would exactly meet the bar.
 * Reported when cluster width is unknown, so the UI can say "tail-bound only
 * above N slots" instead of assuming a width.
 */
export function breakEvenSlots(nTasks: number, ratio: number): number {
  if (ratio <= 0) return Number.POSITIVE_INFINITY;
  return 1 + (nTasks - 1) / ratio;
}

/**
 * Rule 1's ratio, over task DURATION.
 *
 * CONTRACT.md §1 defines the tail on duration and notes that data volume
 * cancels — it scales p50 and p99 together. This console previously read a
 * bytes ratio, which the contract does not store and cannot supply: there is no
 * per-task byte distribution, only totals, so shuffle_read_bytes / task_count
 * is a MEAN and no p50/p99 of bytes can be recovered from it. Reading the
 * duration percentiles is not a preference; it is the only ratio that exists.
 */
export function ratioOf(
  row: Pick<SparkEventRow, "task_duration_p50_ms" | "task_duration_p99_ms">,
): number {
  if (row.task_duration_p50_ms <= 0) return 0;
  return row.task_duration_p99_ms / row.task_duration_p50_ms;
}

/**
 * Volume per task, for the measurability floor.
 *
 * Exact Engine semantics: bytes_touched is shuffle read + shuffle write +
 * input, divided by task_count. The Engine defaults an omitted additive byte
 * field to zero and returns zero when there are no tasks; the front does the
 * same calculation here, then uses bytesPerTaskState before making a UI claim.
 */
export function bytesPerTask(
  row: Pick<SparkEventRow, "shuffle_read_bytes" | "shuffle_write_bytes" | "input_bytes" | "task_count">,
): number {
  if (row.task_count <= 0) return 0;
  return (row.shuffle_read_bytes + row.shuffle_write_bytes + (row.input_bytes ?? 0)) /
    row.task_count;
}

/** Zero tasks cannot support a per-task claim even though Engine arithmetic returns 0. */
export function bytesPerTaskState(
  row: Pick<SparkEventRow, "shuffle_read_bytes" | "shuffle_write_bytes" | "input_bytes" | "task_count">,
): DataState<number> {
  return row.task_count <= 0
    ? { state: "unavailable", value: null }
    : { state: "available", value: bytesPerTask(row) };
}

export interface SuccessfulTaskDurationStats {
  p50Ms: number;
  p99Ms: number;
  maxMs: number;
  sampleCount: number;
}

/** v0.5's sample_count=0 convention: zeros without a sample are unavailable. */
export function successfulTaskDurationState(
  row: Partial<Pick<
    SparkEventRow,
    | "successful_task_duration_p50_ms"
    | "successful_task_duration_p99_ms"
    | "successful_task_duration_max_ms"
    | "successful_task_sample_count"
  >>,
): DataState<SuccessfulTaskDurationStats> {
  const sampleCount = row.successful_task_sample_count;
  if (
    sampleCount === undefined || sampleCount <= 0 ||
    row.successful_task_duration_p50_ms === undefined ||
    row.successful_task_duration_p99_ms === undefined ||
    row.successful_task_duration_max_ms === undefined
  ) return { state: "unavailable", value: null };

  return {
    state: "available",
    value: {
      p50Ms: row.successful_task_duration_p50_ms,
      p99Ms: row.successful_task_duration_p99_ms,
      maxMs: row.successful_task_duration_max_ms,
      sampleCount,
    },
  };
}

export function ruleOneTailBound(
  row: SparkEventRow,
  slots: number | null,
): RuleVerdict {
  const ratio = ratioOf(row);

  // RULE 6 first: with n <= slots the bar is undefined, so rule 1 is vacant.
  const six = ruleSixDistribution(row, slots);
  if (isVacant(six)) return six;

  if (slots === null) {
    const be = breakEvenSlots(row.task_count, ratio);
    return {
      vacant: true,
      reason:
        `cluster width unknown — spark.executor.instances absent from job_conf. ` +
        `Tail-bound only above ${be.toFixed(1)} slots.`,
    };
  }

  const bar = tailBoundBar(row.task_count, slots);
  return ratio > bar
    ? { held: true, reason: `p99/p50 ${ratio.toFixed(2)}x clears the computed bar ${bar.toFixed(2)}x (${row.task_count} tasks / ${slots} slots)` }
    : { held: false, reason: `p99/p50 ${ratio.toFixed(2)}x is under the computed bar ${bar.toFixed(2)}x — work-bound, not tail-bound` };
}

/* ------------------------------------------------------------------ rule 2 */

/**
 * RULE 2 — the noise floor is measured on this bench, never hardcoded.
 * Returns the half-spread of the replay set as a percentage of the mean.
 */
/**
 * Rule 2's floor, MEASURED from the replay set rather than trusted from a row,
 * so a stale stored value cannot mislead.
 *
 * Null input is not an edge case: contract v0.5 stores only the two arms'
 * medians, never the individual replay durations, so against the live store
 * there is nothing to recompute from and the caller must fall back to the
 * stored noise_floor_pct — and say that it did.
 */
export function measureNoiseFloorPct(replayDurationsMs: number[] | null): number | null {
  if (!replayDurationsMs || replayDurationsMs.length < 2) return null;
  const mean = replayDurationsMs.reduce((a, b) => a + b, 0) / replayDurationsMs.length;
  if (mean <= 0) return null;
  const spread = Math.max(...replayDurationsMs) - Math.min(...replayDurationsMs);
  return (spread / mean) * 100;
}

/** A predicted saving inside the measured floor is unresolvable — not zero. */
export function ruleTwoRuntimeResolvable(
  predictedSavingPct: number | null,
  noiseFloorPct: number | null,
): RuleVerdict {
  if (predictedSavingPct === null || noiseFloorPct === null)
    return { vacant: true, reason: "no replay set — nothing to resolve against" };
  return predictedSavingPct > noiseFloorPct
    ? { held: true, reason: `predicted ${predictedSavingPct.toFixed(1)}% clears the measured floor ${noiseFloorPct.toFixed(1)}%` }
    : {
        held: false,
        reason:
          `predicted ${predictedSavingPct.toFixed(1)}% sits inside the measured floor ` +
          `${noiseFloorPct.toFixed(1)}% — unresolvable, which is not the same as zero`,
      };
}

/* ------------------------------------------------------------------ rule 3 */

/**
 * RULE 3 — a delta is credited to tuning only with >= 2 DISTINCT
 * configurations. Values are canonicalised first: '5.0' and '5' are the same
 * config, and counting them twice manufactures evidence that does not exist.
 */
export function canonicaliseConfValue(value: string | null): string | null {
  if (value === null) return null;
  const v = value.trim().toLowerCase();
  if (v === "") return null;
  const n = Number(v);
  if (!Number.isNaN(n)) return String(n); // '5.0' -> '5', '0800' -> '800'
  if (v === "true" || v === "false") return v;
  return v;
}

export function distinctConfigCount(values: (string | null)[]): number {
  return new Set(
    values.map(canonicaliseConfValue).filter((v): v is string => v !== null),
  ).size;
}

export function ruleThreeAttributableToTuning(values: (string | null)[]): RuleVerdict {
  const n = distinctConfigCount(values);
  return n >= 2
    ? { held: true, reason: `${n} distinct configurations observed` }
    : {
        held: false,
        reason:
          `only ${n} distinct configuration after canonicalisation — a delta here ` +
          `cannot be credited to tuning`,
      };
}

/* ------------------------------------------------------------------ rule 4 */

/**
 * RULE 4 — mechanism and runtime are two verdicts, stored separately.
 * Neither is ever inferred from the other. A small bench can honestly deliver
 * the first and not the second.
 */
export interface DualVerdict {
  /** Null = no source in the contract. Not the same as "did not fire". */
  mechanism_confirmed: boolean | null;
  runtime_certified: boolean;
  runtime_verdict: "improved" | "regressed" | "unresolved";
}

export function ruleFourNoInference(v: DualVerdict): { ok: boolean; violation?: string } {
  if (v.runtime_certified && v.runtime_verdict === "unresolved")
    return { ok: false, violation: "certified but unresolved — contradictory" };
  // An UNKNOWN mechanism cannot convict: rule 4 forbids inferring one verdict
  // from the other, and treating null as false would do exactly that.
  if (v.mechanism_confirmed === false && v.runtime_certified)
    return {
      ok: false,
      violation: "runtime certified without a confirmed mechanism — coincidence, not causation",
    };
  return { ok: true };
}

/* ------------------------------------------------------------------ rule 5 */

/**
 * RULE 5 — absence of a skew_split is NOT evidence of absence of skew.
 * AQE only splits what it detects, on the shape it saw. A quiet transition log
 * licenses no claim in either direction.
 */
export function ruleFiveSkewAbsence(transitions: PlanTransitionRow[]): RuleVerdict {
  const split = transitions.some((t) => t.transition_type === "skew_split");
  return split
    ? { held: true, reason: "AQE reported skew_split — skew present, ground truth" }
    : {
        vacant: true,
        reason:
          "no skew_split in the transition log. AQE only splits what it detects; " +
          "absence is not evidence of absence — no claim either way",
      };
}

/* ------------------------------------------------------------------ rule 6 */

/**
 * RULE 6 — with n_tasks <= slots there is no distribution to describe.
 * p99 and p50 land on the same task, rule 1's bar is undefined, and the stage
 * is EXCLUDED rather than cleared. "Two tasks are not a distribution."
 */
export function ruleSixDistribution(
  row: Pick<SparkEventRow, "task_count">,
  slots: number | null,
): RuleVerdict {
  if (row.task_count <= 1)
    return { vacant: true, reason: `${row.task_count} task — p99 and p50 describe the same task` };
  if (slots !== null && row.task_count <= slots)
    return {
      vacant: true,
      reason: `${row.task_count} tasks <= ${slots} slots — no queueing, so rule 1's bar is undefined`,
    };
  if (row.task_count <= 2)
    return { vacant: true, reason: "2 tasks are not a distribution — rule 1 vacant, stage excluded" };
  return { held: true, reason: `${row.task_count} tasks — a distribution exists` };
}

/* ------------------------------------------------------------------ rule 7 */

/**
 * RULE 7 — detect an AQE reshape by comparing the observed task count against
 * the CONFIGURED partition count from job_conf.
 *
 * When they differ, bytes/task is a POST-intervention measurement: the volume
 * floor then measured the healed state, not the state that caused the problem.
 * This is the honest edge the contract documents rather than hides — and the
 * remedy is this detection, not a softer floor.
 */
export function ruleSevenReshaped(
  row: Pick<SparkEventRow, "task_count">,
  configuredPartitions: number | null,
): RuleVerdict {
  if (configuredPartitions === null)
    return { vacant: true, reason: "spark.sql.shuffle.partitions absent from job_conf" };
  if (row.task_count === configuredPartitions)
    return { held: false, reason: `${row.task_count} tasks = configured ${configuredPartitions} — not reshaped` };
  return {
    held: true,
    reason:
      `${row.task_count} tasks vs configured ${configuredPartitions} — AQE reshaped this ` +
      `exchange, so bytes/task is a post-intervention measurement`,
  };
}

/* ------------------------------------------------- attribution & composition */

/** v0.5 still carries no execution -> stage map, so a transition cannot name a stage. */
export function attributionIsAvailable(): boolean {
  return false;
}

export function readSlots(conf: JobConfRow[]): number | null {
  const instances = conf.find((c) => c.key === "spark.executor.instances")?.value ?? null;
  const cores = conf.find((c) => c.key === "spark.executor.cores")?.value ?? null;
  if (instances === null || cores === null) return null; // absent stays absent
  const n = Number(instances) * Number(cores);
  return Number.isFinite(n) && n > 0 ? n : null;
}

export function readConfiguredPartitions(conf: JobConfRow[]): number | null {
  const v = conf.find((c) => c.key === "spark.sql.shuffle.partitions")?.value ?? null;
  if (v === null) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

/** Is a flag already at the value a fix would propose? Then the fix text lies. */
export function noOpGate(conf: JobConfRow[], key: string, proposed: string): RuleVerdict {
  const current = canonicaliseConfValue(conf.find((c) => c.key === key)?.value ?? null);
  const target = canonicaliseConfValue(proposed);
  if (current === null) return { vacant: true, reason: `${key} absent — cannot evaluate` };
  return current === target
    ? { held: false, reason: `${key} is already ${current} — "enable it" is a no-op` }
    : { held: true, reason: `${key}: ${current} -> ${target} is a real change` };
}

export type RefusalCode =
  | "below_volume_floor"
  | "not_a_distribution"
  | "work_bound"
  | "cluster_width_unknown"
  | "post_intervention";

export interface StageAssessment {
  stage: SparkEventRow;
  ratio: number;
  bytesPerTask: number;
  /** Did rule 1's computed bar clear? */
  ruleOne: RuleVerdict;
  ruleSix: RuleVerdict;
  ruleSeven: RuleVerdict;
  breakEvenSlots: number;
  aboveVolumeFloor: boolean;
  /** True only when every gate holds. Anything else is a documented refusal. */
  reportable: boolean;
  refusal: { code: RefusalCode; text: string } | null;
  /** A second fact that changes how the refusal should be read. Rule 7 lands
   *  here: the stage fell under the floor, AND the floor measured the healed
   *  state. Both are true and the UI shows both. */
  caveat: string | null;
}

/**
 * The whole assessment chain for one stage, in the order the engine applies it.
 * The UI renders this object; it never re-decides any part of it.
 */
export function assessStage(
  stage: SparkEventRow,
  conf: JobConfRow[],
): StageAssessment {
  const slots = readSlots(conf);
  const configured = readConfiguredPartitions(conf);
  const ratio = ratioOf(stage);
  const bpt = bytesPerTask(stage);
  const aboveFloor = bpt >= VOLUME_FLOOR_BYTES_PER_TASK;

  const six = ruleSixDistribution(stage, slots);
  const one = ruleOneTailBound(stage, slots);
  const seven = ruleSevenReshaped(stage, configured);

  let refusal: StageAssessment["refusal"] = null;
  let caveat: string | null = null;

  // Rule 7 never overrides another gate — it qualifies whatever the gate said,
  // because a reshaped stage was measured AFTER the intervention.
  const reshaped = !isVacant(seven) && seven.held === true;
  if (reshaped) caveat = seven.reason;

  if (isVacant(six)) {
    refusal = { code: "not_a_distribution", text: six.reason };
  } else if (!aboveFloor) {
    const pctOfFloor = (bpt / VOLUME_FLOOR_BYTES_PER_TASK) * 100;
    const nearMiss = pctOfFloor >= 90;
    refusal = {
      code: reshaped ? "post_intervention" : "below_volume_floor",
      text: nearMiss
        ? `${Math.round(bpt).toLocaleString()} B/task — ${pctOfFloor.toFixed(0)}% of the ` +
          `1 MiB floor, excluded by a ${(100 - pctOfFloor).toFixed(0)}% margin`
        : `${Math.round(bpt).toLocaleString()} B/task is under the 1 MiB measurability ` +
          `floor — scheduler jitter, not a distribution`,
    };
  } else if (isVacant(one)) {
    refusal = { code: "cluster_width_unknown", text: one.reason };
  } else if (one.held === false) {
    refusal = { code: "work_bound", text: one.reason };
  }

  return {
    stage,
    ratio,
    bytesPerTask: bpt,
    ruleOne: one,
    ruleSix: six,
    ruleSeven: seven,
    breakEvenSlots: breakEvenSlots(stage.task_count, ratio),
    aboveVolumeFloor: aboveFloor,
    reportable: refusal === null,
    refusal,
    caveat,
  };
}

/** Formatting helpers used by every screen, so units never drift between them. */
export const fmt = {
  bytes(n: number): string {
    const u = ["B", "KiB", "MiB", "GiB", "TiB"];
    let i = 0;
    let v = n;
    while (v >= 1024 && i < u.length - 1) {
      v /= 1024;
      i++;
    }
    return `${v.toFixed(i === 0 ? 0 : 2)} ${u[i]}`;
  },
  bytesExact(n: number): string {
    return Math.round(n).toLocaleString("en-US");
  },
  /**
   * Scale-aware, because the same field spans six orders of magnitude here: a
   * run's wall clock is minutes, while a single shape's task time can be tens
   * of milliseconds. Formatting everything as MmSSs printed "0m00s" on every
   * bar of the plan-memory chart — a real measurement rendered as nothing.
   */
  duration(ms: number): string {
    if (!Number.isFinite(ms)) return "—";
    if (Math.abs(ms) < 1000) return `${Math.round(ms)} ms`;
    if (Math.abs(ms) < 60000) return `${(ms / 1000).toFixed(1)} s`;
    const m = Math.floor(ms / 60000);
    const s = Math.round((ms % 60000) / 1000);
    return `${m}m${String(s).padStart(2, "0")}s`;
  },
  /**
   * A duration the contract may not have captured. Lives here, not in a screen,
   * so "we did not measure this" renders identically everywhere — an em dash,
   * never 0m00s, which would assert a measurement of zero.
   */
  durationOrDash(ms: number | null): string {
    return ms === null ? "—" : fmt.duration(ms);
  },
  ratio(r: number): string {
    return `${r.toFixed(2)}x`;
  },
  pct(n: number): string {
    return `${n > 0 ? "+" : ""}${n.toFixed(1)}%`;
  },
  shortJob(id: string): string {
    return id.length > 12 ? `...${id.slice(-9)}` : id;
  },
};
