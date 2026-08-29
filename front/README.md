# Apex Console — React front end

A runnable Vite + React + TypeScript implementation of the seven console
screens, styled with Tailwind and reading the frozen **contract v0.5** tables
straight from ClickHouse.

```bash
make store         # start infra/'s ClickHouse and seed it — the canonical store
make ch-user       # create apex_ro, the read-only user the browser ships
make up            # console against that store       -> http://localhost:5173
make up-fixtures   # console alone, served from the recorded gate run
make help          # every target
```

The console no longer runs a ClickHouse of its own: the store belongs to the
`infra/` lane. Compose reaches its host-published HTTP port by default instead
of depending on a compose-only service name or shared network alias.

Without Docker: `npm ci && make dev` — with no store reachable,
`VITE_DATA_SOURCE=auto` falls back to the recorded gate run.

### Configure the ClickHouse endpoint

Development compose uses `http://host.docker.internal:8123` by default. Supply
an explicit URL when infra publishes another port or the store is remote:

```bash
VITE_CLICKHOUSE_URL=http://clickhouse.example.internal:8123 docker compose up --build console
```

The production image treats nginx configuration as a startup template. Set
`CLICKHOUSE_UPSTREAM` when the container starts; it is an endpoint only, never a
credential, and nginx keeps the browser on same-origin `/clickhouse`:

```bash
docker build --target prod -t apex-console:prod .
docker run --rm -p 8080:80 \
  -e CLICKHOUSE_UPSTREAM=http://clickhouse.example.internal:8123 \
  apex-console:prod
```

No short hostname is mandatory: deployments may use a Compose address, host
gateway, private DNS name, or HTTPS reverse proxy without rebuilding assets.

---

## Why this is not just the mockup in React

The HTML mockup in the parent project is a **design reference**. This app is the
same design with the contract's reasoning moved into code. Concretely:

`src/contract/rules.ts` implements the seven rules as **pure functions**, and
every refusal the UI renders is the return value of one of them. No screen
re-derives a threshold and no screen softens one — which is the whole point of
the shared floor in `CONTRACT.md`. If you want to see the product's thesis as
code, read that one file.

```ts
// rule 1 — the tail-bound bar is COMPUTED, never configured
export function tailBoundBar(nTasks: number, slots: number): number {
  if (slots <= 1) return Number.POSITIVE_INFINITY;
  return (nTasks - 1) / (slots - 1);
}
```

---

## Divergences from the mockup, and why

I audited the screens against `CONTRACT.md` and `PIPELINE.md` before writing
this. Six divergences were found and all six are corrected here; a seventh
surfaced once rule 2 became executable.

| # | Rule | The mockup showed | This app shows |
|---|------|-------------------|----------------|
| 1 | Rule 1 | Refusals led with the 1 MiB volume floor; the computed bar was absent | The refusal table has a **BAR (n−1)/(s−1)** column, computed per stage. No 5× or 10× constant exists anywhere in the source |
| 2 | Rule 6 | Stage 11 refused as "2 tasks are not a distribution" | Named as rule 6: `n ≤ slots` makes rule 1's bar undefined, so the stage is **excluded**, not cleared |
| 3 | Rule 3 | Absent | Plan memory counts **distinct configurations after canonicalisation** (`'5.0'` and `'5'` are one config). A fix with 3 attempts and 1 distinct config is shown as *not attributable to tuning* |
| 4 | Rule 5 | Absent | A quiet transition log produces a `skew_absence_not_evidence` withholding on the run screen and a guardrail row on Verify |
| 5 | Rule 7 | Footnoted a future execution→stage map as the remedy for the stage-29 near-miss | Rule 7 detects the reshape from `task_count` vs `spark.sql.shuffle.partitions`. Contract v0.5 still has no execution→stage map, so stage-level transition attribution remains unavailable |
| 6 | Support matrix | `spark 4.1.2` | `spark 4.0`, inside the published matrix |
| 7 | Rule 2 | Replays `18m04s / 16m31s / 17m48s` yield an 8.9% floor, but the screens claimed 17.4% — which would have made the 11% prediction *resolvable* and broken the verdict | Replays are `16m03s / 17m48s / 19m07s`. `measureNoiseFloorPct()` computes **17.37%** from them, so `runtime_unresolved` is now a derived result rather than an asserted one |

Item 7 is the useful one to show a client: making rule 2 executable exposed a
number that had been asserted rather than measured.

---

## Querying ClickHouse from the browser

This was an explicit choice, and it has two consequences worth stating plainly:

1. **The credential ships to the browser.** `contract/01-readonly-user.sql`
   creates `apex_ro` with `readonly = 1` and `GRANT SELECT` only. Anything a
   visitor can read, they can read all of — appropriate for a bench, not for a
   multi-tenant deployment.
2. **Same-origin via proxy.** Vite (dev) and nginx (prod) front ClickHouse at
   `/clickhouse`, so the database never needs `add_http_cors_header`.

Parameters are passed as ClickHouse query parameters (`{job:String}`), never
interpolated, so a job id from the URL cannot become SQL.

```
src/data/repository.ts   <- the seam
  ClickHouseRepository   queries the database (the current choice)
  FixtureRepository      serves the recorded gate run
  HttpRepository         ...is the one to write when serve/ becomes the front door
```

Swapping to `serve/` means implementing one interface. No screen changes,
because no screen knows where a row came from.

**One honest gap:** `refused_count` is derived from the stage rows, not stored,
so the runs list cannot compute it in a single query. It renders as `—`, never
as `0` — "we did not compute it" is not "there were none". Deriving it list-wide
needs either a materialised view or the `serve/` endpoint.

---

## Layout

```
src/
  contract/
    types.ts        canonical v0.5 shape + backward-compatible projection
    rules.ts        THE SEVEN RULES as pure functions + assessStage()
  data/
    clickhouse.ts   HTTP client, parameterised queries
    queries.ts      every SQL statement, argMax(col, ts) for latest attempt
    fixtures.ts     the recorded gate run, embellished
    repository.ts   Repository interface + two implementations
    useRepository.tsx  provider + useAsync (no data-fetching library)
  components/
    atoms/          Label Mono Card Pill Metric Bar Diff Prose
    molecules/      NavBar KpiCard SignalStrip RefusalTable StageNode
                    WithheldPanel DualVerdictPanel GuardrailList LayerTabs DataTable
    layout/         Shell Page
  screens/
    RunsScreen RunDetailScreen FindingScreen AskScreen
    CompareScreen MemoryScreen VerifyScreen
```

### Routes

| Path | Screen |
|------|--------|
| `/runs` | triage inbox — search + findings filter both live |
| `/runs/:jobId` | lineage (3 switchable layers) + problem detail + rule chain |
| `/runs/:jobId/findings/:findingId` | evidence, no-op gate, the floor chart |
| `/ask` | natural language in, structured diagnostic out |
| `/compare` | baseline vs current, aligned on plan fingerprint |
| `/memory` | plan memory — what worked, what did not |
| `/verify` | proposed diff + the two independent verdicts |

---

## Design tokens

Defined once in `tailwind.config.js`. The palette is **semantic, not
decorative** — each colour is a claim:

| Token | Hex | Meaning |
|-------|-----|---------|
| `spark` | `#e25a1c` | brand / selection |
| `finding` | `#fb4934` | a finding Apex will defend |
| `withheld` | `#fabd2f` | withheld or unresolved — **never** "warning" |
| `certified` | `#8ec07c` | certified / passed |
| `muted` | `#665c54` | evaluated and refused |
| `memory` | `#d3869b` | plan memory |
| `canvas` / `surface` / `raised` | `#131516` / `#1d2021` / `#282828` | surfaces |

Type: **JetBrains Mono** for every measurement, identifier, plan and config key;
**IBM Plex Sans** for reasoning prose, never for a number; **Archivo Black** for
the wordmark.

Nothing is coloured for emphasis alone.

---

## What is mocked and what is real

**Real:** the rule functions, the SQL, the repository seam, the ClickHouse
client, routing, the runs search and filter, stage selection, layer switching,
every derived number on screen (ratios, bytes/task, deltas, the noise floor, bar
heights).

**Mocked:** the Ask Apex conversation is scripted — two turns, and the second is
a refusal, because a console that only ever agrees is the thing this product
argues against. Wire it to `serve/`'s tool endpoints to make it real.

---

## What waits on other lanes

All seven screens are implemented and render today — none is a stub. But parts
of them are deliberately inert until a process in another lane runs or ships,
and each screen says so on screen rather than faking the data. The ledger:

| Screen | What is inert today | Which lane owes it |
|--------|--------------------|--------------------|
| `/ask` | The conversation is the two-turn script above. Real diagnostics need `serve/`'s tool endpoints — and, on this side, writing `HttpRepository` against the existing `Repository` interface | `serve` |
| `/memory` | Renders *"nothing indexed yet"*: `apex.plan_memory` is written by the memory lane, not the console. Until that lane runs over a job there is no history to recall | `memory` |
| `/verify` | The two independent verdicts come from `apex.fix_verifications`, written by the verify lane; with no row the screen states the emptiness and which lane owes it. The proposed fix is also still prose — turning it into a testable config overlay is that lane's job | `verify` |
| `/compare` | Needs a second run of the same plan fingerprint to align a baseline; shows *"no baseline"* until the store holds one | `collect` / `engine` (producing runs) |
| `/runs` | `refused_count` renders `—` list-wide — the "honest gap" above: it needs a materialised view or the `serve/` endpoint | `infra` or `serve` |
| `/runs/:jobId` | `attributionIsAvailable()` returns `false`: contract v0.5 still carries no execution→stage map, so a transition cannot name a stage. The noise floor cannot be recomputed live either — the contract stores only the two arms' medians, so the console falls back to the stored value and says it did | future contract revision |

The pattern is the same everywhere: an empty state that names the missing
process beats a plausible number that was never computed.
