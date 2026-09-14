/**
 * The recorded six-lane gate run, embellished to a richer job so every screen
 * has something to show. Shapes match src/contract/types.ts exactly.
 *
 * These are FIXTURES, not defaults: when ClickHouse answers, nothing here is
 * read. `make up-fixtures` runs the console against this file alone.
 */
import type {
  FindingRow, FixVerificationRow, JobConfRow, PlanTransitionRow,
  RunSummary, SparkEventRow,
} from "@/contract/types";
import type { PlanShape, ShapeRun } from "./repository";

export const PLAN_FINGERPRINT = "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0";
export const CURRENT_JOB = "app-20260803014217-0071";
export const BASELINE_JOB = "app-20260802231455-0069";

/**
 * The recorded gate run, as it was captured — before run_outcomes existed.
 *
 * The contract fields that table would supply are attached in `runs` below
 * rather than written into each literal, so this array stays what it is: a
 * recording, not a hand-authored answer to a schema that postdates it.
 */
type RecordedRun = Omit<
  RunSummary,
  "task_time_ms" | "shape_count" | "shaped_stage_count" | "config_source"
  | "conf_executor_instances" | "conf_shuffle_partitions"
> & { age: string };

const recordedRuns: RecordedRun[] = [
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_count": 34,
    "wall_clock_ms": 1084000,
    "finding_count": 2,
    "refused_count": 5,
    "llm_calls": 0,
    "status": "degraded",
    "age": "12m",
    "plan_fingerprint": "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803002911-0070",
    "app_name": "customer_segment_join",
    "stage_count": 21,
    "wall_clock_ms": 401000,
    "finding_count": 1,
    "refused_count": 4,
    "llm_calls": 1,
    "status": "warning",
    "age": "1h",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_count": 34,
    "wall_clock_ms": 712000,
    "finding_count": 1,
    "refused_count": 6,
    "llm_calls": 0,
    "status": "warning",
    "age": "3h",
    "plan_fingerprint": "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802194030-0068",
    "app_name": "sessionize_events",
    "stage_count": 12,
    "wall_clock_ms": 138000,
    "finding_count": 1,
    "refused_count": 2,
    "llm_calls": 0,
    "status": "degraded",
    "age": "5h",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802181203-0067",
    "app_name": "dim_product_scd2",
    "stage_count": 19,
    "wall_clock_ms": 247000,
    "finding_count": 0,
    "refused_count": 3,
    "llm_calls": 0,
    "status": "healthy",
    "age": "6h",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802164418-0066",
    "app_name": "bad_shuffle_probe",
    "stage_count": 8,
    "wall_clock_ms": 96000,
    "finding_count": 2,
    "refused_count": 1,
    "llm_calls": 1,
    "status": "degraded",
    "age": "8h",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802142250-0065",
    "app_name": "generate_data",
    "stage_count": 6,
    "wall_clock_ms": 54000,
    "finding_count": 0,
    "refused_count": 0,
    "llm_calls": 0,
    "status": "healthy",
    "age": "10h",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802103317-0064",
    "app_name": "driver_oom_probe",
    "stage_count": 4,
    "wall_clock_ms": 22000,
    "finding_count": 1,
    "refused_count": 0,
    "llm_calls": 0,
    "status": "failed",
    "age": "14h",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260729180235-0044",
    "app_name": "apex-skew_join-aqe",
    "stage_count": 20,
    "wall_clock_ms": 191000,
    "finding_count": 2,
    "refused_count": 5,
    "llm_calls": 1,
    "status": "healthy",
    "age": "5d",
    "plan_fingerprint": "n/a",
    "started_at": "2026-08-03 01:42:17"
  }
];

/**
 * Every field run_outcomes would carry is null or 'unknown' here, deliberately.
 *
 * This recording predates the table, so claiming a task time or a cluster width
 * for it would be inventing an observation. The detail screen still reads the
 * per-job job_conf fixture, which IS recorded — the list simply does not carry
 * config, and says so rather than defaulting.
 */
export const runs: (RunSummary & { age: string })[] = recordedRuns.map((r) => ({
  ...r,
  task_time_ms: null,
  shape_count: 1,
  shaped_stage_count: null,
  config_source: "unknown",
  conf_executor_instances: null,
  conf_shuffle_partitions: null,
}));

/**
 * Stage rows as recorded. plan_fingerprint is attached in `stagesByJob` below:
 * the recording predates the field, and the two daily_revenue_rollup runs are
 * the pair the README's walkthrough compares, so they — and only they — carry
 * the shared shape. Giving every job the same fingerprint would make every run
 * look comparable to every other, which is the failure the memory lane's own
 * DDL warns about.
 */
const recordedStages: Record<
  string,
  Omit<SparkEventRow, "plan_fingerprint" | "input_bytes">[]
> = {
  "app-20260803014217-0071": [
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 1,
    "stage_name": "Scan orders",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 94371840000,
    "shuffle_write_bytes": 86822092800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 471859200,
    "task_duration_p99_ms": 490733568,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 4,
    "stage_name": "Scan customers",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 31250,
    "shuffle_write_bytes": 28750,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 625,
    "task_duration_p99_ms": 3344,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 6,
    "stage_name": "Exchange orders",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 21350,
    "shuffle_write_bytes": 19642,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 427,
    "task_duration_p99_ms": 4684,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 11,
    "stage_name": "Exchange custs",
    "stage_attempt": 1,
    "task_count": 2,
    "shuffle_read_bytes": 8536800,
    "shuffle_write_bytes": 7853856,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 4268400,
    "task_duration_p99_ms": 30689796,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 25,
    "stage_name": "SortMergeJoin",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 50465865600,
    "shuffle_write_bytes": 46428596352,
    "spill_mem_bytes": 51753517056,
    "spill_disk_bytes": 8160437862,
    "peak_execution_mem_bytes": 17179869184,
    "gc_time_ms": 41200,
    "task_duration_p50_ms": 252329328,
    "task_duration_p99_ms": 358307646,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 29,
    "stage_name": "AQEShuffleRead",
    "stage_attempt": 1,
    "task_count": 114,
    "shuffle_read_bytes": 113632008,
    "shuffle_write_bytes": 104541447,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 996772,
    "task_duration_p99_ms": 10446171,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 31,
    "stage_name": "HashAggregate",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 2265395200,
    "shuffle_write_bytes": 2084163584,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 11326976,
    "task_duration_p99_ms": 14838339,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 33,
    "stage_name": "Exchange rollup",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 683700,
    "shuffle_write_bytes": 629004,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 6837,
    "task_duration_p99_ms": 52508,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 34,
    "stage_name": "Write delta",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 2018634900,
    "shuffle_write_bytes": 1857144108,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 20186349,
    "task_duration_p99_ms": 22003120,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 2,
    "stage_name": "Project",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 1840000,
    "shuffle_write_bytes": 1692800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 92000,
    "task_duration_p99_ms": 402960,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 3,
    "stage_name": "Filter",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 920000,
    "shuffle_write_bytes": 846400,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 18400,
    "task_duration_p99_ms": 26496,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 5,
    "stage_name": "Scan calendar",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 32000000,
    "shuffle_write_bytes": 29440000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 640000,
    "task_duration_p99_ms": 652800,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 7,
    "stage_name": "Exchange dim",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 340000,
    "shuffle_write_bytes": 312800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 3400,
    "task_duration_p99_ms": 12036,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 8,
    "stage_name": "LocalTableScan",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 240000000,
    "shuffle_write_bytes": 220800000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 2400000,
    "task_duration_p99_ms": 3456000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 9,
    "stage_name": "BroadcastExchange",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 128000000,
    "shuffle_write_bytes": 117760000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 640000,
    "task_duration_p99_ms": 1459200,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 10,
    "stage_name": "Sort",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 3680000,
    "shuffle_write_bytes": 3385600,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 18400,
    "task_duration_p99_ms": 72864,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 12,
    "stage_name": "WindowExec",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 48000000,
    "shuffle_write_bytes": 44160000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 2400000,
    "task_duration_p99_ms": 6480000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 13,
    "stage_name": "Coalesce",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 1840000,
    "shuffle_write_bytes": 1692800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 92000,
    "task_duration_p99_ms": 402960,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 14,
    "stage_name": "Union",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 920000,
    "shuffle_write_bytes": 846400,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 18400,
    "task_duration_p99_ms": 26496,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 15,
    "stage_name": "Project",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 445000000,
    "shuffle_write_bytes": 409400000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 8900000,
    "task_duration_p99_ms": 27768000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 16,
    "stage_name": "Filter",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 32000000,
    "shuffle_write_bytes": 29440000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 640000,
    "task_duration_p99_ms": 652800,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 17,
    "stage_name": "Scan calendar",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 9200000,
    "shuffle_write_bytes": 8464000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 92000,
    "task_duration_p99_ms": 171120,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 18,
    "stage_name": "Exchange dim",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 340000,
    "shuffle_write_bytes": 312800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 3400,
    "task_duration_p99_ms": 12036,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 19,
    "stage_name": "LocalTableScan",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 240000000,
    "shuffle_write_bytes": 220800000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 2400000,
    "task_duration_p99_ms": 3456000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 20,
    "stage_name": "BroadcastExchange",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 128000000,
    "shuffle_write_bytes": 117760000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 640000,
    "task_duration_p99_ms": 1459200,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 21,
    "stage_name": "Sort",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 3680000,
    "shuffle_write_bytes": 3385600,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 18400,
    "task_duration_p99_ms": 72864,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 22,
    "stage_name": "WindowExec",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 68000,
    "shuffle_write_bytes": 62560,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 3400,
    "task_duration_p99_ms": 3468,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 23,
    "stage_name": "Coalesce",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 48000000,
    "shuffle_write_bytes": 44160000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 2400000,
    "task_duration_p99_ms": 6480000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 24,
    "stage_name": "Union",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 1840000,
    "shuffle_write_bytes": 1692800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 92000,
    "task_duration_p99_ms": 402960,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 26,
    "stage_name": "Project",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 445000000,
    "shuffle_write_bytes": 409400000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 8900000,
    "task_duration_p99_ms": 27768000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 27,
    "stage_name": "Filter",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 32000000,
    "shuffle_write_bytes": 29440000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 640000,
    "task_duration_p99_ms": 652800,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 28,
    "stage_name": "Scan calendar",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 9200000,
    "shuffle_write_bytes": 8464000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 92000,
    "task_duration_p99_ms": 171120,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 30,
    "stage_name": "Exchange dim",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 240000000,
    "shuffle_write_bytes": 220800000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 2400000,
    "task_duration_p99_ms": 3456000,
    "ts": "2026-08-03 01:44:09"
  },
  {
    "job_id": "app-20260803014217-0071",
    "app_name": "daily_revenue_rollup",
    "stage_id": 32,
    "stage_name": "LocalTableScan",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 3680000,
    "shuffle_write_bytes": 3385600,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 900,
    "task_duration_p50_ms": 18400,
    "task_duration_p99_ms": 72864,
    "ts": "2026-08-03 01:44:09"
  }
],
  "app-20260802231455-0069": [
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 1,
    "stage_name": "Scan orders",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 84934656000,
    "shuffle_write_bytes": 78139883520,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 424673280,
    "task_duration_p99_ms": 441660211,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 4,
    "stage_name": "Scan customers",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 29375,
    "shuffle_write_bytes": 27025,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 588,
    "task_duration_p99_ms": 3143,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 6,
    "stage_name": "Exchange orders",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 20923,
    "shuffle_write_bytes": 19249,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 418,
    "task_duration_p99_ms": 4591,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 11,
    "stage_name": "Exchange custs",
    "stage_attempt": 1,
    "task_count": 2,
    "shuffle_read_bytes": 8707536,
    "shuffle_write_bytes": 8010933,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 4353768,
    "task_duration_p99_ms": 31303592,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 22,
    "stage_name": "SortMergeJoin",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 26686423000,
    "shuffle_write_bytes": 24551509160,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 17179869184,
    "gc_time_ms": 10000,
    "task_duration_p50_ms": 133432115,
    "task_duration_p99_ms": 189473603,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 26,
    "stage_name": "AQEShuffleRead",
    "stage_attempt": 1,
    "task_count": 114,
    "shuffle_read_bytes": 102268807,
    "shuffle_write_bytes": 94087303,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 897095,
    "task_duration_p99_ms": 9401554,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 28,
    "stage_name": "HashAggregate",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 2129471488,
    "shuffle_write_bytes": 1959113769,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 10647357,
    "task_duration_p99_ms": 13948038,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 30,
    "stage_name": "Exchange rollup",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 670026,
    "shuffle_write_bytes": 616424,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 6700,
    "task_duration_p99_ms": 51458,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 31,
    "stage_name": "Write delta",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 2059007598,
    "shuffle_write_bytes": 1894286990,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 20590076,
    "task_duration_p99_ms": 22443183,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 2,
    "stage_name": "Project",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 1950400,
    "shuffle_write_bytes": 1794368,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 97520,
    "task_duration_p99_ms": 427138,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 3,
    "stage_name": "Filter",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 828000,
    "shuffle_write_bytes": 761760,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 16560,
    "task_duration_p99_ms": 23846,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 5,
    "stage_name": "Scan calendar",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 30080000,
    "shuffle_write_bytes": 27673600,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 601600,
    "task_duration_p99_ms": 613632,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 7,
    "stage_name": "Exchange dim",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 333200,
    "shuffle_write_bytes": 306544,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 3332,
    "task_duration_p99_ms": 11795,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 8,
    "stage_name": "LocalTableScan",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 244800000,
    "shuffle_write_bytes": 225216000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 2448000,
    "task_duration_p99_ms": 3525120,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 9,
    "stage_name": "BroadcastExchange",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 135680000,
    "shuffle_write_bytes": 124825600,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 678400,
    "task_duration_p99_ms": 1546752,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 10,
    "stage_name": "Sort",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 3312000,
    "shuffle_write_bytes": 3047040,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 16560,
    "task_duration_p99_ms": 65578,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 12,
    "stage_name": "WindowExec",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 45120000,
    "shuffle_write_bytes": 41510400,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 2256000,
    "task_duration_p99_ms": 6091200,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 13,
    "stage_name": "Coalesce",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 1803200,
    "shuffle_write_bytes": 1658944,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 90160,
    "task_duration_p99_ms": 394901,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 14,
    "stage_name": "Union",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 938400,
    "shuffle_write_bytes": 863328,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 18768,
    "task_duration_p99_ms": 27026,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 15,
    "stage_name": "Project",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 471700000,
    "shuffle_write_bytes": 433964000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 9434000,
    "task_duration_p99_ms": 29434080,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 16,
    "stage_name": "Filter",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 28800000,
    "shuffle_write_bytes": 26496000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 576000,
    "task_duration_p99_ms": 587520,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 17,
    "stage_name": "Scan calendar",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 8648000,
    "shuffle_write_bytes": 7956160,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 86480,
    "task_duration_p99_ms": 160853,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 18,
    "stage_name": "Exchange dim",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 333200,
    "shuffle_write_bytes": 306544,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 3332,
    "task_duration_p99_ms": 11795,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 19,
    "stage_name": "LocalTableScan",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 244800000,
    "shuffle_write_bytes": 225216000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 2448000,
    "task_duration_p99_ms": 3525120,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 20,
    "stage_name": "BroadcastExchange",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 135680000,
    "shuffle_write_bytes": 124825600,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 678400,
    "task_duration_p99_ms": 1546752,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 21,
    "stage_name": "Sort",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 3312000,
    "shuffle_write_bytes": 3047040,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 16560,
    "task_duration_p99_ms": 65578,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 22,
    "stage_name": "WindowExec",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 63920,
    "shuffle_write_bytes": 58806,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 3196,
    "task_duration_p99_ms": 3260,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 23,
    "stage_name": "Coalesce",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 47040000,
    "shuffle_write_bytes": 43276800,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 2352000,
    "task_duration_p99_ms": 6350400,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 24,
    "stage_name": "Union",
    "stage_attempt": 1,
    "task_count": 20,
    "shuffle_read_bytes": 1876800,
    "shuffle_write_bytes": 1726656,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 93840,
    "task_duration_p99_ms": 411019,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 23,
    "stage_name": "Project",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 471700000,
    "shuffle_write_bytes": 433964000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 9434000,
    "task_duration_p99_ms": 29434080,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 24,
    "stage_name": "Filter",
    "stage_attempt": 1,
    "task_count": 50,
    "shuffle_read_bytes": 28800000,
    "shuffle_write_bytes": 26496000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 576000,
    "task_duration_p99_ms": 587520,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 25,
    "stage_name": "Scan calendar",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 8648000,
    "shuffle_write_bytes": 7956160,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 86480,
    "task_duration_p99_ms": 160853,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 27,
    "stage_name": "Exchange dim",
    "stage_attempt": 1,
    "task_count": 100,
    "shuffle_read_bytes": 235200000,
    "shuffle_write_bytes": 216384000,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 2352000,
    "task_duration_p99_ms": 3386880,
    "ts": "2026-08-02 23:20:41"
  },
  {
    "job_id": "app-20260802231455-0069",
    "app_name": "daily_revenue_rollup",
    "stage_id": 29,
    "stage_name": "LocalTableScan",
    "stage_attempt": 1,
    "task_count": 200,
    "shuffle_read_bytes": 3753600,
    "shuffle_write_bytes": 3453312,
    "spill_mem_bytes": 0,
    "spill_disk_bytes": 0,
    "peak_execution_mem_bytes": 4294967296,
    "gc_time_ms": 700,
    "task_duration_p50_ms": 18768,
    "task_duration_p99_ms": 74321,
    "ts": "2026-08-02 23:20:41"
  }
],
};

const SHARED_SHAPE_JOBS = new Set([CURRENT_JOB, BASELINE_JOB]);

export const stagesByJob: Record<string, SparkEventRow[]> = Object.fromEntries(
  Object.entries(recordedStages).map(([job, rows]) => [
    job,
    rows.map((r) => ({
      ...r,
      plan_fingerprint: SHARED_SHAPE_JOBS.has(job) ? PLAN_FINGERPRINT : "",
      // The recording predates the console selecting input_bytes, exactly as it
      // predates plan_fingerprint above. Zero is stated ONCE, here, as a
      // property of this recording — not defaulted per row inside bytesPerTask,
      // where it silently became a property of every live stage too.
      input_bytes: 0,
    })),
  ]),
);

export const jobConfByJob: Record<string, JobConfRow[]> = {
  "app-20260803014217-0071": [
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.sql.shuffle.partitions",
    "value": "200",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.sql.adaptive.enabled",
    "value": "true",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.sql.adaptive.skewJoin.enabled",
    "value": "true",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
    "value": "5",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.executor.memory",
    "value": "16g",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.executor.cores",
    "value": "4",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.memory.fraction",
    "value": "0.6",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260803014217-0071",
    "key": "spark.sql.autoBroadcastJoinThreshold",
    "value": "10485760",
    "ts": "2026-08-03 01:42:17"
  }
],
  "app-20260802231455-0069": [
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.sql.shuffle.partitions",
    "value": "200",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.sql.adaptive.enabled",
    "value": "true",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.sql.adaptive.skewJoin.enabled",
    "value": "true",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
    "value": "5",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.executor.memory",
    "value": "16g",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.executor.cores",
    "value": "4",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.memory.fraction",
    "value": "0.6",
    "ts": "2026-08-03 01:42:17"
  },
  {
    "job_id": "app-20260802231455-0069",
    "key": "spark.sql.autoBroadcastJoinThreshold",
    "value": "10485760",
    "ts": "2026-08-03 01:42:17"
  }
],
};

export const findingsByJob: Record<string, FindingRow[]> = {
  "app-20260803014217-0071": [
  {
    "finding_id": "f-7c41e9",
    "job_id": "app-20260803014217-0071",
    "stage_id": 25,
    "type": "SPILL",
    "severity": "critical",
    "confidence": "HIGH",
    "confidence_score": 0.94,
    "detected_by": "spill_watcher",
    "evidence": "spill_mem_bytes=51753517056 spill_disk_bytes=8160437862 peak=17179869184",
    "impact": "stage 25 wall clock 486s of 1084s total",
    "fix": "spark.sql.shuffle.partitions 200 -> 800; spark.memory.fraction 0.6 -> 0.75",
    "hot_key": "",
    "ts": "2026-08-03 01:44:09"
  },
  {
    "finding_id": "f-189e34",
    "job_id": "app-20260803014217-0071",
    "stage_id": -1,
    "type": "AQE_REPLAN",
    "severity": "critical",
    "confidence": "HIGH",
    "confidence_score": 0.97,
    "detected_by": "aqe_watcher",
    "evidence": "AQEShuffleRead skewed x1 at execution_id=11",
    "impact": "unattributable to a stage under contract v0.4",
    "fix": "keep skewJoin.enabled=true; remove the skew at source (salt the join key)",
    "hot_key": "",
    "ts": "2026-08-03 01:44:11"
  }
] as FindingRow[],
  "app-20260802231455-0069": [
  {
    "finding_id": "f-4b02aa",
    "job_id": "app-20260802231455-0069",
    "stage_id": 9,
    "type": "DUPLICATE_SCAN",
    "severity": "warning",
    // MEDIUM, not BEST_EFFORT: findings.confidence is Enum8('LOW','MEDIUM',
    // 'HIGH') and 0.81 falls in the engine's MEDIUM band (< 0.85). BEST_EFFORT
    // belongs to plan_transitions and only the `as FindingRow[]` cast below
    // ever let it through.
    "confidence": "MEDIUM",
    "confidence_score": 0.81,
    "detected_by": "scan_watcher",
    "evidence": "orders scanned twice in one execution",
    "impact": "unquantified",
    "fix": "cache the intermediate relation",
    "hot_key": "",
    "ts": "2026-08-02 23:26:02"
  }
] as FindingRow[],
};

export const transitionsByJob: Record<string, PlanTransitionRow[]> = {
  "app-20260803014217-0071": [
  {
    "job_id": "app-20260803014217-0071",
    "execution_id": 11,
    "transition_type": "skew_split",
    "detail": "AQEShuffleRead skewed x1",
    "before": "0 skewed",
    "after": "1 skewed",
    "confidence": "HIGH",
    "plan_fingerprint": "2de5e5760399189a81ab5500a216db0bae5c67f72cf42c08bd9f62689b404cf0",
    "ts": "2026-08-03 01:43:52"
  }
] as PlanTransitionRow[],
  // Rule 5: 0069 has NO skew_split. That licenses no claim in either direction.
  "app-20260802231455-0069": [],
};

export const fixVerifications: FixVerificationRow[] = [
  {
  "fix_id": "v-3a91c2",
  "finding_id": "f-7c41e9",
  "job_id": "app-20260803014217-0071",
  "mechanism_confirmed": true,
  "runtime_certified": false,
  "runtime_verdict": "unresolved",
  "predicted_saving_pct": 11,
  "noise_floor_pct": 17.4,
  "replay_count": 3,
  "replay_durations_ms": [
    963000,
    1068000,
    1147000
  ],
  "cluster_slots": null,
  "requires_human_approval": true,
  "applied": false,
  "proposed_diff": "@@ conf/spark-defaults.conf @@\n- spark.sql.shuffle.partitions            200\n+ spark.sql.shuffle.partitions            800\n+ spark.memory.fraction                   0.75\n  spark.sql.adaptive.enabled              true\n  spark.sql.adaptive.skewJoin.enabled     true"
} as FixVerificationRow,
];

/** Redacted in-JVM before egress: every column is none#N. */
export const REDACTED_PLAN = [
  "'Aggregate [sum(none#1L) AS #0L, sum(none#0) AS #1]",
  "+- 'Join Inner, (none#2L = cast(none#0 as bigint))",
  "   :- Filter isnotnull(none#1)",
  "   :  +- AQEShuffleRead skewed x1",
  "   :     +- Relation [none#0L,none#1,none#2] parquet",
  "   +- Filter isnotnull(none#0L)",
  "      +- Relation [none#0L,none#1] parquet",
];

export interface MemoryFix {
  change: string;
  confirmed: number;
  attempts: number;
  distinctConfigs: number;
  note: string;
}

export const memoryFixes: MemoryFix[] = [
  { change: "shuffle.partitions 200 -> 800", confirmed: 2, attempts: 2, distinctConfigs: 2,
    note: "Spill went to zero both times. Runtime effect uncertified both times." },
  { change: "skewedPartitionFactor 5 -> 2", confirmed: 0, attempts: 3, distinctConfigs: 2,
    note: "No mechanism confirmed on any attempt. Do not repeat this." },
  { change: "executor.memory 8g -> 16g", confirmed: 1, attempts: 2, distinctConfigs: 2,
    note: "Directionally right, magnitude uncertain — one environment only." },
  { change: "autoBroadcastJoinThreshold 10m", confirmed: 0, attempts: 3, distinctConfigs: 1,
    note: "Three attempts, one config after canonicalisation — rule 3 refuses to credit it." },
];

/** Wall clock per run on this fingerprint, for the Memory timeline. */
export const memoryTimeline = [
  { job: "0044", ms: 191000, carries: "finding" as const },
  { job: "0051", ms: 604000, carries: "none" as const },
  { job: "0058", ms: 941000, carries: "finding" as const },
  { job: "0063", ms: 1121000, carries: "finding" as const },
  { job: "0067", ms: 640000, carries: "none" as const },
  { job: "0069", ms: 712000, carries: "warning" as const },
  { job: "0071", ms: 1084000, carries: "finding" as const },
];

/**
 * The recorded shape, in the form plan_memory and run_outcomes would return it.
 *
 * Derived from memoryTimeline rather than written twice, so the fixture cannot
 * drift from the chart it already draws. The conf_* fields are null and
 * config_source is 'unknown' for the same reason they are in `runs`: this
 * recording predates job_conf, and claiming a cluster width for it would be
 * inventing an observation — which is exactly what rule 3 exists to refuse.
 */
export const planShapes: PlanShape[] = [
  {
    plan_fingerprint: PLAN_FINGERPRINT,
    run_count: memoryTimeline.length,
    first_run: "2026-07-29 18:02:35",
    last_run: "2026-08-03 01:42:17",
    node_count: 9, join_count: 1, agg_count: 2,
    exchange_count: 3, scan_count: 2, max_depth: 5, has_udf: 0,
  },
];

export const shapeRuns: ShapeRun[] = memoryTimeline.map((t) => ({
  job_id: `app-2026080${t.job.slice(0, 1)}-${t.job}`,
  app_name: "daily_revenue_rollup",
  task_time_ms: t.ms,
  finding_count: t.carries === "none" ? 0 : 1,
  severity_rank: t.carries === "finding" ? 3 : t.carries === "warning" ? 2 : 0,
  config_source: "unknown",
  conf_shuffle_partitions: null,
  conf_executor_instances: null,
  conf_executor_cores: null,
  conf_executor_memory_mb: null,
  observed_at: "2026-08-03 01:42:17",
}));
