---
id: T-20260812-five-tools-assertion
task: T1.07
lane: serve
leg: L1
effort: S
touches_paths: [serve/tests/test_server_tools.py]
depends_on: [T-20260812-register-apex-status]
human_gated: false
---

# T1.07 — Move the exactly-four assertion to five

## 1 · Intent

**Goal.** Re-pin the tool surface at its new size.

**Context.** `test_exactly_the_four_contracted_tools` (`test_server_tools.py:38`) asserts an
**exact ordered list**. That strictness is correct and worth keeping: a subset assertion would
let a fifth tool appear by accident, and an accidental tool on a server a model can call is a
real security event, not a cosmetic one. This commit exists so that changing the pinned
surface is a deliberate, reviewable act.

## 2 · Behavior

**B-1** GIVEN the built server WHEN `list_tools()` is called THEN the assertion compares
against an exact ordered list of **five** names.

**B-2** GIVEN a sixth tool were added WHEN the suite runs THEN it fails — the assertion stays
exact, never `issubset`, never a count.

**B-3** GIVEN the test module WHEN its docstring is read THEN it says five.

## 3 · Contract

```bash
cd serve
uv run --extra dev pytest -q                       # fully green again
git show --stat HEAD                               # exactly one file changed
grep -n 'issubset\|set(\|len(' tests/test_server_tools.py | grep -i tool   # expect: no hits
```

**Card.** One test file. Two edits: the name list, the docstring.

**Exit.** Suite green; the diff touches only `tests/test_server_tools.py`; the assertion is
still an ordered equality.

## 4 · Guardrails

**Anti-patterns.** Relaxing the assertion to a subset or a count so it stops needing
maintenance — the maintenance **is** the control. Bundling any source change into this commit.

**No-touch.** Every file except `tests/test_server_tools.py`.

## 5 · Operations

- **Q. Where does `apex_status` sit in the order?** Resolve in build. Preference: **first** —
  it is the tool a user calls before any other, and the list doubles as documentation.

## 6 · Reversal

**Rollback.** `git revert <sha>` alongside T1.06. Reverting this alone leaves the suite red,
which is the correct signal that the pair belongs together.

**Observability.** This assertion **is** the observability for the tool surface. If it is ever
loosened, nothing else in the repo notices a tool appearing.

signed_off: sha256:8b09c18003c954177f5f54579ffa496d
