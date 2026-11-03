-- Apex infra · retention, additive (existing volumes).
--
-- Fresh volumes get these TTLs from 003/010/012/032 at initdb; a volume that predates them
-- gets the same here. MODIFY TTL rewrites the expression and (materialize_ttl_after_modify,
-- default on) schedules a mutation that drops already-expired parts — on a long-lived
-- store that is a one-off cleanup, not a steady-state cost. Re-running is a no-op.
--
--   findings, fix_verifications  365 DAY  derived knowledge outlives the raw events
--   otel_traces, otel_traces_trace_id_ts, otel_logs   14 DAY  raw landing tables; the
--                                                     reshaped contract tables keep 90
-- Decision D-8 in tasks/.plans/infra-hardening.intent.md; tests/infra/test_retention_ttl.py.

ALTER TABLE apex.findings               MODIFY TTL toDateTime(ts) + INTERVAL 365 DAY;
ALTER TABLE apex.fix_verifications      MODIFY TTL toDateTime(verified_at) + INTERVAL 365 DAY;
ALTER TABLE apex.otel_traces            MODIFY TTL toDateTime(Timestamp) + INTERVAL 14 DAY;
ALTER TABLE apex.otel_traces_trace_id_ts MODIFY TTL Start + INTERVAL 14 DAY;
ALTER TABLE apex.otel_logs              MODIFY TTL toDateTime(Timestamp) + INTERVAL 14 DAY;
