-- Apex infra · ClickStack database bootstrap (runs first on ClickHouse init).
-- infra OWNS the ClickHouse application; the contract/ dir OWNS the schema.
-- Files 002/003/011 are the frozen contract tables applied verbatim; 004/020 add
-- infra-only rollups and the reshape MVs (whose logic mirrors collect/ddl/30_,31_).
CREATE DATABASE IF NOT EXISTS apex;
