-- Apex infra · canonical skew-detection SQL. Two views of the same signal (p99/p50 ratio):
--   (A) from raw spark_events  — exact, per stage/attempt.
--   (B) from the spark_jobs_1m rollup sketch — cheap, per (minute, job), what HyperDX tiles use.
-- Both guard the divide with nullIf(..., 0) so a stage with p50=0 can't divide-by-zero.
-- These are SELECTs (safe to run at init against empty tables); scripts/verify.sh re-runs them
-- with the seeded/ingested job_id. Threshold: p99 > 5x median flags likely skew.

-- (A) Per-stage skew from raw events (last 6h). For each (job_id, stage_id) take the latest
--     attempt's p50/p99 (argMax by ts), compute the ratio, flag > 5x.
SELECT
  job_id,
  stage_id,
  max(stage_attempt)                                                              AS attempt,
  argMax(task_duration_p50_ms, ts)                                                AS p50_ms,
  argMax(task_duration_p99_ms, ts)                                                AS p99_ms,
  round(argMax(task_duration_p99_ms, ts) / nullIf(argMax(task_duration_p50_ms, ts), 0), 2) AS skew_ratio,
  sum(spill_disk_bytes)                                                           AS spill_disk_bytes
FROM apex.spark_events
WHERE ts >= now() - INTERVAL 6 HOUR
GROUP BY job_id, stage_id
HAVING skew_ratio > 5                 -- flag p99 > 5x median
ORDER BY skew_ratio DESC
LIMIT 50;

-- (B) From the rollup sketch — recompute p50/p99 of the per-stage p99 distribution per bucket.
--     quantilesMerge unfolds the stored state; q[1]=p50, q[2]=p99. Flags ratio > 4x.
SELECT
  bucket,
  job_id,
  quantilesMerge(0.5, 0.99)(quantiles__task_duration_p99_ms) AS q,
  round(q[2] / nullIf(q[1], 0), 2)                           AS p99_over_p50
FROM apex.spark_jobs_1m
WHERE bucket >= now() - INTERVAL 24 HOUR
GROUP BY bucket, job_id
HAVING p99_over_p50 > 4
ORDER BY p99_over_p50 DESC;
