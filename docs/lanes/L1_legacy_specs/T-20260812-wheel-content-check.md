---
id: T-20260812-wheel-content-check
task: T1.14
lane: serve
leg: L1
effort: S
touches_paths: [serve/pyproject.toml, serve/tests/test_packaging.py]
depends_on: [T-20260812-pypi-metadata]
human_gated: false
---

# T1.14 — Wheel content check

## 1 · Intent

**Goal.** Ship the package and nothing else.

**Context.** `[tool.hatch.build.targets.wheel]` names `packages = ["src/apex_mcp"]`, which is
right — but nothing asserts it. `serve/` also contains `tests/`, `tools/` (two live gates that
**write fixture rows to ClickHouse**) and `scripts/`. Shipping `tools/read_only_gate.py` inside
a published wheel would put a seeding script into every user's environment.

## 2 · Behavior

**B-1** GIVEN a built wheel WHEN its contents are listed THEN every entry is under `apex_mcp/`
or `apex_mcp-<version>.dist-info/`.

**B-2** GIVEN a built wheel WHEN its contents are listed THEN no path contains `tests/`,
`tools/` or `scripts/`.

**B-3** GIVEN a built wheel WHEN installed into a clean environment THEN `apex-mcp` resolves as
a console script and starts.

**B-4** GIVEN the sdist WHEN inspected THEN it contains `README.md` and `pyproject.toml` —
enough to rebuild from source.

## 3 · Contract

```bash
cd serve
rm -rf dist && uv build
uv run python -m zipfile -l dist/*.whl
uv run python - <<'PY'
import glob, zipfile
names = zipfile.ZipFile(glob.glob("dist/*.whl")[0]).namelist()
bad = [n for n in names if not (n.startswith("apex_mcp/") or ".dist-info/" in n)]
assert not bad, bad
assert not [n for n in names if any(p in n for p in ("tests/", "tools/", "scripts/"))]
print(f"{len(names)} entries, all in-package")
PY
```

**Card.** A build-config assertion if anything is wrong, plus one test that runs the check in
CI. Expect **zero** config change — this task usually only proves the current setting.

**Exit.** The script prints `… all in-package`; `test_packaging.py` green.

## 4 · Guardrails

**Anti-patterns.** Adding `tools/` to the wheel so users can run the gates — the gates seed
fixture rows, and a read-only server's package must not carry a writer. Excluding files via
`.gitignore` and assuming the build honors it; assert on the **artifact**.

**No-touch.** `[project]` metadata (T1.13's territory) and the `src/` layout itself.

## 5 · Operations

- **Q. Should the gates ship somewhere users can get them?** Not in this wheel. If it becomes a
  real need, a `serve/tools/` extra or a separate `apex-mcp-gates` distribution — decide in L2,
  not here.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Test-and-config only.

**Observability.** The test runs in the standard suite, so a later build-config change that
widens the wheel fails immediately rather than at publish time.

signed_off: sha256:05ad46e6e3b6d2464e6c152ef30e96de
