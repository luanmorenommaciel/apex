# Apex Console — React front end

A runnable Vite + React + TypeScript implementation of the seven console
screens, styled with Tailwind and reading the frozen **contract v0.6** tables
through the Apex API in `serve/`. The browser holds an API token and no
database user, and carries no SQL: since 2026-10-19 the API is the console's
**only** door (`D-api-only`, recorded in `tasks/.plans/front-lane-hardening.yaml`).

Start the API first ([serve/RUNBOOK.md](../serve/RUNBOOK.md), it uses port
8099), then:

```bash
VITE_APEX_API_TOKEN=<token> make up    # compose, through the host gateway  -> http://localhost:5173
VITE_APEX_API_TOKEN=<token> make dev   # Vite on the host, proxies /v1 to 127.0.0.1:8099
make up-fixtures                       # console alone, served from the recorded gate run
make help                              # every target
```

The console runs no store of its own and reaches none: ClickHouse belongs to
the `infra/` lane and only `serve/` reads it.

Without Docker: `nvm use && npm ci && make dev` — Node 22 (`.nvmrc`; the
`engines` range in `package.json` is what every devDependency accepts, and
`engines.test.ts` keeps it in step with the image and CI). `.env.example`
defaults to `VITE_DATA_SOURCE=http`.

`VITE_APEX_API_PROXY_TARGET` moves the dev proxy's target; the browser keeps
calling `/v1` relative and stays same-origin either way. At boot, `http` asks
`/v1/health` once: the API's liveness body or a 401 mounts the app (a 401 is
then reported on every screen, never worked around), and no HTTP answer at all
renders a "no store answered" page naming `/v1/health`. The recorded gate run
is served only by `DATA_SOURCE=fixtures`, never as a fallback.

### Configure a deployment

Development compose forwards `/v1` to `http://host.docker.internal:8099` by
default. Supply an explicit target when the API is remote or uses another port:

```bash
VITE_APEX_API_PROXY_TARGET=http://apex-api.example.internal:8099 docker compose up --build console
```

**The production image is configured at container start, not at build.** Vite
inlines every `VITE_*` reference into the bundle, so an image built once would
otherwise be pinned forever to the API, token and mode it was compiled
against. The entrypoint renders `/config.js` from its own environment and
`index.html` loads it before the app; `src/data/runtimeConfig.ts` is the read
side. One image therefore serves every deployment:

| Variable | Default | Meaning |
|----------|---------|---------|
| `DATA_SOURCE` | `http` | `http` (the browser holds an API token, never a database user) or `fixtures` (the recording, explicit). Anything else is refused at boot, by name |
| `APEX_API_UPSTREAM` | `http://127.0.0.1:1` | Where nginx proxies `/v1`. Defaults to an unroutable address so a `fixtures` image still boots; an `http` image without it warns at boot and renders "no store answered" |
| `APEX_API_TOKEN` | *unset* | The bearer token written into `/config.js`. A credential for the API, never for the store — scope and rotate it per consumer |
| `APEX_API_URL` | *unset* | Only for a deliberate cross-origin call. The API sends no CORS header, so a browser blocks that; leave it unset and let nginx forward `/v1` |

**What the image sends with every response.** A same-origin
`Content-Security-Policy` (`default-src 'self'`; `style-src` also allows the
inline style attributes React sets; fonts are bundled, both doors are proxied,
so nothing off-origin is needed), `X-Content-Type-Options: nosniff`,
`X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` and
a `Permissions-Policy` denying camera, microphone and geolocation. Text and JSON
are gzipped; `/assets/` is cached for a year as immutable (Vite hashes the
names), `/config.js` is never cached. No `Strict-Transport-Security`: the
image listens on plain http and terminates no TLS — put a terminator in front
of it. Both proxies time out explicitly (`proxy_connect_timeout 5s`,
`proxy_send_timeout 30s`, `proxy_read_timeout 60s` in `nginx.conf`); a very
large `spark_events` can push a run list toward the read bound, which is the
one to raise.

**Behind a TLS terminator.** The image terminates no TLS, by decision
(2026-10-19): it listens on port 80 only, never sends
`Strict-Transport-Security`, and never redirects to `https`. Put a terminator
in front of it — an ingress, a load balancer, a reverse proxy — that owns the
certificate, answers on 443, sets HSTS, and forwards plain http to the image
with `X-Forwarded-Proto: https`. What the image guarantees in return is that
every redirect it issues is a path (`absolute_redirect off`,
`port_in_redirect off` in `nginx.conf`), so a browser that arrived over https
is never sent to an `http://` URL; the API token in `/config.js` and every
`/v1` request then travel only over the terminator's TLS.

```bash
docker build --target prod -t apex-console:prod .
docker run --rm -p 8080:80 \
  -e APEX_API_UPSTREAM=http://apex-api.example.internal:8099 \
  -e APEX_API_TOKEN=<token> \
  apex-console:prod
```

`make prod` does the same through the host gateway; override any of the three
on the command line:

```bash
make prod APEX_API_TOKEN=<token>        # http, the default
make prod DATA_SOURCE=fixtures          # the recording, no API in the path
```

No short hostname is mandatory: deployments may use a Compose address, host
gateway, private DNS name, or HTTPS reverse proxy without rebuilding assets.

Rotating the token is a restart, not a rebuild. It is still a *public*
credential — a client-side console cannot hide one — but it is a credential for
the API, scoped and revoked per consumer, and never for the store.

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
| 5 | Rule 7 | Footnoted a future execution→stage map as the remedy for the stage-29 near-miss | Rule 7 detects the reshape from `task_count` vs `spark.sql.shuffle.partitions`. Contract v0.6 can emit optional stage `execution_id`, but no read-side mapping has been proven, so stage-level transition attribution remains unavailable |
| 6 | Support matrix | `spark 4.1.2` | `spark 4.0`, inside the published matrix |
| 7 | Rule 2 | Replays `18m04s / 16m31s / 17m48s` yield an 8.9% floor, but the screens claimed 17.4% — which would have made the 11% prediction *resolvable* and broken the verdict | Replays are `16m03s / 17m48s / 19m07s`. `measureNoiseFloorPct()` computes **17.37%** from them, so `runtime_unresolved` is now a derived result rather than an asserted one |

Item 7 is the useful one to show a client: making rule 2 executable exposed a
number that had been asserted rather than measured.

---

## One door: the Apex API

Until 2026-10-19 the console could also query ClickHouse straight from the
browser, carrying a read-only database user (`apex_ro`) to every visitor. That
door was removed by decision (`D-api-only`): anything a visitor could read,
they could read all of, and a second door is a second thing to secure. What
remains:

```
src/data/repository.ts   <- the seam
  HttpRepository         reads over serve/'s /v1 (DATA_SOURCE=http, the default):
                         the browser holds an API token and no database user
  FixtureRepository      serves the recorded gate run (DATA_SOURCE=fixtures)
```

No screen knows where a row came from. The rows are the projections
`serve/src/apex_mcp/ch.py` computes — the one home of the console's SQL — and
a test on the serve side reads the Repository interface and the row types from
`src/contract/types.ts` and fails when a route stops projecting a field. `/v1`
is proxied (Vite in dev, nginx in the image), so the API needs no CORS header
and the browser never leaves its origin. serve's live parity gate runs each of
those statements as raw SQL under a read-only user and holds the API's rows to
it (`serve/RUNBOOK.md` §3.1).

**`refused_count` is computed, not stored.** Among the five loudest p99/p50
ratios of a run, it counts the stages rules 1, 6 and 7 refuse a tail claim for.
The run rollup in `serve/src/apex_mcp/ch.py` carries a `refused` CTE that
encodes those rules in SQL, so the list shows it; `src/contract/refusedCount.test.ts`
holds that arithmetic to `assessStage()` over the recording, and serve's
parity gate holds the API's rows to the statement run as raw SQL. `-1`,
rendered `—`, means the API did not compute it — never `0`.

---

## Layout

```
src/
  contract/
    types.ts        canonical v0.6 shape + backward-compatible projection
    rules.ts        THE SEVEN RULES as pure functions + assessStage()
  data/
    http.ts         the Apex API client (token, paths, no SQL)
    fixtures.ts     the recorded gate run, embellished
    repository.ts   Repository interface + HttpRepository + FixtureRepository
    useRepository.tsx  provider + useRead (keyed cache, no data-fetching library)
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

Defined once in `tailwind.config.js`. The three typefaces it names — JetBrains
Mono, IBM Plex Sans, Archivo Black — ship in the bundle from the `@fontsource`
packages imported in `src/main.tsx` (latin subset, the weights used), so no
visitor's browser contacts Google Fonts and the console renders the same
offline. The palette is **semantic, not decorative** — each colour is a claim:

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

**Real:** the rule functions, the repository seam, the API client, routing, the runs search and filter, stage selection, layer switching,
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
| `/ask` | The conversation is the two-turn script above. The pieces now exist — `serve/` serves the eight MCP tools over `/v1`, and `HttpRepository` is written — and what is missing is a product decision on what `/ask` does with them and whether it needs a model. Recorded as `D-2026-09-23-ask-consumer` in `tasks/.plans/serve-api-sweep.yaml` | product |
| `/memory` | Renders *"nothing indexed yet"*: `apex.plan_memory` is written by the memory lane, not the console. Until that lane runs over a job there is no history to recall | `memory` |
| `/verify` | The two independent verdicts come from `apex.fix_verifications`, written by the verify lane; with no row the screen states the emptiness and which lane owes it. The proposed fix is also still prose — turning it into a testable config overlay is that lane's job | `verify` |
| `/compare` | Needs a second run of the same plan fingerprint to align a baseline; shows *"no baseline"* until the store holds one | `collect` / `engine` (producing runs) |
| `/runs/:jobId` | `attributionIsAvailable()` returns `false`: v0.6 emits optional producer-side `execution_id`, but no proven execution-to-stage mapping is available to the console. A transition therefore cannot name a stage. The noise floor also cannot be recomputed live because the contract stores only the two arms' medians, so the console falls back to the stored value and says it did | read-side mapping plus runtime evidence |

The pattern is the same everywhere: an empty state that names the missing
process beats a plausible number that was never computed.
