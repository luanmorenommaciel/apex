-- Additive migration for pre-v0.2 ClickHouse volumes.
-- Safe to run repeatedly. Never rename or repurpose a contract column.
ALTER TABLE apex.findings
    ADD COLUMN IF NOT EXISTS app_id String DEFAULT '' AFTER job_id;

ALTER TABLE apex.findings
    ADD COLUMN IF NOT EXISTS confidence_score Float32 DEFAULT 0 AFTER confidence;
