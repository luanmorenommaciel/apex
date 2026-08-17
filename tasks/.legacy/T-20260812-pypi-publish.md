---
id: T-20260812-pypi-publish
task: T1.16
lane: serve
leg: L1
effort: S
touches_paths: [serve/.mcp.json, serve/README.md, serve/VALIDATION.md, .mcp.json]
depends_on: [T-20260812-testpypi-rehearsal, T-20260812-root-mcp-json]
human_gated: true
---

# T1.16 — 🔒 PyPI publish, then drop `--from` everywhere

## 1 · Intent

**Goal.** Deliver the one-command install: `uvx apex-mcp`.

**Context.** This is L1's headline promise and the last of its four features. `serve/.mcp.json`
already carries the instruction to make this change — *"Replace `uvx --from ./serve apex-mcp`
with plain `uvx apex-mcp` once the package is published"*. This task executes that note.

**🔒 Human-gated.** Requires PyPI credentials **and** a resolved distribution name (T1.13's
open question).

## 2 · Behavior

**B-1** GIVEN a released version WHEN `uvx apex-mcp` runs on a clean machine THEN the server
starts, blocks on stdin, and writes zero bytes to stdout.

**B-2** GIVEN the release WHEN a user runs `claude mcp add --scope user --transport stdio apex
-- uvx apex-mcp` THEN `claude mcp list` reports `apex … ✔ Connected`.

**B-3** GIVEN both `.mcp.json` files WHEN read THEN `args` is `["apex-mcp"]` and the `_comment`
no longer instructs a future reader to make this change.

**B-4** GIVEN `README.md` and `VALIDATION.md` WHEN read THEN the `--from <path>` fallback is
gone and the *Known limits* entry about PyPI is removed.

## 3 · Contract

```bash
cd serve && rm -rf dist && uv build && uvx twine check dist/*
uvx twine upload dist/*                                  # 🔒 needs PyPI token

cd /tmp && uvx apex-mcp </dev/null >/tmp/p-stdout.bin 2>/tmp/p-stderr.txt
test ! -s /tmp/p-stdout.bin && echo "stdout: 0 bytes OK"
claude mcp add --scope user --transport stdio apex-verify -- uvx apex-mcp && claude mcp list
grep -rn '\-\-from' serve/.mcp.json .mcp.json serve/README.md serve/VALIDATION.md
```

**Card.** One upload + four documentation/config edits. No source change.

**Exit.** `stdout: 0 bytes OK`; `claude mcp list` shows connected; the final `grep` returns
nothing.

## 4 · Guardrails

**Anti-patterns.** Publishing before T1.15 passed — the version is immutable and a broken
release is permanent. Editing the config files **before** the upload succeeds, which leaves the
repo pointing at a package that does not exist. Publishing from a dirty tree: build from a
clean checkout so the artifact matches a commit.

**No-touch.** Source. This task ships what T1.01–T1.14 built and changes no behavior.

## 5 · Operations

- **Q. Distribution name confirmed available?** Inherit the answer from T1.13's open question.
  **Must be resolved before upload** — the name is permanent once claimed.
- **Q. Who owns the PyPI project, and is it a shared account or an org?** A single personal
  account is a bus factor for every future release. Record the decision here.
- **Q. Release version?** `0.2.0`, matching the contract version already in `pyproject.toml`.

## 6 · Reversal

**Rollback.** The config and doc edits revert cleanly with `git revert`. **The release itself
does not** — PyPI allows yanking, never deleting or replacing. Treat the upload as one-way and
recover by publishing `0.2.1`.

**Observability.** `claude mcp list` is the user-visible check. A broken release surfaces as
every new user failing at install with no signal reaching this repo — which is why B-1 is
verified from `/tmp` on a clean resolution, not from the checkout.

signed_off: sha256:80a58ddca294e882d591df3e2d73c957
