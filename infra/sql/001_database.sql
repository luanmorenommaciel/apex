-- Apex infra · ClickStack database bootstrap (runs first on ClickHouse init).
-- infra OWNS the ClickHouse application; the contract/ dir OWNS the schema.
-- 002/003/011/013 are the frozen contract tables applied verbatim; 004 the infra-only rollup;
-- 010/012 the exporter landing tables and 020/021 the reshape MVs (mirrors of collect/ddl/);
-- 030-032 the memory/verify mirrors; 033-042 converge pre-existing volumes; 050 the skew SQL.
-- scripts/ddl_manifest.txt lists every object and where its truth lives.
CREATE DATABASE IF NOT EXISTS apex;
