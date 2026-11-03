-- Apex infra · canonical skew-detection SQL. Two views of the same signal (p99/p50 ratio):
--   (A) from raw spark_events  — exact, per stage/attempt, with the contract's closed-form verdict.
--   (B) from the spark_jobs_1m rollup sketch — cheap, per (minute, job), what HyperDX tiles use.
-- Both guard the divide with nullIf(..., 0) so a stage with p50=0 can't divide-by-zero.
-- These are SELECTs (safe to run at init against empty tables); scripts/verify.sh and
-- tests/e2e/run.sh extract (A) and run it against the seeded/ingested job_id.
-- Numbered 050 so it runs AFTER every DDL at initdb: (A) joins apex.job_conf (013), and a
-- file that sorted before it (the old 005) aborted a fresh initdb once the join existed.
--
-- CONTRACT.md rule 1: a fixed 5x/10x threshold is WRONG. A stage is tail-bound iff
--     p99/p50 > (n_tasks - 1) / (slots - 1)
-- and the ratio uses the retry-safe successful-task population whenever a successful
-- sample exists (successful_task_sample_count > 0), falling back to the legacy all-attempt
-- columns for historical rows. `slots` is the cluster width: instances x cores from
-- apex.job_conf (the same keys engine reads) or an operator-supplied width; it is NEVER
-- guessed. Unknown width => tail_bound is NULL and min_slots_for_tail_bound says what
-- width the observed ratio would need. Stages with n_tasks <= slots run in a single wave
-- and are excluded from the verdict (rule 1 corollary), never passed.
--
-- Operator width: the line `WITH NULL AS operator_slots` is a MARKER. verify.sh and run.sh
-- rewrite it from APEX_CLUSTER_SLOTS (the dev lab is 8 worker cores, dev/README.md); the
-- file itself must stay valid without it because it runs at initdb.

-- (A) Per-stage skew from raw events (last 6h). For each (job_id, stage_id) take the latest
--     attempt's p50/p99 (argMax by ts), compute the ratio, and judge it against the closed form.
WITH NULL AS operator_slots
SELECT
  job_id,
  stage_id,
  max(stage_attempt)                                                                           AS attempt,
  argMax(if(successful_task_sample_count > 0, 'successful', 'all_attempts'), ts)                AS population,
  argMax(if(successful_task_sample_count > 0, successful_task_sample_count, task_count), ts)    AS n_tasks,
  argMax(if(successful_task_sample_count > 0, successful_task_duration_p50_ms, task_duration_p50_ms), ts) AS p50_ms,
  argMax(if(successful_task_sample_count > 0, successful_task_duration_p99_ms, task_duration_p99_ms), ts) AS p99_ms,
  round(p99_ms / nullIf(p50_ms, 0), 2)                                                         AS skew_ratio,
  sum(spill_disk_bytes)                                                                        AS spill_disk_bytes,
  coalesce(nullIf(any(conf_slots), 0), operator_slots)                                         AS slots,
  n_tasks <= slots                                                                             AS single_wave,
  if(slots > 1 AND n_tasks > slots, round((n_tasks - 1) / (slots - 1), 2), NULL)               AS tail_bound_threshold,
  if(tail_bound_threshold IS NULL, NULL, skew_ratio > tail_bound_threshold)                    AS tail_bound,
  if(skew_ratio > 0 AND n_tasks >= 2, round(1 + (n_tasks - 1) / skew_ratio, 2), NULL)          AS min_slots_for_tail_bound
FROM apex.spark_events
LEFT JOIN (
  SELECT job_id,
         toUInt32OrZero(conf['spark.executor.instances']) * toUInt32OrZero(conf['spark.executor.cores']) AS conf_slots
  FROM apex.job_conf
) AS c USING (job_id)
WHERE ts >= now() - INTERVAL 6 HOUR
GROUP BY job_id, stage_id
HAVING p50_ms > 0
ORDER BY tail_bound DESC NULLS LAST, skew_ratio DESC;

-- (B) From the rollup sketch — p50/p99 of the per-stage p99 distribution per bucket, from the
--     successful-sample sketch when the bucket carries one, else the legacy sketch.
--     quantiles*Merge unfolds the stored state; q[1]=p50, q[2]=p99. The closed form is a
--     per-stage statement, so (B) ranks buckets by ratio and leaves the verdict to (A).
SELECT
  bucket,
  job_id,
  sum(sum__successful_task_sample_count)                                                       AS successful_samples,
  if(successful_samples > 0, 'successful', 'all_attempts')                                     AS population,
  if(successful_samples > 0,
     quantilesIfMerge(0.5, 0.99)(quantilesIf__successful_task_duration_p99_ms),
     quantilesMerge(0.5, 0.99)(quantiles__task_duration_p99_ms))                               AS q,
  round(q[2] / nullIf(q[1], 0), 2)                                                             AS p99_over_p50
FROM apex.spark_jobs_1m
WHERE bucket >= now() - INTERVAL 24 HOUR
GROUP BY bucket, job_id
HAVING q[1] > 0
ORDER BY p99_over_p50 DESC;
