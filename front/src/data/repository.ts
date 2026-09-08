/**
 * The seam between the console and its data.
 *
 * ClickHouseRepository queries the database from the browser (the choice for
 * this bench). FixtureRepository serves the recorded run. Swapping in an
 * HttpRepository against serve/ means implementing this one interface — no
 * screen changes, because no screen knows where a row came from.
 */
import type {
  FindingRow, FixVerificationRow, JobConfRow, PlanTransitionRow,
  RunSummary, SparkEventRow,
} from "@/contract/types";
import * as fx from "./fixtures";
import * as Q from "./queries";
import { ping, query } from "./clickhouse";
import { runtimeConfig } from "./runtimeConfig";

/** A plan shape the memory lane indexed, plus how often it has run. */
export interface PlanShape {
  plan_fingerprint: string;
  run_count: number;
  first_run: string;
  last_run: string;
  node_count: number;
  join_count: number;
  agg_count: number;
  exchange_count: number;
  scan_count: number;
  max_depth: number;
  has_udf: number;
}

/** One run of one shape. conf_* is null when the jar emitted no job_conf. */
export interface ShapeRun {
  job_id: string;
  app_name: string;
  task_time_ms: number;
  finding_count: number;
  severity_rank: number;
  config_source: string;
  conf_shuffle_partitions: number | null;
  conf_executor_instances: number | null;
  conf_executor_cores: number | null;
  conf_executor_memory_mb: number | null;
  observed_at: string;
}

/** A run that shares at least one plan shape with the run being compared. */
export interface BaselineCandidate {
  job_id: string;
  app_name: string;
  shared_shapes: number;
  observed_at: string;
}

export interface Repository {
  readonly kind: "clickhouse" | "fixtures";
  listRuns(limit?: number): Promise<(RunSummary & { age?: string })[]>;
  /** One run's summary row. null when the job is unknown — never a synthesised zero. */
  run(jobId: string): Promise<(RunSummary & { age?: string }) | null>;
  /** Other runs that executed at least one of this run's plan shapes, newest first. */
  baselineCandidates(jobId: string): Promise<BaselineCandidate[]>;
  /** Plan shapes the memory lane knows, most-run first. */
  planShapes(): Promise<PlanShape[]>;
  /** Every run of one shape, oldest first — the history rule 3 reasons over. */
  shapeRuns(fingerprint: string): Promise<ShapeRun[]>;
  stages(jobId: string): Promise<SparkEventRow[]>;
  jobConf(jobId: string): Promise<JobConfRow[]>;
  findings(jobId: string): Promise<FindingRow[]>;
  transitions(jobId: string): Promise<PlanTransitionRow[]>;
  fixVerification(findingId: string): Promise<FixVerificationRow | null>;
}

const relativeAge = (iso: string): string => {
  const then = new Date(iso.replace(" ", "T") + "Z").getTime();
  if (!Number.isFinite(then)) return "";
  const h = Math.max(0, Math.round((Date.now() - then) / 3600000));
  return h < 1 ? "now" : h < 24 ? `${h}h` : `${Math.round(h / 24)}d`;
};

const statusOf = (findings: number, critical: boolean): RunSummary["status"] =>
  findings === 0 ? "healthy" : critical ? "degraded" : "warning";

/** The shape RUN_LIST and RUN_ONE both return — one rollup, one mapping. */
interface RunRollupRow {
  job_id: string; app_name: string; stage_count: number; started_at: string;
  finding_count: number; has_critical: number; task_time_ms: number;
  plan_fingerprint: string; shape_count: number; shaped_stage_count: number;
  config_source: string;
  conf_executor_instances: number | null; conf_shuffle_partitions: number | null;
}

/** ClickHouse renders Nullable(Int32) as JSON null; anything else is a real value. */
const nullableInt = (v: number | null): number | null =>
  v === null || v === undefined ? null : Number(v);

/** -1 is the query's sentinel for "this run is not indexed", not a measurement. */
const notIndexed = (v: number): number | null => (Number(v) < 0 ? null : Number(v));

// refused_count is DERIVED, never stored: it is the count of stages the engine
// evaluated for a tail claim and declined. Computing it needs the stage rows,
// so the list shows it per-run only once opened.
const toRunSummary = (r: RunRollupRow): RunSummary & { age?: string } => ({
  job_id: r.job_id,
  app_name: r.app_name,
  stage_count: Number(r.stage_count),
  wall_clock_ms: null, // not captured by the contract — see RunSummary
  task_time_ms: notIndexed(r.task_time_ms),
  finding_count: Number(r.finding_count),
  refused_count: -1, // -1 renders as "—", never as zero
  llm_calls: 0,
  status: statusOf(Number(r.finding_count), Boolean(Number(r.has_critical))),
  plan_fingerprint: r.plan_fingerprint,
  shape_count: Number(r.shape_count),
  shaped_stage_count: notIndexed(r.shaped_stage_count),
  config_source: r.config_source,
  conf_executor_instances: nullableInt(r.conf_executor_instances),
  conf_shuffle_partitions: nullableInt(r.conf_shuffle_partitions),
  started_at: r.started_at,
  age: relativeAge(r.started_at),
});

export class ClickHouseRepository implements Repository {
  readonly kind = "clickhouse" as const;

  async listRuns(limit = 50) {
    const rows = await query<RunRollupRow>(Q.RUN_LIST, { limit });
    return rows.map(toRunSummary);
  }

  async run(jobId: string) {
    const rows = await query<RunRollupRow>(Q.RUN_ONE, { job: jobId });
    return rows[0] ? toRunSummary(rows[0]) : null;
  }

  baselineCandidates(jobId: string) {
    return query<BaselineCandidate>(Q.RUNS_SHARING_SHAPE, { job: jobId });
  }

  planShapes() {
    return query<PlanShape>(Q.PLAN_SHAPES);
  }
  shapeRuns(fingerprint: string) {
    return query<ShapeRun>(Q.SHAPE_RUNS, { fingerprint });
  }

  stages(jobId: string) {
    return query<SparkEventRow>(Q.LATEST_STAGES, { job: jobId });
  }
  jobConf(jobId: string) {
    return query<JobConfRow>(Q.JOB_CONF, { job: jobId });
  }
  findings(jobId: string) {
    return query<FindingRow>(Q.FINDINGS, { job: jobId });
  }
  transitions(jobId: string) {
    return query<PlanTransitionRow>(Q.PLAN_TRANSITIONS, { job: jobId });
  }
  async fixVerification(findingId: string) {
    const rows = await query<Record<string, unknown>>(Q.FIX_VERIFICATIONS, { finding: findingId });
    const r = rows[0];
    if (!r) return null;
    // The query already renamed, flipped the sign and applied rule 2. What it
    // cannot supply, it returns as NULL, and that travels through as null —
    // mechanism_confirmed has no column, and the individual replay durations
    // were never stored, only the two arms' medians.
    return {
      fix_id: String(r.fix_id),
      finding_id: String(r.finding_id),
      job_id: String(r.job_id),
      mechanism_confirmed: r.mechanism_confirmed === null ? null : Boolean(Number(r.mechanism_confirmed)),
      runtime_certified: Boolean(Number(r.runtime_certified)),
      runtime_verdict: r.runtime_verdict as FixVerificationRow["runtime_verdict"],
      predicted_saving_pct: r.predicted_saving_pct === null ? null : Number(r.predicted_saving_pct),
      noise_floor_pct: r.noise_floor_pct === null ? null : Number(r.noise_floor_pct),
      replay_count: Number(r.replay_count ?? 0),
      replay_durations_ms: null,
      cluster_slots: r.cluster_slots === null ? null : Number(r.cluster_slots),
      requires_human_approval: true as const,
      applied: false as const,
      proposed_diff: String(r.proposed_diff ?? ""),
    };
  }
}

export class FixtureRepository implements Repository {
  readonly kind = "fixtures" as const;

  async listRuns() {
    return fx.runs;
  }
  async run(jobId: string) {
    return fx.runs.find((r) => r.job_id === jobId) ?? null;
  }
  async baselineCandidates(jobId: string) {
    // The recording holds one comparable pair, and it is the pair the README's
    // walkthrough describes. Anything else would be inventing shared history.
    const other = jobId === fx.CURRENT_JOB ? fx.BASELINE_JOB
                : jobId === fx.BASELINE_JOB ? fx.CURRENT_JOB
                : null;
    if (!other) return [];
    const r = fx.runs.find((x) => x.job_id === other);
    return r ? [{ job_id: r.job_id, app_name: r.app_name, shared_shapes: 1,
                  observed_at: r.started_at }] : [];
  }
  async planShapes() {
    return fx.planShapes;
  }
  async shapeRuns(fingerprint: string) {
    return fingerprint === fx.PLAN_FINGERPRINT ? fx.shapeRuns : [];
  }
  async stages(jobId: string) {
    return fx.stagesByJob[jobId] ?? [];
  }
  async jobConf(jobId: string) {
    return fx.jobConfByJob[jobId] ?? [];
  }
  async findings(jobId: string) {
    return fx.findingsByJob[jobId] ?? [];
  }
  async transitions(jobId: string) {
    return fx.transitionsByJob[jobId] ?? [];
  }
  async fixVerification(findingId: string) {
    return fx.fixVerifications.find((f) => f.finding_id === findingId) ?? null;
  }
}

export async function resolveRepository(): Promise<Repository> {
  // Runtime, so a single production image can be started against fixtures,
  // pinned to ClickHouse, or left to probe — without a rebuild.
  const mode = runtimeConfig.dataSource;
  if (mode === "fixtures") return new FixtureRepository();
  if (mode === "clickhouse") return new ClickHouseRepository();
  return (await ping()) ? new ClickHouseRepository() : new FixtureRepository();
}
