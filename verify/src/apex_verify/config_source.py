"""Where the observed run's effective SparkConf comes from.

Contract v0.4 (`apex.job_conf`, ratified) made ClickHouse the PRIMARY source:
"was `skewJoin.enabled` true on this run?" is answerable from `apex.job_conf`
alone, so the no-op gate now works on any platform that ships Apex telemetry —
not just deployments with a Spark History Server (dev / EMR / on-prem). The
History Server REST API is kept as a FALLBACK for runs that predate conf
capture or ran with `spark.apex.conf.enabled=false`.

The source is pluggable and every fetch resolves to one of three states
(`ConfigKnowledge`):

  * KNOWN       — a conf was retrieved; the no-op gate may deduce from it.
  * UNKNOWN     — the source was reachable but holds nothing for this run.
                  Confidence is capped (MEDIUM) with the caveat "cannot rule
                  out that this fix is already active".
  * UNAVAILABLE — the source itself cannot be reached at all. Same cap.

SLOTS CAVEAT (contract v0.4, explicit): resource keys (`spark.executor.*`,
`spark.driver.*`) land in `apex.job_conf` ONLY if they were explicitly set —
the jar never synthesises a default, because a fabricated default poisons "the
config that worked". So `slots_from_conf` returns None whenever it cannot
multiply two real, captured numbers, and callers cap confidence per contract
rule 1 rather than guess a cluster width.

SECURITY: the History Server's `/environment` endpoint returns the WHOLE
SparkConf — which can carry `spark.hadoop.fs.s3a.secret.key`, JDBC passwords,
tokens (dev's own spark-defaults.conf carries MinIO credentials). Anything
read from it is filtered to the perf-key allowlist before it goes anywhere;
the whole conf is never held, logged, or persisted.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from .guardrails import SPARK_DEFAULTS
from .models import ConfigKnowledge

# The keys this lane is ever allowed to reason about: the v0.4 job_conf
# allowlist (ZEST six + AQE flags + broadcast threshold) plus the Spark
# defaults the no-op gate compares against. Anything else the History Server
# hands us is dropped unread.
JOB_CONF_ALLOWLIST = frozenset({
    "spark.sql.shuffle.partitions",
    "spark.executor.instances",
    "spark.executor.cores",
    "spark.executor.memory",
    "spark.driver.cores",
    "spark.driver.memory",
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    "spark.sql.autoBroadcastJoinThreshold",
})
SAFE_KEYS = JOB_CONF_ALLOWLIST | frozenset(SPARK_DEFAULTS)

# Resource keys that determine cluster width. Present iff explicitly set.
_SLOTS_KEYS = ("spark.executor.instances", "spark.executor.cores")

# Same shape as memory/clickhouse.py: latest row wins, server-side parameter
# binding, and "no row" means "not captured" — never "defaults".
_JOB_CONF_SQL = """
SELECT conf
FROM apex.job_conf
WHERE job_id = {job_id:String}
ORDER BY ts DESC
LIMIT 1
"""


@dataclass(frozen=True)
class ConfigResult:
    """The outcome of asking one source (or a chain) for a run's conf."""

    knowledge: ConfigKnowledge
    source: str                       # "clickhouse_job_conf" | "history_server" | "none"
    config: Mapping[str, str] | None  # allowlisted keys only; None unless KNOWN
    detail: str = ""
    slots: int | None = None          # cluster width, only if derivable without guessing
    attempts: tuple[str, ...] = field(default=())  # per-source outcomes, in order


def slots_from_conf(conf: Mapping[str, str] | None) -> int | None:
    """Cluster width = executor.instances × executor.cores, or None.

    Both keys must be present AND parse as positive integers. A missing key is
    "not explicitly set", not a default (contract v0.4 caveat) — so None here
    is an instruction to CAP CONFIDENCE, never to substitute a guess.
    """
    if not conf:
        return None
    try:
        instances = int(str(conf[_SLOTS_KEYS[0]]))  # type: ignore[index]
        cores = int(str(conf[_SLOTS_KEYS[1]]))      # type: ignore[index]
    except (KeyError, ValueError):
        return None
    if instances <= 0 or cores <= 0:
        return None
    return instances * cores


class ConfigSource(Protocol):
    """A pluggable way to learn a run's effective conf."""

    name: str

    def fetch(self, job_id: str, app_id: str = "") -> ConfigResult: ...


class ClickHouseJobConfSource:
    """PRIMARY — `apex.job_conf` (contract v0.4). Platform-independent."""

    name = "clickhouse_job_conf"

    def __init__(self, client: Any = None):
        # The client is injectable so tests and the predict path never need a
        # live driver; it is built lazily so importing this module stays free
        # of the optional clickhouse-connect dependency.
        self._client = client

    def _connect(self):
        if self._client is None:
            import clickhouse_connect  # optional dependency (`pip install .[clickhouse]`)

            self._client = clickhouse_connect.get_client(
                host=os.getenv("CLICKHOUSE_HOST", "localhost"),
                port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
                username=os.getenv("CLICKHOUSE_USER", "apex"),
                password=os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev"),
                database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
            )
        return self._client

    def fetch(self, job_id: str, app_id: str = "") -> ConfigResult:
        try:
            result = self._connect().query(_JOB_CONF_SQL, parameters={"job_id": job_id})
            rows = [dict(zip(result.column_names, row)) for row in result.result_rows]
        except Exception as exc:  # noqa: BLE001 - any driver/network failure = source down
            return ConfigResult(
                knowledge=ConfigKnowledge.UNAVAILABLE,
                source=self.name,
                config=None,
                detail=f"apex.job_conf not reachable: {type(exc).__name__}: {exc}",
            )
        if not rows or not rows[0].get("conf"):
            return ConfigResult(
                knowledge=ConfigKnowledge.UNKNOWN,
                source=self.name,
                config=None,
                detail=(
                    f"no apex.job_conf row for job_id={job_id} — the run predates "
                    "conf capture or ran with spark.apex.conf.enabled=false"
                ),
            )
        conf = {str(k): str(v) for k, v in dict(rows[0]["conf"]).items()}
        slots = slots_from_conf(conf)
        return ConfigResult(
            knowledge=ConfigKnowledge.KNOWN,
            source=self.name,
            config=conf,
            detail=(
                f"resolved allowlisted conf from apex.job_conf ({len(conf)} keys)"
                + (
                    f"; slots={slots} from explicitly-set executor keys"
                    if slots is not None
                    else "; executor.instances/cores not explicitly set — slots unknown, "
                    "confidence capped per contract rule 1"
                )
            ),
            slots=slots,
        )


class HistoryServerSource:
    """FALLBACK — Spark History Server REST `/environment`.

    Works only where a history server (or event log) exists. The response is
    filtered to SAFE_KEYS immediately: the raw payload is the whole SparkConf
    and may carry credentials.
    """

    name = "history_server"

    def __init__(self, base_url: str | None = None, timeout_s: float = 10.0):
        self._base_url = (base_url or os.getenv("APEX_HISTORY_URL", "http://localhost:18080")).rstrip("/")
        self._timeout = timeout_s

    def fetch(self, job_id: str, app_id: str = "") -> ConfigResult:
        app = app_id or job_id  # contract: job_id IS the applicationId unless overridden
        url = f"{self._base_url}/api/v1/applications/{app}/environment"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                env = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - unreachable OR app not indexed
            return ConfigResult(
                knowledge=ConfigKnowledge.UNAVAILABLE,
                source=self.name,
                config=None,
                detail=f"history server cannot answer for {app}: {type(exc).__name__}: {exc}",
            )
        pairs = env.get("sparkProperties") or []
        conf = {str(k): str(v) for k, v in pairs if str(k) in SAFE_KEYS}
        if not conf:
            return ConfigResult(
                knowledge=ConfigKnowledge.UNKNOWN,
                source=self.name,
                config=None,
                detail=f"history server indexed {app} but exposed no allowlisted keys",
            )
        return ConfigResult(
            knowledge=ConfigKnowledge.KNOWN,
            source=self.name,
            config=conf,
            detail=(
                f"effective conf from {url} filtered to {len(conf)} allowlisted keys; "
                "SQL defaults NOT resolved by this source — absent keys fall back to "
                "the gate's built-in Spark 3.5/4.x defaults"
            ),
            slots=slots_from_conf(conf),
        )


def default_sources() -> list[ConfigSource]:
    """ClickHouse first, History Server as the fallback. Order is the contract."""
    return [ClickHouseJobConfSource(), HistoryServerSource()]


def resolve_config(
    job_id: str,
    app_id: str = "",
    sources: list[ConfigSource] | None = None,
) -> ConfigResult:
    """Walk the source chain; the first KNOWN conf wins.

    Every source's outcome is recorded in `attempts` so the verdict can say
    exactly where knowledge came from — or why there is none. A KNOWN result
    with `slots=None` is still KNOWN for the no-op gate; the missing slots
    cap confidence downstream (contract rule 1).
    """
    attempts: list[str] = []
    for source in sources if sources is not None else default_sources():
        result = source.fetch(job_id, app_id)
        attempts.append(f"{result.source}: {result.knowledge.value} — {result.detail}")
        if result.knowledge is ConfigKnowledge.KNOWN:
            return ConfigResult(
                knowledge=result.knowledge,
                source=result.source,
                config=result.config,
                detail=result.detail,
                slots=result.slots,
                attempts=tuple(attempts),
            )
    return ConfigResult(
        knowledge=ConfigKnowledge.UNKNOWN,
        source="none",
        config=None,
        detail="no config source could produce this run's effective SparkConf",
        attempts=tuple(attempts),
    )
