---
id: T-20260812-pypi-metadata
task: T1.13
lane: serve
leg: L1
effort: S
touches_paths: [serve/pyproject.toml]
depends_on: []
human_gated: false
---

# T1.13 — PyPI metadata

## 1 · Intent

**Goal.** Make the package publishable.

**Context.** `pyproject.toml` carries `name`, `version`, `description`, dependencies and
`[project.scripts]` — enough to build a wheel, not enough to publish one. Until it is
published, every install path needs `uvx --from <path>`, which is the difference between a
one-command install and a paragraph of instructions.

## 2 · Behavior

**B-1** GIVEN the project WHEN built THEN the wheel metadata carries `readme`, `license`,
`authors`, `keywords`, `classifiers` and `[project.urls]` (Homepage, Repository, Issues).

**B-2** GIVEN the built artifacts WHEN `twine check` runs THEN every one reports `PASSED`.

**B-3** GIVEN the rendered long description WHEN inspected THEN it is `serve/README.md` and its
relative links are understood to be repo-relative — PyPI does not resolve them.

**B-4** GIVEN the dependency pins WHEN read THEN `mcp[cli]>=1.27,<2` is **unchanged** — the
`<2` bound is a researched decision, not an incidental pin.

## 3 · Contract

```bash
cd serve
uv build
uvx twine check dist/*
uv run python -c "
import tomllib, pathlib
p = tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']
need = {'readme','license','authors','keywords','classifiers','urls'}
missing = need - p.keys()
assert not missing, missing
assert p['dependencies'][0].startswith('mcp[cli]>=1.27,<2'), p['dependencies'][0]
print('metadata complete')"
```

**Card.** One file. Metadata only — no dependency, version or entry-point change.

**Exit.** `twine check` → `PASSED` for wheel and sdist; the assertion prints
`metadata complete`.

## 4 · Guardrails

**Anti-patterns.** Bumping `version` here — publishing is T1.16 and conflating them makes a
failed publish look like a metadata bug. Relaxing `<2` "while we're in the file". Rewriting
`serve/README.md` to please PyPI's renderer; broken relative links on the PyPI page are
acceptable, a README that stops serving repo readers is not.

**No-touch.** `[project.scripts]`, `[build-system]`, `[tool.hatch.*]`, `[tool.pytest.ini_options]`.

## 5 · Operations

- **Q. Is the name `apex-mcp` available on PyPI?** **Blocking, and unresolved.** Check before
  this task freezes the name into metadata: `curl -s -o /dev/null -w '%{http_code}'
  https://pypi.org/pypi/apex-mcp/json` — `404` means free, `200` means taken and the lane
  needs a new distribution name. Record the answer here.
- **Q. Which license?** Needs an owner decision; blocks nothing else in L1 but does block T1.16.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Metadata-only; the wheel still builds either way.

**Observability.** `twine check` in the L1 definition of done runs on every build.

signed_off: sha256:0a33ba91d43362a3fdd42d20a4f58265
