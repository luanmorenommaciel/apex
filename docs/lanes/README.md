# docs/lanes/ — the detailed build briefs

One research-backed brief per pipeline stage. Each is a **self-contained branch brief**: mission + exit criterion, mermaid graph, key decisions (with pinned versions), verify-gated build steps, an atomic task checklist, starter code, and verified pitfalls.

| Brief | Stage | Dir |
|---|---|---|
| `DEV.md`     | ① generate  | [`../../dev/`](../../dev/) |
| `JAR.md`     | ② capture   | [`../../jar/`](../../jar/) |
| `COLLECT.md` | ③ transport | [`../../collect/`](../../collect/) |
| `INFRA.md`   | ④ store/serve | [`../../infra/`](../../infra/) |
| `ENGINE.md`  | ⑤ reason    | [`../../engine/`](../../engine/) |
| `SERVE.md`   | ⑥ interface | [`../../serve/`](../../serve/) |

**To populate:** move the existing `LANE-1..6-*.md` here and rename per the table above. They already obey the contract; only the filenames change.

## Feeding a stage to an agent

Hand the agent **two files**: [`../../CONTRACT.md`](../../CONTRACT.md) (the interface) + the one brief. Then:

```bash
git checkout -b jar/T4-stage-metrics
# "Build this task from docs/lanes/JAR.md. CONTRACT.md is the frozen interface —
#  obey its field names exactly. The task's acceptance criterion is your test."
```
