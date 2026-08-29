---
id: T-20260812-cursor-codex-config
task: T1.18
lane: serve
leg: L1
effort: S
touches_paths: [serve/README.md]
depends_on: []
human_gated: false
---

# T1.18 — Cursor + Codex config sections

## 1 · Intent

**Goal.** Let a Cursor or Codex user install Apex from the README alone.

**Context.** The lane brief names all three clients as targets and `SERVE.md` T12 accepts on
*"the same `.mcp.json` loads in Cursor/Codex"*. The README delivers a full `claude mcp add`
recipe and then says the other two *"read the same schema"* — true, and it never says **where
each one looks**. Two of the three supported clients are documented by implication.

## 2 · Behavior

**B-1** GIVEN the README WHEN a Cursor user reads it THEN the exact config path is named and
the project-scope vs user-scope distinction is stated.

**B-2** GIVEN the README WHEN a Codex user reads it THEN the same holds for Codex.

**B-3** GIVEN any of the three clients WHEN a user follows its section THEN the verification
step is named — how to confirm the server is connected and the tools are listed.

**B-4** GIVEN the sections WHEN read THEN each states that the `${VAR}` values expand from the
environment **at client start**, so exporting a variable afterwards has no effect until restart.

## 3 · Contract

```bash
cd /opt/projects/dataship/git/apex
grep -ci 'cursor' serve/README.md   # expect: >= 2
grep -ci 'codex'  serve/README.md   # expect: >= 2
grep -n 'restart' serve/README.md   # the expand-at-start caveat is present
```

**Card.** One README section (~25 lines), three subsections. Documentation only.

**Exit.** A reader can configure all three clients without leaving the file; the greps pass.

## 4 · Guardrails

**Anti-patterns.** Documenting a path from memory. **Verify each against that client's current
docs and record the source** — a wrong config path is worse than no section, because it looks
authoritative. Duplicating the whole env table per client; write it once and reference it.

**No-touch.** The Claude Code section, which is verified and correct — including the
flags-before-the-name warning, which was learned the hard way.

## 5 · Operations

- **Q. Do Cursor and Codex support the `${VAR:-default}` expansion form, or only `${VAR}`?**
  **Unverified, and it matters** — `serve/.mcp.json` relies on the `:-default` form for the
  password. If a client does not support it, that file fails to parse there. Verify per client
  and record the answer here; if unsupported, it becomes a defect in T1.17's shared config.

## 6 · Reversal

**Rollback.** `git revert <sha>`. Documentation only.

**Observability.** None automated — client config paths drift with client releases and nothing
in this repo will notice. Re-verify when a supported client ships a major version; note the
last-verified date in the section itself.

signed_off: sha256:936431640bb64460abd377af5aa3d03e
