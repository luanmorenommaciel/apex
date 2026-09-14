-- Applied by hand to infra's ClickHouse: `make ch-user`.
--
-- This is no longer an initdb script. The console's own compose used to boot a
-- ClickHouse seeded from this directory, which gave a live database holding
-- exactly one user and no contract tables. The store is infra's now, and this
-- file only adds the credential the browser is allowed to carry.
--
-- The console queries ClickHouse from the BROWSER, so this credential ships to
-- every visitor. It must therefore be able to do exactly one thing: read the
-- seven contract tables.
CREATE DATABASE IF NOT EXISTS apex;

CREATE USER IF NOT EXISTS apex_ro IDENTIFIED WITH no_password
  SETTINGS readonly = 1;

GRANT SELECT ON apex.* TO apex_ro;
GRANT SHOW TABLES ON apex.* TO apex_ro;
