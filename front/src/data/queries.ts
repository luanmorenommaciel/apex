/**
 * Every SQL statement the console issues, in one file.
 *
 * Two invariants, both from the contract:
 *  - Stage rows are per (stage_id, attempt); the LATEST attempt is selected with
 *    argMax(col, ts). Aggregating across attempts double-counts a retry.
 *  - Absent job_conf keys stay absent. No COALESCE to a default anywhere.
 */

export const LATEST_STAGES = `
SELECT
  se.job_id                                       AS job_id,
  any(se.app_name)                                AS app_name,
  se.stage_id                                     AS stage_id,
  -- No stage name exists in the contract. NULL, never a label invented from
  -- plan_json, which the DDL marks as a tree-string that is never parsed.
  CAST(NULL AS Nullable(String))                  AS stage_name,
  max(se.stage_attempt)                           AS stage_attempt,
  argMax(se.task_count, se.ts)                    AS task_count,
  argMax(se.shuffle_read_bytes, se.ts)            AS shuffle_read_bytes,
  argMax(se.shuffle_write_bytes, se.ts)           AS shuffle_write_bytes,
  -- The third term of rule 1's volume floor. Engine sums shuffle read + write
  -- + INPUT for bytes_touched (apex_engine/clickhouse.py, SHAPE_HISTORY_SQL);
  -- omitting it here measured every stage short and refused stages the engine
  -- had accepted, with nothing on screen to say the two disagreed.
  argMax(se.input_bytes, se.ts)                   AS input_bytes,
  argMax(se.spill_mem_bytes, se.ts)               AS spill_mem_bytes,
  argMax(se.spill_disk_bytes, se.ts)              AS spill_disk_bytes,
  argMax(se.peak_execution_mem_bytes, se.ts)      AS peak_execution_mem_bytes,
  argMax(se.gc_time_ms, se.ts)                    AS gc_time_ms,
  -- Rule 1's ratio. Duration percentiles, because the contract holds no byte
  -- distribution to build a bytes ratio from. There is no stage duration here
  -- either, and none anywhere else: the console reports it as not captured.
  argMax(se.task_duration_p50_ms, se.ts)          AS task_duration_p50_ms,
  argMax(se.task_duration_p99_ms, se.ts)          AS task_duration_p99_ms,
  -- The pairing key for /compare. A stage with no real fingerprint returns ''
  -- and is reported as unmatched rather than paired on its id, which would
  -- silently compare two different operators.
  if(match(toString(argMax(se.plan_fingerprint, se.ts)), '^[0-9a-f]{64}$')
     AND argMax(se.plan_fingerprint, se.ts) != toFixedString(repeat('0', 64), 64),
     toString(argMax(se.plan_fingerprint, se.ts)), '') AS plan_fingerprint,
  -- Qualified \`se.\`, every one: the output alias \`ts\` would otherwise shadow
  -- the source column inside each argMax and ClickHouse rejects the statement
  -- with ILLEGAL_AGGREGATION. The memory lane aliases it \`stage_ts\` for the
  -- same reason; qualifying keeps the contract's field name on the wire.
  max(se.ts)                                      AS ts
FROM spark_events AS se
WHERE se.job_id = {job:String}
GROUP BY se.job_id, se.stage_id
ORDER BY se.stage_id
`;

/**
 * The run rollup, defined ONCE, over apex.run_outcomes.
 *
 * Three properties of that table drive every line below:
 *
 *  1. GRAIN is (plan_fingerprint, job_id) — one row per plan SHAPE, not per run.
 *     A job that ran two shapes has two rows, so a per-job list must aggregate.
 *  2. ENGINE is ReplacingMergeTree(indexed_at). Re-indexing a job leaves both
 *     versions readable until a merge, so FINAL is required for a correct count.
 *  3. wall_clock_ms is NOT a job duration. The memory lane defines it as
 *     dateDiff(min(stage_ts), max(stage_ts)) WITHIN one shape, and its own DDL
 *     says so: "stages of different shapes interleave, so this is context, not
 *     the cost metric". It is 0 for a single-stage shape. It is therefore NOT
 *     read here, and summing it across shapes would be meaningless.
 *
 * task_time_ms IS summable and IS defined: sum(task_count * p50) per shape, so
 * the total over a job's shapes is that job's total task time. That is the
 * metric the memory lane computes deltas on, and the only run-level cost figure
 * the contract actually stores.
 *
 * `where` and `tail` are literals from this file — never a value from a URL.
 */
const runRollup = (where: string, tail: string) => `
WITH
-- spark_events is authoritative for WHAT RAN. Every stage is here, including the
-- ones no plan shape claims, so the run's identity and stage count come from it
-- and a run stays listed even if the memory lane has never indexed it.
base AS (
  SELECT job_id, argMax(app_name, ts) AS app_name,
         uniqExact(stage_id) AS stage_count, min(ts) AS started_at
  FROM spark_events
  ${where}
  GROUP BY job_id
),
-- findings is authoritative for WHAT WAS CLAIMED — including stage_id = -1,
-- the job-level AQE findings that belong to no stage and therefore to no shape.
f AS (
  SELECT job_id, count() AS finding_count,
         max(severity IN ('critical', 'blocker')) AS has_critical
  FROM findings GROUP BY job_id
),
-- run_outcomes is authoritative ONLY for shape-attributable outcome data. Its
-- grain is (plan_fingerprint, job_id) and its ENGINE is ReplacingMergeTree, so:
-- FINAL to drop superseded index passes, GROUP BY to fold shapes into one run.
-- Its own stage_count and finding_count are deliberately NOT read: it excludes
-- stages whose plan_fingerprint is absent and findings with no stage, so both
-- would under-report the run. wall_clock_ms is not read either — the lane's DDL
-- calls it a per-shape span and "NOT a job duration".
shapes AS (
  SELECT ro.job_id AS job_id,
         sum(ro.task_time_ms)                                  AS task_time_ms,
         -- RunSummary holds one fingerprint; report the dominant shape and send
         -- shape_count with it, so "this run is one shape" stays distinguishable
         -- from "we picked one of many".
         toString(argMax(ro.plan_fingerprint, ro.stage_count)) AS plan_fingerprint,
         uniqExact(ro.plan_fingerprint)                        AS shape_count,
         sum(ro.stage_count)                                   AS shaped_stage_count,
         -- 'observed' only when the jar emitted job_conf for this run. Otherwise
         -- every conf_* is NULL and rule 1 has no cluster width to read.
         argMax(ro.config_source, ro.observed_at)              AS config_source,
         max(ro.conf_executor_instances)                       AS conf_executor_instances,
         max(ro.conf_shuffle_partitions)                       AS conf_shuffle_partitions
  -- Columns inside aggregates are qualified with \`ro.\`: unqualified,
  -- argMax(plan_fingerprint, stage_count) resolves stage_count to the
  -- sum(stage_count) alias and ClickHouse fails with ILLEGAL_AGGREGATION.
  FROM run_outcomes AS ro FINAL
  GROUP BY ro.job_id
)
SELECT
  -- Aliased explicitly, every one. job_id exists in all three CTEs, so ClickHouse
  -- keeps it qualified as \`b.job_id\` in the result and the client reads undefined
  -- from it — a silently blank column, not an error. The others are unambiguous
  -- today and would not need it; they carry the alias so a future CTE cannot
  -- reintroduce the same bug.
  b.job_id      AS job_id,
  b.app_name    AS app_name,
  b.stage_count AS stage_count,
  b.started_at  AS started_at,
  ifNull(f.finding_count, 0) AS finding_count,
  ifNull(f.has_critical, 0)  AS has_critical,
  -- A run the memory lane has not indexed joins to nothing. -1 marks that as
  -- "not indexed", which the repository turns into null — never a zero.
  ifNull(s.task_time_ms, -1)       AS task_time_ms,
  ifNull(s.plan_fingerprint, '')   AS plan_fingerprint,
  ifNull(s.shape_count, 0)         AS shape_count,
  ifNull(s.shaped_stage_count, -1) AS shaped_stage_count,
  ifNull(s.config_source, 'unknown') AS config_source,
  s.conf_executor_instances, s.conf_shuffle_partitions
FROM base b
LEFT JOIN f      ON f.job_id = b.job_id
LEFT JOIN shapes s ON s.job_id = b.job_id
${tail}
`;

export const RUN_LIST = runRollup("", "ORDER BY b.started_at DESC LIMIT {limit:UInt32}");

export const RUN_ONE = runRollup("WHERE job_id = {job:String}", "LIMIT 1");

/**
 * job_conf holds ONE row per job with conf as a Map, while every consumer here
 * reads one row per key. arrayJoin over the map's entries does the reshape in
 * SQL, so readSlots() and readConfiguredPartitions() keep working unchanged.
 *
 * An absent key stays absent: the map simply has no entry, and no LEFT JOIN or
 * COALESCE invents one. That is what lets rule 1 declare itself vacant rather
 * than assume a cluster width.
 */
export const JOB_CONF = `
SELECT
  job_id,
  entry.1 AS key,
  entry.2 AS value,
  ts
FROM job_conf
ARRAY JOIN CAST(conf, 'Array(Tuple(String, String))') AS entry
WHERE job_id = {job:String}
ORDER BY key
`;

export const FINDINGS = `
SELECT finding_id, job_id, stage_id, type, severity, confidence,
       confidence_score, detected_by, evidence, impact, fix, hot_key, ts
FROM findings
WHERE job_id = {job:String}
ORDER BY confidence_score DESC
`;

/**
 * plan_fingerprint is NOT a column here — it lives on spark_events, so it is
 * joined in. `any()` over the job's fingerprinted stages is sound only because
 * the console uses it as the run's shape identity; a stage-accurate fingerprint
 * would need the execution -> stage map that contract v0.4 does not carry.
 *
 * update_seq exists to pick the LATEST re-plan per execution_id. Without it an
 * execution that AQE re-planned three times renders as three transitions.
 */
export const PLAN_TRANSITIONS = `
WITH fp AS (
  SELECT job_id, any(toString(plan_fingerprint)) AS plan_fingerprint
  FROM spark_events
  WHERE job_id = {job:String}
    AND match(toString(plan_fingerprint), '^[0-9a-f]{64}$')
    AND plan_fingerprint != toFixedString(repeat('0', 64), 64)
  GROUP BY job_id
)
SELECT
  t.job_id                            AS job_id,
  t.execution_id                      AS execution_id,
  argMax(t.update_seq, t.update_seq)  AS update_seq,
  argMax(t.transition_type, t.update_seq) AS transition_type,
  argMax(t.detail, t.update_seq)      AS detail,
  argMax(t.before, t.update_seq)      AS before,
  argMax(t.after, t.update_seq)       AS after,
  argMax(t.confidence, t.update_seq)  AS confidence,
  ifNull(any(fp.plan_fingerprint), '') AS plan_fingerprint,
  max(t.ts)                           AS ts
FROM plan_transitions AS t
LEFT JOIN fp ON fp.job_id = t.job_id
WHERE t.job_id = {job:String}
GROUP BY t.job_id, t.execution_id
ORDER BY t.execution_id
`;

/**
 * Candidate baselines: other runs that executed at least one of THIS run's plan
 * shapes, most recent first.
 *
 * Sharing a fingerprint is the only sound basis for comparing two runs — it is
 * what lets a delta be attributed to data or config rather than to a different
 * query. Runs that share nothing are not returned, so the screen can say "no
 * comparable run" instead of differencing two unrelated jobs.
 *
 * Reads run_outcomes, which is already keyed by (plan_fingerprint, job_id) —
 * the exact index this question needs.
 */
export const RUNS_SHARING_SHAPE = `
WITH mine AS (
  SELECT DISTINCT plan_fingerprint
  FROM run_outcomes FINAL
  WHERE job_id = {job:String}
)
SELECT
  o.job_id                       AS job_id,
  any(o.app_name)                AS app_name,
  uniqExact(o.plan_fingerprint)  AS shared_shapes,
  max(o.observed_at)             AS observed_at
FROM run_outcomes AS o FINAL
INNER JOIN mine ON mine.plan_fingerprint = o.plan_fingerprint
WHERE o.job_id != {job:String}
GROUP BY o.job_id
ORDER BY observed_at DESC
LIMIT 20
`;

export const PLAN_MEMORY = `
SELECT plan_fingerprint, any(app_name) AS app_name, count(DISTINCT job_id) AS run_count,
       min(ts) AS first_seen, max(ts) AS last_seen
FROM plan_transitions t INNER JOIN spark_events e USING (job_id)
GROUP BY plan_fingerprint
ORDER BY last_seen DESC
`;

/**
 * Three of the console's twelve fields exist as columns. The rest are renames,
 * derivations, or absent — and each is marked as which:
 *
 *  - runtime_certified / runtime_verdict are RULE 2, computed here rather than
 *    stored. A delta inside the measured floor is unresolvable, which is not
 *    the same as zero, so it becomes 'unresolved' and never a direction.
 *  - predicted_saving_pct flips the sign of predicted_delta_pct: the column is
 *    signed with negative meaning faster; a "saving" is positive when faster.
 *  - cluster_slots is instances x cores from run_outcomes, the same product the
 *    engine forms in jobconf.py. NULL when the jar never emitted the conf.
 *  - mechanism_confirmed has NO source and is returned as NULL. Deriving it
 *    from method/safety_verdict would collapse rule 4's two verdicts into one.
 */
export const FIX_VERIFICATIONS = `
WITH slots AS (
  SELECT job_id,
         max(conf_executor_instances) * max(conf_executor_cores) AS cluster_slots
  FROM run_outcomes FINAL
  GROUP BY job_id
)
SELECT
  v.verification_id AS fix_id,
  v.finding_id      AS finding_id,
  v.job_id          AS job_id,
  CAST(NULL AS Nullable(UInt8))       AS mechanism_confirmed,
  toUInt8(v.measured_delta_pct IS NOT NULL
          AND v.noise_floor_pct IS NOT NULL
          AND abs(v.measured_delta_pct) > v.noise_floor_pct) AS runtime_certified,
  multiIf(v.measured_delta_pct IS NULL
            OR v.noise_floor_pct IS NULL
            OR abs(v.measured_delta_pct) <= v.noise_floor_pct, 'unresolved',
          v.measured_delta_pct < 0, 'improved',
          'regressed')                AS runtime_verdict,
  -v.predicted_delta_pct              AS predicted_saving_pct,
  v.noise_floor_pct                   AS noise_floor_pct,
  v.replay_reps                       AS replay_count,
  s.cluster_slots                     AS cluster_slots,
  v.proposed_config                   AS proposed_diff
FROM fix_verifications AS v
LEFT JOIN slots s ON s.job_id = v.job_id
WHERE v.finding_id = {finding:String}
ORDER BY v.verified_at DESC
LIMIT 1
`;

/**
 * Every plan shape the memory lane has indexed, with how many runs executed it.
 *
 * plan_memory is a STRUCTURAL index — node counts, operator mix, an embedding —
 * not an outcome store, so the run count and the dates come from run_outcomes.
 * The INNER JOIN is deliberate: a shape with no outcome row has no history to
 * show, and a run whose shape was never indexed is not a shape we know.
 */
export const PLAN_SHAPES = `
WITH r AS (
  SELECT plan_fingerprint,
         uniqExact(job_id) AS run_count,
         min(observed_at)  AS first_run,
         max(observed_at)  AS last_run
  FROM run_outcomes FINAL
  GROUP BY plan_fingerprint
)
SELECT
  toString(pm.plan_fingerprint) AS plan_fingerprint,
  r.run_count      AS run_count,
  r.first_run      AS first_run,
  r.last_run       AS last_run,
  pm.node_count    AS node_count,
  pm.join_count    AS join_count,
  pm.agg_count     AS agg_count,
  pm.exchange_count AS exchange_count,
  pm.scan_count    AS scan_count,
  pm.max_depth     AS max_depth,
  pm.has_udf       AS has_udf
FROM plan_memory AS pm FINAL
INNER JOIN r ON r.plan_fingerprint = pm.plan_fingerprint
ORDER BY r.run_count DESC, r.last_run DESC
LIMIT 50
`;

/**
 * ONE redacted plan exemplar for a shape.
 *
 * `plan_memory.sample_plan_json` is the contract's own answer to "show me this
 * plan": its DDL calls it "ONE redacted exemplar, for citation", already
 * redacted upstream by the jar, and the table holds one row per fingerprint.
 *
 * It is read from HERE and not from spark_events.plan_json, for two reasons.
 * plan_json is per stage, so a 34-stage run would ship 34 Catalyst trees to
 * draw one; and its DDL marks it a tree-string that is never parsed, which this
 * console honours by rendering the text verbatim and reading nothing out of it.
 *
 * Empty when the memory lane has not indexed the shape — which is a fact about
 * that lane, and the screen says so rather than showing a plan from a fixture.
 */
export const PLAN_SAMPLE = `
SELECT toString(sample_plan_json) AS sample_plan_json
FROM plan_memory FINAL
WHERE plan_fingerprint = {fingerprint:String}
ORDER BY indexed_at DESC
LIMIT 1
`;

/**
 * Every run of ONE shape, oldest first — the history rule 3 reasons over.
 *
 * task_time_ms is the cost metric, not wall_clock_ms: the latter is this lane's
 * per-shape timestamp span, which its own DDL calls "context, not the cost
 * metric". The conf_* columns are NULL unless the jar emitted job_conf for that
 * run, and null travels through as "not captured" so rule 3 can refuse to
 * credit a difference rather than compare against an invented default.
 */
export const SHAPE_RUNS = `
SELECT
  job_id                                   AS job_id,
  app_name                                 AS app_name,
  task_time_ms                             AS task_time_ms,
  finding_count                            AS finding_count,
  indexOf(['info', 'warning', 'critical', 'blocker'], worst_severity) AS severity_rank,
  config_source                            AS config_source,
  conf_shuffle_partitions                  AS conf_shuffle_partitions,
  conf_executor_instances                  AS conf_executor_instances,
  conf_executor_cores                      AS conf_executor_cores,
  conf_executor_memory_mb                  AS conf_executor_memory_mb,
  observed_at                              AS observed_at
FROM run_outcomes FINAL
WHERE plan_fingerprint = {fingerprint:String}
ORDER BY observed_at
`;
