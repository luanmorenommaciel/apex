#!/usr/bin/env python3
"""Apex infra · verify-ddl — compare every object in the RUNNING ClickHouse, whole, against
its DDL sources. Fails loudly (exit 1) on any drift, naming the object and the clause.

Why this exists: ClickHouse runs /docker-entrypoint-initdb.d only on FIRST boot, so on a
pre-existing volume the schema can silently lag the repo. The earlier version of this
script diffed column names and types for seven tables and nothing else; a wrong engine,
ORDER BY, TTL, setting, a stale reshape MV or a missing exporter table all passed.

How it works (no DDL parser): for each source file named in scripts/ddl_manifest.txt the
file is applied into a scratch database on the same server (apex.X rewritten to the
scratch name outside string literals), so ClickHouse itself formats both sides. Every
object is then compared clause by clause:

  live object  vs  infra copy   -> everything: columns, engine, partition, keys, TTL,
                                   settings, and an MV's full query
  infra copy   vs  lane source  -> columns, engine, partition, keys, MV query only
                                   (TTL/SETTINGS are infra's to set — README line 6)

Scratch databases carry a random suffix and are dropped on every exit path.

Usage:  make verify-ddl   (or python3 scripts/verify_ddl.py)
        python3 scripts/verify_ddl.py --list-tables     # manifest objects, one per line, offline
Stdlib only; talks to ClickHouse via `docker exec clickhouse-client` like apply_ddl.sh.
"""
from __future__ import annotations

import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

INFRA_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = INFRA_DIR.parent
MANIFEST = INFRA_DIR / "scripts" / "ddl_manifest.txt"
CONTAINER = os.environ.get("INFRA_CLICKHOUSE_CONTAINER", "apex-infra-clickhouse")

STRUCTURAL = ("columns", "engine", "partition", "primary", "order", "query")  # lane-owned
INFRA_OWNED = ("ttl", "settings")                                             # infra-owned
CLAUSES = STRUCTURAL + INFRA_OWNED


# ── manifest ─────────────────────────────────────────────────────────────────────────
def read_manifest() -> list[dict]:
    rows = []
    for ln in MANIFEST.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        obj, kind, lane, infra = ln.split()
        rows.append({"object": obj, "kind": kind, "lane": lane, "infra": infra})
    return rows


# ── credentials ──────────────────────────────────────────────────────────────────────
def load_creds():
    """CLICKHOUSE_USER/PASSWORD from the environment, infra/.env, or the secret file preflight
    renders. No default password: a missing one is reported by name, exit 2."""
    env = {}
    env_file = Path(os.environ.get("INFRA_ENV_FILE") or (INFRA_DIR / ".env"))
    if env_file.exists():
        for ln in env_file.read_text().splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    user = os.environ.get("CLICKHOUSE_USER", env.get("CLICKHOUSE_USER", "apex"))
    password = os.environ.get("CLICKHOUSE_PASSWORD") or env.get("CLICKHOUSE_PASSWORD") or ""
    if not password:
        secret = Path(os.environ.get("INFRA_SECRETS_DIR") or (INFRA_DIR / "secrets")) / "clickhouse_password"
        password = secret.read_text().strip() if secret.exists() else ""
    if not password:
        print("❌ CLICKHOUSE_PASSWORD is required (set it in infra/.env and run scripts/preflight.sh; there is no default)")
        sys.exit(2)
    return user, password


# ── server access ────────────────────────────────────────────────────────────────────
class Server:
    def __init__(self, user: str, password: str):
        self.user, self.password = user, password

    def _client(self, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["docker", "exec", "-i", CONTAINER, "clickhouse-client",
             "--user", self.user, "--password", self.password, *args],
            input=stdin, capture_output=True, text=True,
        )

    def query(self, sql: str) -> str:
        r = self._client("--query", sql, "--format", "TSVRaw")
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else "query failed")
        return r.stdout

    def multiquery(self, sql: str) -> None:
        r = self._client("--multiquery", stdin=sql)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip()[-1500:])

    def show_create(self, db: str, name: str) -> str | None:
        out = self.query(f"SELECT create_table_query FROM system.tables WHERE database = '{db}' AND name = '{name}'").strip()
        return out or None


# ── text handling ────────────────────────────────────────────────────────────────────
def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"--.*$", "", ln) for ln in text.splitlines())


def rewrite_db(text: str, scratch: str) -> str:
    """apex.<ident> -> <scratch>.<ident> outside single-quoted literals ('apex.stage' stays)."""
    out, i, in_str = [], 0, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if c == "'":
                in_str = False
            i += 1
            continue
        if c == "'":
            in_str = True
            out.append(c)
            i += 1
            continue
        m = re.match(r"apex\.(?=[A-Za-z_])", text[i:])
        if m and (i == 0 or not re.match(r"[\w.]", text[i - 1])):
            out.append(scratch + ".")
            i += len("apex.")
            continue
        out.append(c)
        i += 1
    return "".join(out)


def normalize(create: str, scratch: str | None = None) -> str:
    if scratch:
        create = create.replace(scratch + ".", "apex.").replace(f"`{scratch}`.", "apex.")
    create = re.sub(r"\s+", " ", create).strip()
    create = re.sub(r"CREATE (TABLE|MATERIALIZED VIEW) (\S+) UUID '[0-9a-f-]+'", r"CREATE \1 \2", create)
    return create


def clauses(create: str) -> dict[str, str]:
    """Split a ClickHouse-formatted CREATE into comparable clauses."""
    out = {k: "" for k in CLAUSES}
    if create.startswith("CREATE MATERIALIZED VIEW"):
        head, _, query = create.partition(" AS SELECT ")
        out["query"] = "SELECT " + query
        m = re.search(r"TO apex\.\w+( \(.*\))?$", head)
        out["columns"] = (m.group(0) if m else head)
        return out
    m = re.match(r"CREATE TABLE \S+ \((.*)\) ENGINE = (.*)$", create)
    if not m:
        out["columns"] = create
        return out
    out["columns"] = m.group(1)
    tail = "ENGINE = " + m.group(2)
    keywords = [("engine", "ENGINE = "), ("partition", "PARTITION BY "), ("primary", "PRIMARY KEY "),
                ("order", "ORDER BY "), ("ttl", "TTL "), ("settings", "SETTINGS ")]
    positions = []
    for key, kw in keywords:
        for mm in re.finditer(r"(?<![\w.])" + re.escape(kw), tail):
            positions.append((mm.start(), key, kw))
    positions.sort()
    for idx, (start, key, kw) in enumerate(positions):
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(tail)
        out[key] = tail[start + len(kw):end].strip()
    # SETTINGS is a set: ClickHouse lists a setting added by ALTER ... MODIFY SETTING after the
    # implicit index_granularity, while a CREATE lists it where the DDL put it. Same settings,
    # different order, no drift.
    if out["settings"]:
        out["settings"] = ", ".join(sorted(s.strip() for s in out["settings"].split(",")))
    return out


# ── main ─────────────────────────────────────────────────────────────────────────────
def build_side(server: Server, rows: list[dict], side: str) -> tuple[str, dict[str, str]]:
    """Apply each distinct source file of *side* into a fresh scratch db; return (db, {object: create})."""
    scratch = f"apex_verify_{side}_{secrets.token_hex(3)}"
    server.query(f"CREATE DATABASE {scratch}")
    seen: list[str] = []
    for row in rows:
        if row[side] not in seen:
            seen.append(row[side])
    for rel in seen:
        text = strip_comments((REPO_ROOT / rel).read_text())
        server.multiquery(rewrite_db(text, scratch))
    built = {}
    for row in rows:
        name = row["object"].split(".", 1)[1]
        create = server.show_create(scratch, name)
        built[row["object"]] = normalize(create, scratch) if create else ""
    return scratch, built


def main(argv: list[str]) -> int:
    rows = read_manifest()
    if "--list-tables" in argv:
        for row in rows:
            print(row["object"].split(".", 1)[1])
        return 0

    for row in rows:
        for side in ("lane", "infra"):
            if not (REPO_ROOT / row[side]).exists():
                print(f"❌ {row['object']}: {side} source {row[side]} not found")
                return 1

    user, password = load_creds()
    st = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER], capture_output=True, text=True)
    if st.stdout.strip() != "running":
        print(f"❌ {CONTAINER} is not running — 'docker compose up -d' first")
        return 1
    server = Server(user, password)

    scratches: list[str] = []
    failures = 0
    try:
        lane_db, lane = build_side(server, rows, "lane")
        scratches.append(lane_db)
        infra_db, infra = build_side(server, rows, "infra")
        scratches.append(infra_db)
        for row in rows:
            obj = row["object"]
            problems = []
            live_create = server.show_create("apex", obj.split(".", 1)[1])
            if not live_create:
                problems.append("missing on the live server")
            elif not infra[obj]:
                problems.append(f"infra copy {row['infra']} does not create it")
            else:
                live_c, infra_c, lane_c = clauses(normalize(live_create)), clauses(infra[obj]), clauses(lane[obj] or infra[obj])
                for key in CLAUSES:
                    if live_c[key] != infra_c[key]:
                        problems.append(f"{key.upper()} drift vs {row['infra']}\n         live:     {live_c[key] or '<none>'}\n         expected: {infra_c[key] or '<none>'}")
                if lane[obj]:
                    for key in STRUCTURAL:
                        if infra_c[key] != lane_c[key]:
                            problems.append(f"mirror drift: {key.upper()} in {row['infra']} differs from lane source {row['lane']}\n         infra: {infra_c[key] or '<none>'}\n         lane:  {lane_c[key] or '<none>'}")
                else:
                    problems.append(f"lane source {row['lane']} does not create it")
            if problems:
                failures += 1
                print(f"❌ {obj} ({row['kind']}):")
                for p in problems:
                    print(f"     - {p}")
            else:
                print(f"✅ {obj:<32} {row['kind']:<5} matches {row['infra']}" + ("" if row["lane"] == row["infra"] else f" (mirror of {row['lane']})"))
    except Exception as exc:  # noqa: BLE001 - report, then clean up
        print(f"❌ verify-ddl aborted: {exc}")
        failures += 1
    finally:
        for db in scratches:
            try:
                server.query(f"DROP DATABASE IF EXISTS {db}")
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️  could not drop scratch database {db}: {exc}")

    if failures:
        print(f"\n❌ verify-ddl FAILED — {failures} object(s) drifted. Run 'make apply-ddl' (or 'docker compose up', which migrates); "
              f"if drift persists the live object predates a change ADD COLUMN cannot express and needs a rebuild.")
        return 1
    print(f"\n✅ verify-ddl PASSED — {len(rows)} objects match their DDL sources clause by clause.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
