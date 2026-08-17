---
id: T-20260812-graphify-rebuild
task: T1.22
lane: serve
leg: L1
effort: S
touches_paths: [graphify-out/]
depends_on: [T-20260812-four-to-five-doc-ripple]
human_gated: false
---

# T1.22 — Rebuild the graphify graph

## 1 · Intent

**Goal.** Make the knowledge graph know about L1.

**Context.** `graphify-out/` was built **2026-07-27** and is how work in this repo gets its
bearings — this leg was scoped from a graph query. It currently has no `apex_status`, no
`resolve_settings`, no `ServerStatus`. A stale graph does not fail loudly; it quietly answers
questions about a codebase that no longer exists, which is the same failure shape as a stale
`VALIDATION.md`.

## 2 · Behavior

**B-1** GIVEN the rebuilt graph WHEN queried for `apex_status` THEN the node exists with its
source location in `server.py`.

**B-2** GIVEN the rebuilt graph WHEN queried for the serve lane THEN `ServerStatus`,
`resolve_settings` and `store_health` appear.

**B-3** GIVEN the rebuild WHEN it completes THEN the pre-existing nodes for `analyze_run`,
`compare_runs`, `search_kb` and `suggest_fix` are still present — an update, not a truncation.

**B-4** GIVEN `tasks/` WHEN the graph is built THEN the task-specs are indexed, so a future
session can ask what L1 committed to.

## 3 · Contract

```bash
cd /opt/projects/dataship/git/apex
graphify . --update
graphify query "apex_status server status tool" --budget 800
graphify query "suggest_fix" --budget 400        # B-3: pre-existing nodes survive
```

**Card.** No source change. Regenerated artifacts under `graphify-out/`.

**Exit.** All four behaviors observable in the query output.

## 4 · Guardrails

**Anti-patterns.** A full rebuild when `--update` suffices — it re-spends extraction tokens for
the same result. Committing `graphify-out/` if it is meant to stay untracked; it is currently
**untracked** in this repo, so check `git status` before adding anything and keep that decision
deliberate.

**No-touch.** `graphify-out/.graphify_root` and `.graphify_python`, which pin the scan root and
interpreter.

## 5 · Operations

- **Q. Should `graphify-out/` be committed?** Open, and bigger than L1 — it is 1.3 MB of
  generated JSON that every session benefits from and every rebuild churns. Decide at repo
  level; do not settle it silently here.
- **Q. The graph warns it uses the pre-#1504 node-ID scheme.** A `--force` re-extract fixes
  same-name-file collisions. Costs a full extraction; weigh it when the next lane starts.

## 6 · Reversal

**Rollback.** Re-run `graphify . --update` at any time; the graph is derived, never a source of
truth.

**Observability.** Staleness is silent by nature. The only real guard is rebuilding at the end
of each leg — which is why this task is the last item in L1 rather than a background chore.

signed_off: sha256:cfd9be1e193b3d48f3a9392f6187e624
