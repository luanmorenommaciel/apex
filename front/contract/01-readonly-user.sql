-- Applied by hand to infra's ClickHouse: `make ch-user`.
--
-- This is no longer an initdb script. The console's own compose used to boot a
-- ClickHouse seeded from this directory, which gave a live database holding
-- exactly one user and no contract tables. The store is infra's now, and this
-- file only adds the credential the browser is allowed to carry.
--
-- The console queries ClickHouse from the BROWSER, so this credential ships to
-- every visitor. It must therefore be able to do exactly one thing: read the
-- seven tables the console queries (front/src/data/queries.ts) — and nothing
-- else. Grants are per table on purpose: a grant on apex.* would hand the browser
-- the raw OTLP landing tables (otel_traces, otel_logs) and every table added
-- later, by default. tests/infra/test_console_ro_scope.py proves the list
-- covers queries.ts and that otel_traces is refused.
--
-- no_password stays: the credential is in the bundle by design, so a password
-- would protect nothing; what keeps this user off the network is infra binding
-- its ports to loopback (infra/docker-compose.yml).
CREATE DATABASE IF NOT EXISTS apex;

CREATE USER IF NOT EXISTS apex_ro IDENTIFIED WITH no_password
  SETTINGS readonly = 1;

-- Re-running must converge: drop whatever an earlier version granted (apex.*).
REVOKE ALL ON apex.* FROM apex_ro;

GRANT SELECT ON apex.spark_events      TO apex_ro;
GRANT SELECT ON apex.findings          TO apex_ro;
GRANT SELECT ON apex.plan_transitions  TO apex_ro;
GRANT SELECT ON apex.job_conf          TO apex_ro;
GRANT SELECT ON apex.plan_memory       TO apex_ro;
GRANT SELECT ON apex.run_outcomes      TO apex_ro;
GRANT SELECT ON apex.fix_verifications TO apex_ro;
GRANT SHOW TABLES ON apex.* TO apex_ro;
