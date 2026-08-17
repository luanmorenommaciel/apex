# tasks/ — task-specs, not plan items

A plan item is a **mention**: it names the evidence and leaves three answers to every
question. A task-spec is a **contract**: one atomic change, signed by a human on Behavior,
run by a machine on Contract, bounded by Guardrails, and reversible by construction.

> **Swap the engine, keep the spec** — the same rule as `AGENTS.md`. A spec that only one
> particular agent can execute is a plan item wearing a costume.

## File shape

```
tasks/T-<YYYYMMDD>-<slug>.md
```

Frontmatter is the machine-readable header; the six zones are the body.

| Key | Meaning |
|---|---|
| `id` | stable identity, matches the filename |
| `lane` / `leg` | where this sits in `docs/lanes/` |
| `effort` | `S` ≤1h · `M` ≤half day · `L` ≥half day. An `L` is usually two specs. |
| `touches_paths` | every path the change may write. Nothing outside this list. |
| `depends_on` | task ids that must be `done` first. Empty = startable now. |
| `human_gated` | `true` when a credential or a decision an agent cannot make is required |

## The six zones

| # | Zone | Owner | Contains |
|---|---|---|---|
| 1 | **Intent** | human | goal · context — *why this exists*, and what breaks without it |
| 2 | **Behavior** | human **signs** | `B-n` GIVEN / WHEN / THEN — observable, no implementation |
| 3 | **Contract** | machine **runs** | the literal commands · the card · the exit condition |
| 4 | **Guardrails** | the boundary | anti-patterns · no-touch paths and invariants |
| 5 | **Operations** | resolved in build | open questions — answered **in this file** as they are settled |
| 6 | **Reversal** | full profile | rollback · observability — how to undo, how you'd notice |

**Zone 2 is the signature line.** If a human cannot read the GIVEN/WHEN/THEN and say
"yes, that is what I want", the spec is not ready. **Zone 3 must be copy-pasteable** — a
command a reviewer runs without interpreting anything.

## Seals

`signed_off` is a digest over the body, so a spec cannot drift from its signature silently.

```bash
python3 tasks/seal.py sign  tasks/T-20260812-*.md   # stamp
python3 tasks/seal.py check tasks/*.md              # verify, exit 1 on drift
```

With `APEX_SPEC_KEY` set the digest is `hmac-sha256`; without it, plain `sha256` and the
line says so. An unkeyed seal detects **drift**, not **authorship** — do not read it as
authority it does not carry.
