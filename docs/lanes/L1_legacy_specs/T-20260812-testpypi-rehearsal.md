---
id: T-20260812-testpypi-rehearsal
task: T1.15
lane: serve
leg: L1
effort: S
touches_paths: [serve/VALIDATION.md]
depends_on: [T-20260812-wheel-content-check]
human_gated: true
---

# T1.15 — 🔒 TestPyPI publish + install rehearsal

## 1 · Intent

**Goal.** Rehearse the publish on a registry where mistakes are free.

**Context.** A PyPI release is **immutable**: a version number, once published, can be yanked
but never replaced. The one-command install is L1's headline promise, so the first time it is
exercised should not be against the real index.

**🔒 Human-gated.** Requires a TestPyPI API token. An agent may prepare and verify everything
up to the upload.

## 2 · Behavior

**B-1** GIVEN built artifacts WHEN uploaded to TestPyPI THEN the upload succeeds and the
project page renders the README.

**B-2** GIVEN a machine with no local checkout WHEN
`uvx --index-url https://test.pypi.org/simple/ apex-mcp` runs THEN the server starts and blocks
on stdin.

**B-3** GIVEN that launch with immediate EOF WHEN it exits THEN **stdout received zero bytes**
and diagnostics appeared on stderr.

**B-4** GIVEN the installed package WHEN its dependencies resolve THEN `mcp` and
`clickhouse-connect` come from **real** PyPI, not TestPyPI — the index flag must not strand the
dependency resolution.

## 3 · Contract

```bash
cd serve && rm -rf dist && uv build
uvx twine upload --repository testpypi dist/*          # 🔒 needs TESTPYPI token

cd /tmp && uvx --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ apex-mcp </dev/null \
  >/tmp/tp-stdout.bin 2>/tmp/tp-stderr.txt
test ! -s /tmp/tp-stdout.bin && echo "stdout: 0 bytes OK"
```

**Card.** No source change. Outcome recorded in `VALIDATION.md`.

**Exit.** `stdout: 0 bytes OK`; the TestPyPI page renders; B-4 confirmed by the resolution
succeeding with the extra index.

## 4 · Guardrails

**Anti-patterns.** Reusing the version number intended for real PyPI — burn a `.devN` suffix on
TestPyPI so T1.16 gets a clean number. Testing from inside `serve/`, where a local install can
satisfy the import and produce a false pass. Omitting `--extra-index-url` and then "fixing" B-4
by vendoring a dependency.

**No-touch.** `pyproject.toml` — if metadata is wrong, fix it in T1.13 and rebuild, do not
patch it here.

## 5 · Operations

- **Q. Which version number for the rehearsal?** `0.2.0.dev1`, incrementing per attempt.
  TestPyPI is also immutable per version. *(resolved)*
- **Q. Who holds the token?** Record the owner here when this runs — it is also the answer for
  T1.16.

## 6 · Reversal

**Rollback.** Yank the TestPyPI release. Nothing in the repo changes, so there is nothing to
revert in git.

**Observability.** A clean-machine install is the only check that catches a missing dependency
or a broken console script; `uv run` inside the project masks both.

signed_off: sha256:7c05a998a54b680393c224ae6f936914
