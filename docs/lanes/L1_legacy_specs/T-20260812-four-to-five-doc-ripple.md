---
id: T-20260812-four-to-five-doc-ripple
task: T1.21
lane: serve
leg: L1
effort: S
touches_paths: [serve/README.md, serve/VALIDATION.md, docs/lanes/SERVE.md]
depends_on: [T-20260812-register-apex-status, T-20260812-gate-status-assert, T-20260812-stdio-gate-five-tools]
human_gated: false
---

# T1.21 — Close the four→five doc ripple

## 1 · Intent

**Goal.** Leave no document claiming four tools.

**Context.** "Exactly four tools" is asserted in **10 places** across code, tests, gates and
three documents. T1.06 changed the code and T1.07 the test; this task closes the prose. A doc
that contradicts the code is worse than a missing doc — `VALIDATION.md` in particular is a
record of what was **observed**, and a stale record is a false one.

## 2 · Behavior

**B-1** GIVEN `README.md` WHEN read THEN the tool table has five rows, the prose says five, and
the install comment matches.

**B-2** GIVEN `VALIDATION.md` WHEN read THEN the scope table lists `apex_status`, the stdio-gate
bullet says five, and **the test count matches the suite's actual output** — not an estimate.

**B-3** GIVEN `docs/lanes/SERVE.md` WHEN read THEN the mission statement and T11's accept
criterion both say five.

**B-4** GIVEN the repository WHEN grepped THEN no file claims four tools.

## 3 · Contract

```bash
cd /opt/projects/dataship/git/apex
cd serve && uv run --extra dev pytest -q 2>&1 | tail -2   # read the real count
cd /opt/projects/dataship/git/apex
grep -rniE 'four tools|exactly 4 tools|lists exactly the four' \
  serve/ docs/lanes/SERVE.md --include='*.md' --include='*.py'   # expect: no hits
grep -n 'passed' serve/VALIDATION.md                             # count matches the run above
```

**Card.** Three documents. No code, no tests.

**Exit.** The ripple grep returns nothing; the count in `VALIDATION.md` equals the number
pytest just printed.

## 4 · Guardrails

**Anti-patterns.** Writing a test count from memory — run the suite and copy the number; a
`VALIDATION.md` figure is a recorded observation, not a claim. Recording gate results without
rerunning the gates: T1.19 and T1.20 must have actually passed after their changes. Editing
`SERVE.md`'s **T1–T14 checklist** to reflect L1 work; that brief records what shipped, and L1
lives in `L1_tasks.md` and `tasks/`.

**No-touch.** `SERVE.md`'s Key decisions table and starter snippets — historical record of the
build, still accurate.

## 5 · Operations

- **Q. Should `SERVE.md` T11's accept criterion be edited, or annotated as superseded?**
  Resolve in build. Preference: **edit the number, add a one-line note pointing at L1** — the
  brief stays readable and the history stays traceable.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Documentation only.

**Observability.** The ripple grep in the Contract zone is reusable — run it whenever the tool
surface changes again, which L2 will do at least three more times.

signed_off: sha256:8a845e209b245b52f53bbca8f11b735b
