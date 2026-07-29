# docs/lanes/ — the detailed build briefs

One research-backed brief per lane. Each is a **self-contained branch brief**: mission + exit criterion, mermaid graph, key decisions (with pinned versions), verify-gated build steps, an atomic task checklist, starter code, and verified pitfalls.

| Brief | Lane | Dir | Framing |
|---|---|---|---|
| `DEV.md`     | ① generate  | [`../../dev/`](../../dev/)       | to-build |
| `JAR.md`     | ② capture   | [`../../jar/`](../../jar/)       | to-build |
| `COLLECT.md` | ③ transport | [`../../collect/`](../../collect/) | to-build |
| `INFRA.md`   | ④ store     | [`../../infra/`](../../infra/)   | to-build |
| `ENGINE.md`  | ⑤ reason    | [`../../engine/`](../../engine/) | to-build |
| `SERVE.md`   | ⑥ interface | [`../../serve/`](../../serve/)   | to-build |
| `MEMORY.md`  | ⑦ recall    | [`../../memory/`](../../memory/) | **as-built** |
| `VERIFY.md`  | ⑧ refute    | [`../../verify/`](../../verify/) | **as-built** |

**Two framings, deliberately.** Briefs ①–⑥ were written *before* their lane existed and are
preserved as-written — they are the specification the lane was built against, and reading them
next to the result shows where the spec was wrong (all seven cross-lane contract rules came from
exactly that gap). `MEMORY.md` and `VERIFY.md` are **as-built**: both lanes were added mid-build
in response to what the first six uncovered, so a forward-looking brief for them would be
fiction. Each documents the lane as shipped, with the research that justified its decisions.

Every lane also has its own `README.md` covering as-built detail, layout, and how to run it.

## Feeding a lane to an agent

Hand the agent **two files**: [`../../CONTRACT.md`](../../CONTRACT.md) (the interface) + the one brief. Then:

```bash
git checkout -b jar/T4-stage-metrics
# "Build this task from docs/lanes/JAR.md. CONTRACT.md is the frozen interface —
#  obey its field names exactly. The task's acceptance criterion is your test."
```

**The contract is what makes this parallelizable.** Because every lane consumes and produces
contract rows rather than importing another lane's code, eight lanes were built concurrently
across 50+ commits with **zero merge conflicts**. Freeze the seam first; fan out second. A lane
may *add* a field; it may never rename or repurpose one, and only a ratified change amends the
contract.
