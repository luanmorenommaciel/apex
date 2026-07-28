"""Stage 3 — the SAFETY GATE. Nothing reaches an executor without passing here.

Derived from OptiSpark (pypi.org/project/optispark 0.2.0), with two corrections
to the brief that the source verified:

  * OptiSpark's PRIMARY defense is an AST `ReadOnlyValidator`
    (`ast.NodeVisitor`) that raises before `exec()` — not the size check. It
    blocks `.write`, `.save()`, `.saveAsTable()`, `.insertInto()`, `.drop()`,
    `.delete()`, `.truncate()`, and `DROP/DELETE/TRUNCATE/INSERT/UPDATE/CREATE`
    tokens inside `spark.sql()` string arguments. For Apex's "never touch
    customer data" rule this matters MORE than the size gate, so it is
    implemented first and cannot be skipped.
  * The `optimizedPlan().stats().sizeInBytes()` check in OptiSpark is
    CONDITIONAL — it fires only when the generated code contains a high-risk op
    (their example: `F.explode`), with a 50 MB default budget. Apex applies it
    UNCONDITIONALLY, because our budget question ("could this OOM the bench?") is
    not conditional on the operator.

**The Long.MaxValue trap.** `stats().sizeInBytes()` falls back to
`spark.sql.defaultSizeInBytes`, which defaults to `Long.MaxValue` (8 EiB) when
Catalyst has no statistics for the relation. A naive `size > budget` therefore
blocks *everything* while looking like a working gate — and, worse, a naive
`size < budget` written to dodge that would *allow* everything. Neither is
acceptable, so `MaxValue` is treated as a distinct third state, UNKNOWN, and we
fail closed with `BLOCK_SIZE_UNKNOWN` — a verdict a human can read and act on.

Apex adds one rule OptiSpark has no need for: a **path allowlist**. Replay runs
only against the synthetic bench. Any URI literal outside the allowed prefixes is
blocked, so a generated snippet cannot be pointed at a customer table even by
accident.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

from .models import SafetyReport, SafetyVerdict

# Catalyst's "I have no statistics" sentinel: spark.sql.defaultSizeInBytes,
# whose default is Long.MaxValue.
LONG_MAX_VALUE = 9223372036854775807

# Default budget for a bench DataFrame. OptiSpark uses 50 MB; the dev bench runs
# in a 2 GB worker, so 256 MiB is the ceiling that still leaves headroom.
DEFAULT_SIZE_BUDGET_BYTES = 256 << 20

# Attribute access that begins a write. Blocked outright.
DESTRUCTIVE_ATTRS = frozenset({"write", "writeStream", "writeTo"})

# Method calls that mutate storage or catalog state.
DESTRUCTIVE_CALLS = frozenset({
    "save", "saveAsTable", "insertInto", "createTable", "createOrReplaceTable",
    "drop", "dropTable", "delete", "truncate", "overwrite", "replaceWhere",
    "mode", "toTable", "start", "vacuum", "restoreToVersion",
})

# SQL verbs that mutate. Matched as whole words inside spark.sql() literals.
DESTRUCTIVE_SQL = re.compile(
    r"\b(DROP|DELETE|TRUNCATE|INSERT|UPDATE|CREATE|ALTER|MERGE|REPLACE|GRANT|REVOKE|COPY)\b",
    re.IGNORECASE,
)

# Escape hatches out of the DataFrame API and out of the process.
FORBIDDEN_NAMES = frozenset({
    "exec", "eval", "compile", "__import__", "open", "input", "breakpoint", "globals", "locals",
})
FORBIDDEN_MODULES = frozenset({
    "os", "sys", "subprocess", "socket", "shutil", "pathlib", "importlib", "ctypes",
    "requests", "urllib", "urllib3", "http", "boto3", "pickle", "builtins",
})
# py4j bridges — generated code has no business reaching the JVM directly.
FORBIDDEN_ATTRS = frozenset({"_jvm", "_jdf", "_jsc", "_jsparkSession", "_gateway", "_sc"})

_URI_RE = re.compile(r"^(?:s3a?|s3n|gs|abfss?|wasbs?|hdfs|file|dbfs)://|^/dbfs/|^/mnt/", re.IGNORECASE)

# Only the synthetic bench. dev/common/data.py owns these two paths.
DEFAULT_ALLOWED_PATH_PREFIXES = ("s3a://warehouse/fact", "s3a://warehouse/dim")


class UnsafeCode(Exception):
    """Raised when generated code fails the read-only validator."""


@dataclass
class ReadOnlyValidator(ast.NodeVisitor):
    """Walk a full syntax tree and collect every reason the code is unsafe.

    Unlike OptiSpark's fail-on-first design this collects ALL violations before
    reporting, so a human sees the whole picture in one verdict instead of
    fixing one line and rediscovering the next.
    """

    allowed_path_prefixes: tuple[str, ...] = DEFAULT_ALLOWED_PATH_PREFIXES
    violations: list[str] = field(default_factory=list)

    def _flag(self, node: ast.AST, msg: str) -> None:
        line = getattr(node, "lineno", 0)
        self.violations.append(f"line {line}: {msg}")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in DESTRUCTIVE_ATTRS:
            self._flag(node, f"write path opened via .{node.attr}")
        if node.attr in FORBIDDEN_ATTRS:
            self._flag(node, f"py4j/JVM escape hatch .{node.attr}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr in DESTRUCTIVE_CALLS:
                self._flag(node, f"destructive call .{func.attr}()")
            if func.attr == "sql":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        hit = DESTRUCTIVE_SQL.search(arg.value)
                        if hit:
                            self._flag(node, f"mutating SQL verb {hit.group(0).upper()} in spark.sql()")
        if isinstance(func, ast.Name) and func.id in FORBIDDEN_NAMES:
            self._flag(node, f"forbidden builtin {func.id}()")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in FORBIDDEN_MODULES:
                self._flag(node, f"forbidden import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".")[0]
        if root in FORBIDDEN_MODULES:
            self._flag(node, f"forbidden import from {node.module}")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and _URI_RE.match(node.value.strip()):
            path = node.value.strip()
            if not any(path.startswith(p) for p in self.allowed_path_prefixes):
                self._flag(
                    node,
                    f"path outside the synthetic bench: {path[:60]!r} — replay may only "
                    f"read {', '.join(self.allowed_path_prefixes)}",
                )
        self.generic_visit(node)


def validate_read_only(
    code: str, allowed_path_prefixes: tuple[str, ...] = DEFAULT_ALLOWED_PATH_PREFIXES
) -> SafetyReport:
    """AST gate. Returns a report; never executes, never imports the code."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return SafetyReport(
            safe=False,
            verdict=SafetyVerdict.BLOCK_AST,
            detail=f"code does not parse: {exc.msg} at line {exc.lineno}",
        )
    validator = ReadOnlyValidator(allowed_path_prefixes=allowed_path_prefixes)
    validator.visit(tree)
    if validator.violations:
        return SafetyReport(
            safe=False,
            verdict=SafetyVerdict.BLOCK_AST,
            detail="read-only validator rejected the code — " + "; ".join(validator.violations),
        )
    return SafetyReport(safe=True, verdict=SafetyVerdict.ALLOW, detail="AST read-only gate passed")


def check_size(
    size_in_bytes: int | None, budget_bytes: int = DEFAULT_SIZE_BUDGET_BYTES
) -> SafetyReport:
    """Catalyst size gate with the Long.MaxValue trap handled explicitly.

    Three states, not two:
      * a real size within budget            -> ALLOW
      * a real size over budget              -> BLOCK_SIZE
      * MaxValue / None (statistics absent)  -> BLOCK_SIZE_UNKNOWN, fail closed
    """
    if size_in_bytes is None:
        return SafetyReport(
            safe=False,
            verdict=SafetyVerdict.BLOCK_SIZE_UNKNOWN,
            detail=(
                "optimizedPlan.stats.sizeInBytes was not obtainable. Failing closed: an "
                "unknown size is not a small size."
            ),
        )
    if size_in_bytes >= LONG_MAX_VALUE:
        return SafetyReport(
            safe=False,
            verdict=SafetyVerdict.BLOCK_SIZE_UNKNOWN,
            detail=(
                f"optimizedPlan.stats.sizeInBytes = {size_in_bytes} (Long.MaxValue, "
                f"8.0 EiB) — this is Catalyst's spark.sql.defaultSizeInBytes sentinel for "
                f"'no statistics available', NOT a real 8-exabyte estimate. Failing "
                f"closed; run ANALYZE TABLE or enable CBO to get a usable estimate."
            ),
        )
    if size_in_bytes > budget_bytes:
        return SafetyReport(
            safe=False,
            verdict=SafetyVerdict.BLOCK_SIZE,
            detail=(
                f"optimizedPlan.stats.sizeInBytes = {size_in_bytes:,} bytes exceeds the "
                f"{budget_bytes:,}-byte bench budget — OOM risk, blocked before execution."
            ),
        )
    return SafetyReport(
        safe=True,
        verdict=SafetyVerdict.ALLOW,
        detail=(
            f"optimizedPlan.stats.sizeInBytes = {size_in_bytes:,} bytes, within the "
            f"{budget_bytes:,}-byte bench budget"
        ),
    )


def catalyst_size_in_bytes(df) -> int | None:  # pragma: no cover - needs a live JVM
    """Read `optimizedPlan().stats().sizeInBytes()` off a PySpark DataFrame.

    Returns None if the py4j path is unavailable, which `check_size` treats as
    UNKNOWN and blocks. This is the only place Apex reaches through `_jdf`, and it
    is Apex's own code — generated code touching `_jdf` is rejected by the AST gate.
    """
    try:
        return int(df._jdf.queryExecution().optimizedPlan().stats().sizeInBytes())
    except Exception:  # noqa: BLE001 - any py4j/JVM failure means "unknown"
        return None


def gate(
    code: str | None = None,
    size_in_bytes: int | None = None,
    *,
    budget_bytes: int = DEFAULT_SIZE_BUDGET_BYTES,
    allowed_path_prefixes: tuple[str, ...] = DEFAULT_ALLOWED_PATH_PREFIXES,
    will_execute: bool = True,
) -> SafetyReport:
    """Full gate. AST first (cheapest, most decisive), then the size budget.

    `will_execute=False` short-circuits to NOT_APPLICABLE: a prediction-only
    verdict runs nothing, so there is nothing to gate and claiming otherwise
    would be theatre.
    """
    if not will_execute:
        return SafetyReport(
            safe=True,
            verdict=SafetyVerdict.NOT_APPLICABLE,
            detail="prediction only — no code and no query were executed anywhere",
        )
    if code is not None:
        ast_report = validate_read_only(code, allowed_path_prefixes)
        if not ast_report.safe:
            return ast_report
    size_report = check_size(size_in_bytes, budget_bytes)
    if not size_report.safe:
        return size_report
    return SafetyReport(
        safe=True,
        verdict=SafetyVerdict.ALLOW,
        detail=f"AST gate passed; {size_report.detail}",
    )
