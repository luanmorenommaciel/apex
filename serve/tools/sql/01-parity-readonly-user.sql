-- The console parity gate's read-only reference user.
--
-- The gate (tools/console_parity_gate.py) runs every console statement in
-- ch.py twice: once as raw SQL over the ClickHouse HTTP interface as THIS
-- user, with readonly = 1 and no setting of its own, and once through the
-- Apex API. The raw door is the reference the API is held to, so it must be
-- able to do exactly one thing: read the contract tables.
--
-- Moved here from front/contract/01-readonly-user.sql on 2026-10-19
-- (D-api-only): the console no longer queries ClickHouse from the browser,
-- so the user exists for the gate alone. Apply with clickhouse-client
-- --multiquery (the HTTP interface rejects multi-statement bodies).
CREATE DATABASE IF NOT EXISTS apex;

CREATE USER IF NOT EXISTS apex_ro IDENTIFIED WITH no_password
  SETTINGS readonly = 1;

GRANT SELECT ON apex.* TO apex_ro;
GRANT SHOW TABLES ON apex.* TO apex_ro;
