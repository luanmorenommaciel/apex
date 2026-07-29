#!/usr/bin/env python3
"""Apex infra · verify-ddl — DESCRIBE each contract table in the RUNNING ClickHouse and
diff it against its DDL source of truth. Fails loudly (exit 1) on any drift.

Why this exists: ClickHouse runs /docker-entrypoint-initdb.d only on FIRST boot, so on a
pre-existing volume the schema can silently lag the contract ("the DDL is applied" when it
isn't). This script is the loud check: every contract/mirror table must exist and every
column must match its source of truth by name and type.

Sources of truth (mirror, never redefine):
  contract/*.ddl.sql  — ratified + proposed contract tables
  memory/sql/030,031  — v0.3 mirrors (plan_memory, run_outcomes)
  verify/ddl/         — v0.3 mirror (fix_verifications)

Column-set and type drift are FAILURES. An order-only difference (e.g. a column added to
a live table via ALTER ... ADD COLUMN, which appends) is reported as a note, not a failure.

Usage:  make verify-ddl   (or python3 scripts/verify_ddl.py)
Stdlib only; talks to ClickHouse via `docker exec clickhouse-client` like apply_ddl.sh.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

INFRA_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = INFRA_DIR.parent

# table -> DDL source of truth (relative to repo root). Mirrored in infra/sql/.
SOURCES = {
    "apex.spark_events":      "contract/spark_events.ddl.sql",
    "apex.findings":          "contract/findings.ddl.sql",
    "apex.plan_transitions":  "contract/plan_transitions.ddl.sql",
    "apex.job_conf":          "contract/job_conf.ddl.sql",
    "apex.plan_memory":       "memory/sql/030_plan_memory.sql",
    "apex.run_outcomes":      "memory/sql/031_run_outcomes.sql",
    "apex.fix_verifications": "verify/ddl/fix_verifications.ddl.sql",
}

CONTAINER = os.environ.get("INFRA_CLICKHOUSE_CONTAINER", "apex-infra-clickhouse")


def load_creds():
    env = {}
    env_file = INFRA_DIR / ".env"
    if env_file.exists():
        for ln in env_file.read_text().splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    user = os.environ.get("CLICKHOUSE_USER", env.get("CLICKHOUSE_USER", "apex"))
    password = os.environ.get("CLICKHOUSE_PASSWORD", env.get("CLICKHOUSE_PASSWORD", "apex_local_dev"))
    return user, password


def parse_ddl(path):
    """Return (table_name, [(column, normalized_type), ...]) from a CREATE TABLE file."""
    # Strip `--` comments FIRST, line-wise: comments carry apostrophes ("Spark's OWN")
    # and parens that would break the quote/paren tracking below. (No source DDL has
    # a `--` inside a string literal.)
    text = "\n".join(re.sub(r"--.*$", "", ln) for ln in path.read_text().splitlines())
    m = re.search(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.]+)\s*\(", text, re.IGNORECASE)
    if not m:
        raise ValueError(f"no CREATE TABLE found in {path}")
    table = m.group(1)
    # Extract the balanced top-level (...) column block.
    depth, in_str, start = 0, False, None
    block = None
    for j in range(m.end() - 1, len(text)):
        c = text[j]
        if in_str:
            if c == "'":
                in_str = False
            continue
        if c == "'":
            in_str = True
        elif c == "(":
            depth += 1
            if depth == 1:
                start = j + 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                block = text[start:j]
                break
    if block is None:
        raise ValueError(f"unbalanced parens in {path}")
    # Split the block at top-level commas (commas inside Map(...)/Enum8(...) don't split).
    parts, depth, in_str, cur = [], 0, False, []
    for c in block:
        if in_str:
            cur.append(c)
            if c == "'":
                in_str = False
            continue
        if c == "'":
            in_str = True
            cur.append(c)
        elif c == "(":
            depth += 1
            cur.append(c)
        elif c == ")":
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        parts.append("".join(cur))
    cols = []
    for p in parts:
        # Drop -- comments line-wise, then rejoin (a column def may span lines).
        s = " ".join(re.sub(r"--.*$", "", ln).strip() for ln in p.splitlines()).strip()
        if not s:
            continue
        m2 = re.match(r"([A-Za-z_]\w*)\s+(.*)$", s)
        if not m2:
            continue  # not a column def (constraint/index line) — none today, but skip safely
        name, spec = m2.group(1), m2.group(2)
        spec = re.split(r"\s+(?:DEFAULT|MATERIALIZED|ALIAS|COMMENT|CODEC|TTL)\s+", spec)[0]
        cols.append((name, re.sub(r"\s+", "", spec)))
    return table, cols


def live_columns(table, user, password):
    r = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, "clickhouse-client",
         "--user", user, "--password", password,
         "--query", f"DESCRIBE TABLE {table}", "--format", "TSVRaw"],  # TSVRaw: no \' escaping in Enum8 types
        capture_output=True, text=True)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip().splitlines()[-1:]
    cols = []
    for ln in r.stdout.splitlines():
        if ln.strip():
            f = ln.split("\t")
            cols.append((f[0], re.sub(r"\s+", "", f[1])))
    return cols, None


def main():
    user, password = load_creds()
    st = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER],
                        capture_output=True, text=True)
    if st.stdout.strip() != "running":
        print(f"❌ {CONTAINER} is not running — 'docker compose up -d' first")
        return 1

    failures = 0
    for table, src in SOURCES.items():
        src_path = REPO_ROOT / src
        if not src_path.exists():
            print(f"❌ {table}: source of truth {src} not found")
            failures += 1
            continue
        src_table, expected = parse_ddl(src_path)
        if src_table != table:
            print(f"❌ {table}: {src} declares {src_table} — manifest out of date")
            failures += 1
            continue
        actual, err = live_columns(table, user, password)
        if actual is None:
            print(f"❌ {table}: DESCRIBE failed (table missing?) — {err}")
            failures += 1
            continue
        exp_map, act_map = dict(expected), dict(actual)
        problems = []
        for name, t in expected:
            if name not in act_map:
                problems.append(f"missing column {name} {t}")
            elif act_map[name] != t:
                problems.append(f"type drift on {name}: contract {t} vs live {act_map[name]}")
        for name, t in actual:
            if name not in exp_map:
                problems.append(f"unexpected column {name} {t} (not in {src})")
        if problems:
            failures += 1
            print(f"❌ {table} (vs {src}):")
            for p in problems:
                print(f"     - {p}")
        else:
            note = ""
            if [n for n, _ in expected] != [n for n, _ in actual]:
                note = "  (same columns, different order — ALTER-appended on a pre-existing volume)"
            print(f"✅ {table:<24} {len(expected)} columns match {src}{note}")

    if failures:
        print(f"\n❌ verify-ddl FAILED — {failures} table(s) drifted. Run 'make apply-ddl'; "
              f"if drift persists, the live table predates a type change and needs a rebuild.")
        return 1
    print(f"\n✅ verify-ddl PASSED — {len(SOURCES)} contract tables match their DDL sources exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
