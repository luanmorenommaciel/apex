"""Disposable ClickHouse for the infra live tests.

Starts a throwaway ``clickhouse/clickhouse-server:24.8`` container with a chosen set of
``infra/sql`` files mounted as ``/docker-entrypoint-initdb.d`` on a random free loopback
port, answers queries over HTTP, applies further files with ``clickhouse-client
--multiquery`` (the same mechanism ``infra/scripts/apply_ddl.sh`` uses) and removes the
container afterwards. It never names, inspects or stops a real infra container: the
container name carries a random suffix and the port is whatever the kernel hands out.

Live tests are opt-in: ``APEX_INFRA_LIVE=1``. Without it every test using
``live_only`` skips, which keeps the lean CI python job service-free.
"""
from __future__ import annotations

import base64
import os
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

IMAGE = "clickhouse/clickhouse-server:24.8"
REPO = Path(__file__).resolve().parents[2]
SQL_DIR = REPO / "infra" / "sql"
CONTAINER_PREFIX = "apex-disposable-"
LIVE = os.environ.get("APEX_INFRA_LIVE") == "1"

live_only = pytest.mark.skipif(
    not LIVE, reason="set APEX_INFRA_LIVE=1 to run against a disposable ClickHouse"
)


def prefix(path: Path) -> int:
    """Numeric filename prefix (``034_x.sql`` -> 34)."""
    return int(path.name[:3])


def sql_files(predicate=None) -> list[Path]:
    """``infra/sql/*.sql`` in apply order, optionally filtered on the numeric prefix."""
    files = sorted(SQL_DIR.glob("*.sql"), key=lambda p: p.name)
    if predicate is None:
        return files
    return [f for f in files if predicate(prefix(f))]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def normalize_sql(text: str) -> str:
    """Strip ``--`` comments, collapse whitespace, drop a trailing semicolon."""
    import re

    text = "\n".join(re.sub(r"--.*$", "", line) for line in text.splitlines())
    return re.sub(r"\s+", " ", text).strip().rstrip(";").strip()


class DisposableClickHouse:
    """Context manager around one throwaway server."""

    def __init__(
        self,
        init_files: list[Path],
        overrides: dict[str, str] | None = None,
        config_d: Path | None = None,
        ready_timeout: float = 180.0,
    ) -> None:
        self.init_files = list(init_files)
        self.overrides = dict(overrides or {})
        self.config_d = config_d
        self.ready_timeout = ready_timeout
        self.name = CONTAINER_PREFIX + secrets.token_hex(4)
        self.user = "apex"
        self.password = secrets.token_hex(12)
        self.port = free_port()
        self._tmp: Path | None = None

    # -- lifecycle ----------------------------------------------------------
    def start(self) -> "DisposableClickHouse":
        self._tmp = Path(tempfile.mkdtemp(prefix="apex-initdb-"))
        initdb = self._tmp / "initdb"
        initdb.mkdir()
        for src in self.init_files:
            text = self.overrides.get(src.name)
            if text is None:
                shutil.copyfile(src, initdb / src.name)
            else:
                (initdb / src.name).write_text(text)
        cmd = [
            "docker", "run", "-d", "--name", self.name,
            "-p", f"127.0.0.1:{self.port}:8123",
            "-e", f"CLICKHOUSE_USER={self.user}",
            "-e", f"CLICKHOUSE_PASSWORD={self.password}",
            "-e", "CLICKHOUSE_DB=apex",
            "-e", "CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1",  # as infra/docker-compose.yml: apex may CREATE USER
            "-v", f"{initdb}:/docker-entrypoint-initdb.d:ro",
        ]
        if self.config_d is not None:
            cmd += ["-v", f"{self.config_d.resolve()}:/etc/clickhouse-server/config.d/apex:ro"]
        cmd.append(IMAGE)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        self._wait_ready()
        return self

    def _wait_ready(self) -> None:
        deadline = time.monotonic() + self.ready_timeout
        last = ""
        while time.monotonic() < deadline:
            state = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", self.name],
                capture_output=True, text=True,
            )
            if state.stdout.strip() != "true":
                logs = subprocess.run(["docker", "logs", self.name], capture_output=True, text=True)
                self.stop()  # no --rm on docker run, so the logs above are still readable
                raise RuntimeError(
                    f"{self.name} exited during initdb (bad DDL?):\n{(logs.stdout + logs.stderr)[-4000:]}"
                )
            try:
                if self.query("SELECT 1").strip() == "1":
                    return
            except Exception as exc:  # noqa: BLE001 - still booting
                last = str(exc)
            time.sleep(1.0)
        self.stop()
        raise RuntimeError(f"{self.name} did not answer within {self.ready_timeout}s: {last}")

    def stop(self) -> None:
        subprocess.run(["docker", "rm", "-f", self.name], capture_output=True, text=True)
        if self._tmp is not None:
            shutil.rmtree(self._tmp, ignore_errors=True)
            self._tmp = None

    def __enter__(self) -> "DisposableClickHouse":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()

    # -- access -------------------------------------------------------------
    def query(self, sql: str, fmt: str | None = "TSVRaw") -> str:
        """One statement over HTTP; raises with ClickHouse's message on failure."""
        if fmt and "FORMAT" not in sql.upper():
            sql = f"{sql.rstrip().rstrip(';')} FORMAT {fmt}"
        token = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/", data=sql.encode(),
            headers={"Authorization": f"Basic {token}"}, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode()
        except urllib.error.HTTPError as err:
            raise RuntimeError(err.read().decode()) from None

    def apply(self, files: list[Path], overrides: dict[str, str] | None = None) -> None:
        """Apply files in order with clickhouse-client --multiquery (what apply_ddl.sh does)."""
        overrides = dict(overrides or {})
        for path in files:
            text = overrides.get(path.name, path.read_text())
            proc = subprocess.run(
                ["docker", "exec", "-i", self.name, "clickhouse-client",
                 "--user", self.user, "--password", self.password, "--multiquery"],
                input=text, capture_output=True, text=True,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"applying {path.name} failed:\n{proc.stderr[-3000:]}")

    def create_table_query(self, name: str, database: str = "apex") -> str:
        return self.query(
            f"SELECT create_table_query FROM system.tables WHERE database = '{database}' AND name = '{name}'"
        ).strip()
