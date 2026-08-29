/**
 * Row shapes for the frozen Apex contract, v0.5.
 *
 * SparkEventContractV05 mirrors the canonical DDL field for field. SparkEventRow
 * is the console's intentionally narrower projection: additive fields are
 * optional there until a query selects them, so absence remains observable.
 */
export const CONTRACT_VERSION = "0.5" as const;

export type Confidence = "HIGH" | "BEST_EFFORT";
export type Severity = "critical" | "warning" | "info";

/** One canonical row per (job_id, stage_id, stage_attempt). */
export interface SparkEventContractV05 {
  job_id: string;
  app_id: string;
  app_name: string;
  stage_id: number;
  stage_attempt: number;
  ts: string;
  shuffle_read_bytes: number;
  shuffle_write_bytes: number;
  spill_disk_bytes: number;
  spill_mem_bytes: number;
  gc_time_ms: number;
  executor_run_time_ms: number;
  input_bytes: number;
  output_bytes: number;
  peak_execution_mem_bytes: number;
  task_count: number;
  task_duration_p50_ms: number;
  task_duration_p99_ms: number;
  task_duration_max_ms: number;
  task_duration_sample_count: number;
  successful_task_duration_p50_ms: number;
  successful_task_duration_p99_ms: number;
  successful_task_duration_max_ms: number;
  successful_task_sample_count: number;
  successful_task_shuffle_read_bytes_p50: number;
  successful_task_shuffle_read_bytes_max: number;
  successful_task_shuffle_read_bytes_sample_count: number;
  task_attempt_count: number;
  task_failed_attempt_count: number;
  task_counted_failure_attempt_count: number;
  task_killed_attempt_count: number;
  task_speculative_attempt_count: number;
  plan_fingerprint: string;
  plan_json: string;
  attributes: Record<string, string>;
}

type SparkEventProjectionCore = Pick<
  SparkEventContractV05,
  | "job_id"
  | "app_name"
  | "stage_id"
  | "stage_attempt"
  | "task_count"
  | "shuffle_read_bytes"
  | "shuffle_write_bytes"
  | "spill_mem_bytes"
  | "spill_disk_bytes"
  | "peak_execution_mem_bytes"
  | "gc_time_ms"
  | "task_duration_p50_ms"
  | "task_duration_p99_ms"
  | "plan_fingerprint"
  | "ts"
>;

type SparkEventProjectionAdditions = Omit<
  SparkEventContractV05,
  keyof SparkEventProjectionCore
>;

/** Latest console projection via argMax(col, ts). Unselected fields stay absent. */
export type SparkEventRow = SparkEventProjectionCore &
  Partial<SparkEventProjectionAdditions> & {
  /**
   * NOT CAPTURED. The contract stores no stage name, and plan_json — the only
   * other text on the row — is a redacted Catalyst tree-string its own DDL says
   * must never be parsed. A label derived from it would be an invention, so the
   * DAG falls back to the stage id.
   */
  stage_name: string | null;
  /**
   * The stage's plan shape. Stage IDS move between runs; fingerprints do not,
   * so this is the only sound key for pairing a stage across two runs. Empty
   * when the stage carried no fingerprint — such a stage cannot be paired.
   */
  };

/** Runtime re-planning decisions captured from Spark's own AQE listener. */
export interface PlanTransitionRow {
  job_id: string;
  /** v0.5 keys transitions by (job_id, execution_id) and carries NO
   *  execution -> stage map. See rules.ts, attributionIsAvailable(). */
  execution_id: number;
  transition_type: "skew_split" | "join_strategy" | "coalesce" | "other";
  /** Monotonic per execution_id. The latest re-plan is the one with max(update_seq). */
  update_seq: number;
  /** UNTRUSTED: written by the observed job. Render as data, never evaluate. */
  detail: string;
  before: string;
  after: string;
  confidence: Confidence;
  /**
   * NOT a column of plan_transitions — joined from spark_events, where the
   * fingerprint actually lives. Empty when the job has no fingerprinted stage.
   */
  plan_fingerprint: string;
  ts: string;
}

/** The resolved configuration the job actually ran with — not the repository's. */
export interface JobConfRow {
  job_id: string;
  key: string;
  /** Absent keys are ABSENT. Never defaulted, never synthesised. */
  value: string | null;
  ts: string;
}

export interface FindingRow {
  finding_id: string;
  job_id: string;
  /** -1 means job-level: the contract could not attribute this to a stage. */
  stage_id: number;
  type: "SPILL" | "AQE_REPLAN" | "SKEW" | "DUPLICATE_SCAN" | "GC_PRESSURE";
  severity: Severity;
  confidence: Confidence;
  /** The raw 0..1 the contract routes. Rank on this, never on the display tier. */
  confidence_score: number;
  detected_by: string;
  /** UNTRUSTED, all four. */
  evidence: string;
  impact: string;
  fix: string;
  hot_key: string;
  ts: string;
}

export interface PlanMemoryRow {
  plan_fingerprint: string;
  app_name: string;
  run_count: number;
  first_seen: string;
  last_seen: string;
  /** Distinct configurations tried, not attempts. Rule 3 depends on the
   *  difference between these two numbers. */
  distinct_configs: number;
  attempts: number;
}

export interface FixVerificationRow {
  /** apex.fix_verifications.verification_id — one row per verification attempt. */
  fix_id: string;
  finding_id: string;
  job_id: string;
  /**
   * Verdict one: did the fix demonstrably fire?
   *
   * NO SOURCE. Nothing in the contract asserts it. The nearest columns —
   * method='replayed', safe=1 — say something was executed safely, which is a
   * different claim. Null keeps the two verdicts of rule 4 independent instead
   * of quietly deriving one from the other.
   */
  mechanism_confirmed: boolean | null;
  /**
   * Verdict two: is the runtime delta separable from noise? Independent.
   * DERIVED, not stored: |measured_delta_pct| > noise_floor_pct — rule 2 in SQL.
   */
  runtime_certified: boolean;
  runtime_verdict: "improved" | "regressed" | "unresolved";
  /**
   * apex.fix_verifications.predicted_delta_pct, SIGN INVERTED on read: the
   * column is a signed delta where negative means faster, while the console
   * speaks of a saving, where positive means faster.
   */
  predicted_saving_pct: number | null;
  /** MEASURED from replays on this bench. Never a constant. Nullable in the table. */
  noise_floor_pct: number | null;
  /** apex.fix_verifications.replay_reps — repetitions PER ARM, not the total. */
  replay_count: number;
  /**
   * NO SOURCE. The table keeps only the two arms' medians (baseline_ms,
   * treatment_ms); the individual replay durations were never stored.
   */
  replay_durations_ms: number[] | null;
  /** DERIVED from run_outcomes: conf_executor_instances x conf_executor_cores. */
  cluster_slots: number | null;
  requires_human_approval: true;
  applied: false;
  /** apex.fix_verifications.proposed_config — the conf overlay as JSON, not a diff. */
  proposed_diff: string;
}

/**
 * A run as the console lists it. Rolled up from apex.run_outcomes, whose grain
 * is one row per (plan_fingerprint, job_id).
 */
export interface RunSummary {
  job_id: string;
  app_name: string;
  stage_count: number;
  /**
   * NOT CAPTURED by the current contract, and null says exactly that.
   *
   * spark_events has no stage duration, and run_outcomes.wall_clock_ms is the
   * timestamp span of ONE plan shape — its own DDL calls it "context, not the
   * cost metric" and it is 0 for a single-stage shape. Nothing in the contract
   * stores how long a run took, so nothing here may claim to.
   */
  wall_clock_ms: number | null;
  /**
   * sum(task_count * p50) over the run's shapes. Summable, defined, stored —
   * the only run-level cost figure the contract keeps. Null where it was not
   * captured; 0 would assert "measured, and it was nothing".
   */
  task_time_ms: number | null;
  finding_count: number;
  /** Stages that carried a tail and produced no claim. */
  refused_count: number;
  llm_calls: number;
  status: "healthy" | "warning" | "degraded" | "failed";
  /** The dominant shape's fingerprint. Meaningful alone only when shape_count is 1. */
  plan_fingerprint: string;
  /** Distinct plan shapes in this run. >1 means plan_fingerprint is a choice. */
  shape_count: number;
  /**
   * Stages a plan shape claims, which is ≤ stage_count: the memory lane excludes
   * any stage whose plan_fingerprint is absent, because a shape meaning "no plan"
   * would match every job to every other. Null when the run is not indexed.
   */
  shaped_stage_count: number | null;
  /** 'observed' | 'zest-seed' | 'unknown'. 'unknown' ⇒ every conf_* is null. */
  config_source: string;
  /** Rule 1's cluster width, when the jar emitted job_conf. Null is ABSENT. */
  conf_executor_instances: number | null;
  /** Rule 7's configured partitions. Null is ABSENT, never a default. */
  conf_shuffle_partitions: number | null;
  started_at: string;
}
