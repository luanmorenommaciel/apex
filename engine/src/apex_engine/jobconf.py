"""`apex.job_conf` (contract v0.4) as the engine reads it.

Two jobs, both required by CONTRACT.md's cross-lane rules:

  1. **cluster width for rule 1** — `spark.executor.instances * spark.executor.cores`.
     ⚠️ Those two keys are present **iff explicitly set**: contract v0.4 states
     resource keys are *never synthesized*, because "a fabricated default poisons
     'the config that worked'". In a standalone cluster they are usually absent —
     verified on this store, where `spark.executor.instances` appears in **0 of 51**
     `job_conf` rows. So the normal outcome here is UNKNOWN, and unknown must stay
     unknown: `spark.sql.shuffle.partitions` is a partition count and is never a
     substitute, and neither is `task_count`.

  2. **the NO-OP check** — was the fix engine is about to recommend already in
     force on the observed run? Apex's headline false positive recommended
     `spark.sql.adaptive.skewJoin.enabled=true` on a run where it was already
     `true` (it is `true` in **51 of 51** rows in this store). verify/ owns the
     full gate; engine's duty is not to emit the recommendation in the first place.

`conf` values are the strings Spark reported (`"true"`, `"16m"`, `"268435456b"`,
`"5.0"`), so equality needs normalization — `"16m"` and `"16777216b"` are the same
value, and `"5"` and `"5.0"` are the same number.

Pure: this module parses and interprets, it never queries. The read lives in
`clickhouse.EngineStore.job_conf`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from .physics import ClusterWidth

# The only two keys a cluster width may be derived from. Both must be present.
SLOT_KEYS = ("spark.executor.instances", "spark.executor.cores")

# Keys whose already-active state engine checks before recommending them.
AQE_ENABLED = "spark.sql.adaptive.enabled"
SKEW_JOIN_ENABLED = "spark.sql.adaptive.skewJoin.enabled"
COALESCE_ENABLED = "spark.sql.adaptive.coalescePartitions.enabled"
SHUFFLE_PARTITIONS = "spark.sql.shuffle.partitions"

_BYTE_UNITS = {"b": 1, "k": 1 << 10, "kb": 1 << 10, "m": 1 << 20, "mb": 1 << 20,
               "g": 1 << 30, "gb": 1 << 30, "t": 1 << 40, "tb": 1 << 40,
               "p": 1 << 50, "pb": 1 << 50}
_SIZE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*([kmgtp]?b|[kmgtp])$")
_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")


def normalize_value(value: str | None) -> str:
    """Canonical form of a Spark conf value, so equality means equality.

    Booleans casefold; byte sizes expand to a byte count; integral floats lose
    their `.0`. Anything unrecognized is returned casefolded and stripped —
    never coerced into a number it is not.
    """
    if value is None:
        return ""
    text = str(value).strip().casefold()
    if text in ("true", "false"):
        return text
    if match := _SIZE.match(text):
        magnitude, unit = match.groups()
        return str(int(float(magnitude) * _BYTE_UNITS[unit if unit.endswith("b") else unit]))
    if _NUMBER.match(text):
        number = float(text)
        return str(int(number)) if number.is_integer() else str(number)
    return text


def _positive_int(value: str | None) -> int | None:
    try:
        parsed = int(float(normalize_value(value)))
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


@dataclass(frozen=True)
class JobConf:
    """One `apex.job_conf` row. `present=False` is a real, reportable state."""

    job_id: str = ""
    app_id: str = ""
    app_name: str = ""
    conf: Mapping[str, str] = field(default_factory=dict)
    present: bool = False

    @classmethod
    def missing(cls, job_id: str = "") -> "JobConf":
        return cls(job_id=job_id, present=False)

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> "JobConf":
        raw = row.get("conf") or {}
        conf = {str(k): str(v) for k, v in dict(raw).items()}
        return cls(
            job_id=str(row.get("job_id", "")),
            app_id=str(row.get("app_id", "")),
            app_name=str(row.get("app_name", "")),
            conf=conf,
            present=True,
        )

    def get(self, key: str) -> str | None:
        value = self.conf.get(key)
        return value if value not in (None, "") else None

    # --- rule 1 input ------------------------------------------------------

    def cluster_width(self) -> ClusterWidth:
        """instances x cores, or an explicit UNKNOWN naming what was missing."""
        if not self.present:
            return ClusterWidth(
                slots=None, source="unknown",
                detail="no apex.job_conf row for this job (contract v0.4 table empty or absent)",
            )
        instances = _positive_int(self.get(SLOT_KEYS[0]))
        cores = _positive_int(self.get(SLOT_KEYS[1]))
        if instances and cores:
            return ClusterWidth(
                slots=instances * cores,
                source="job_conf",
                detail=f"{SLOT_KEYS[0]}={instances} x {SLOT_KEYS[1]}={cores}",
            )
        absent = [key for key, value in zip(SLOT_KEYS, (instances, cores)) if not value]
        return ClusterWidth(
            slots=None,
            source="unknown",
            detail=(
                f"apex.job_conf carries {len(self.conf)} allowlisted keys but not "
                f"{' and '.join(absent)} — contract v0.4 emits resource keys only when "
                f"explicitly set and never synthesizes a default"
            ),
        )

    # --- the NO-OP check ---------------------------------------------------

    def already_active(self, key: str, value: str) -> bool | None:
        """Is `key` already `value` on the observed run? None = cannot tell.

        None when there is no `job_conf` row or the key is absent from it. An
        absent key is NOT "not set to this value": contract v0.4 omits a key that
        was set nowhere, so silence is the only honest answer.
        """
        if not self.present:
            return None
        observed = self.get(key)
        if observed is None:
            return None
        return normalize_value(observed) == normalize_value(value)

    def active_summary(self, keys: tuple[str, ...]) -> str:
        """`key=value` for the keys actually present, for evidence text."""
        parts = [f"{k}={self.get(k)}" for k in keys if self.get(k) is not None]
        return ", ".join(parts)

    def signature_map(self) -> dict[str, str]:
        """Normalized conf, for counting DISTINCT configurations (rule 3)."""
        return {k: normalize_value(v) for k, v in sorted(self.conf.items())}


def operator_width(slots: int | None, source: str = "operator") -> ClusterWidth:
    """Wrap an explicitly supplied width.

    An operator-supplied width is an OBSERVATION (this lab's true width comes
    from the Spark master's `/json/` ALIVE-worker cores, which is where dev's
    calibration gets `slots=8`), not a guess — but it is not read from the run's
    own telemetry either, so it is labelled distinctly and travels into evidence.
    """
    if slots is None or slots <= 0:
        return ClusterWidth()
    return ClusterWidth(slots=int(slots), source=source, detail=f"{source}-supplied width")
