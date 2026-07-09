# Codex Branch and DataFlint Solution Comparison

Date: 2026-07-09
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Remote Snapshot

Latest `git fetch origin --prune` found no new remote updates after the previous refresh. Current heads:

| Ref | HEAD | Notes |
| --- | --- | --- |
| `gustocezar/feature/codex-desacoplamento-geradores` | `76a33d8` | Local Codex branch; not pushed; contains Commander harness, planning, reassessment. |
| `origin/gustocezar/feature/desacoplamento-geradores` | `bd8a08b` | Evaluated branch; keep untouched. |
| `origin/gustocezar/feature/cowork-desacoplamento-geradores` | `1c675cd` | Latest update is governance/documentation: Captain's Report, backlog P2-12, `VALIDACAO.md` section 7 stub. |
| `origin/gustocezar/feature/kimi-desacoplamento-geradores` | `e271e32` | Unchanged; Go core, validator, runbooks, comparison docs. |
| `origin/spike/apex-v0.1` | `53479f5` | Unchanged; full local platform spike. |
| `origin/estudo/dataflint` | `8953cbe` | DataFlint study branch. |
| `origin/reuniao/2026-06-30-commander-plan` | `2ff9914` | Meeting/issue plan branch. |

No push was performed.

## Executive Recommendation

The strongest Apex solution is a hybrid, not a single existing branch:

```text
spike/apex-v0.1 platform spine
  + Kimi EvidenceValidator, runbooks, negative baselines
  + Cowork MCP apply_fix, ADR-005, issue traceability
  + Codex Commander contract tests and safety plan
```

The best decision for Luan is to pick one of two execution paths:

| Path | Use When | Recommendation |
| --- | --- | --- |
| Platform-first | The team wants a real V1 platform quickly | Start from `spike/apex-v0.1` in a separate integration branch, then port Kimi validation and Cowork `apply_fix`. |
| Contract-first | The team wants minimum risk while the evaluated branch stays under review | Continue from the Codex branch and import detector/config/validator/apply-fix contracts incrementally. |

Do not raw-merge `cowork`, `kimi`, or `spike` into the evaluated branch. Their shapes are too different.

## What Each Solution Has

| Capability | Codex local | Evaluated base | Spike v0.1 | Cowork | Kimi | DataFlint |
| --- | --- | --- | --- | --- | --- | --- |
| Safe local branch | Yes | No, under review | Remote branch | Remote branch | Remote branch | External product |
| Event-log parsing | Yes, via existing `apex.apexlib` | Yes | Yes, with Go loader | Yes, Python poller/ingest | Yes, Go/Python design | Yes, via Spark plugin/history/SaaS |
| Real platform stack | No | No | Yes: Spark, MinIO, ClickHouse, HyperDX | Partial `v1-skeleton` | Partial CREI/MCP direction | Yes, product and SaaS/OSS |
| Detector coverage | 1 local skew candidate | v4 skew | 5 deterministic detectors: skew, shuffle, plans, GC, OOM | Mostly skew | Skew/spill/memory direction | Broad alert catalog |
| Configurable thresholds | Not yet | Limited | Yes, `diagnostics.yaml` | Mostly hardcoded | Runbooks/validator | Product-managed |
| Evidence validation | Planned | Some v4 evidence validation | Guards in detector config | Missing explicit validator | Strongest validator | Proprietary/not transparent |
| Negative baseline | Planned | Partial scenario discipline | Some healthy-run guards | Missing | Strongest explicit baseline | Not visible |
| MCP | Planned as contract | No | Yes: list/detect/report/analyze | Yes: findings/stage/slow/diagnose/apply_fix | Yes, smaller surface | Yes, Spark MCP server in SaaS/Copilot |
| `apply_fix` | Planned as preview-first | No | No | Yes, but can write files after LLM output | No | DataFlint claims IDE code-level fixes in SaaS Copilot |
| UI | No | No | HyperDX/ClickStack | No rich UI | No rich UI | Strong UI: Spark UI enhancement + SaaS dashboard |
| LLM optional | Yes by design | Yes | Yes; degrades to detectors-only | No, CrewAI required for diagnosis/fix | Yes | SaaS AI agents |
| Merge risk | Low | N/A | High if raw-merged | High if raw-merged | Medium/high if raw-merged | External benchmark, no merge |

## Solution-by-Solution Assessment

### 1. Codex Local Branch

Best use: integration bridge and safety harness.

What it has:

- local `apex.commander` telemetry contract;
- NDJSON ClickStack MVP;
- deterministic skew finding by `job_id`;
- CLI demo;
- 44 local tests passing in the last verification;
- branch reassessment and implementation plan.

What it lacks:

- real ClickHouse/ClickStack;
- real MCP server;
- multi-detector coverage;
- EvidenceValidator;
- runbooks;
- UI;
- production Spark environment.

Verdict: best branch to coordinate safely, not enough alone for V1 product.

### 2. Evaluated Base: `desacoplamento-geradores`

Best use: protected stable baseline.

What it has:

- v4 skew slice;
- scenario-driven evidence;
- watcher/oracle discipline;
- validated skew evidence and stage correlation.

What it lacks:

- real V1 platform;
- ClickStack/MCP/product loop;
- multi-detector runtime.

Verdict: keep untouched while under review.

### 3. `spike/apex-v0.1`

Best use: platform spine.

What it has:

- full local stack: Spark, Delta, MinIO, ClickHouse, HyperDX/ClickStack;
- Go eventlog-loader;
- `apex_diagnostics` package;
- 5 deterministic detectors;
- `diagnostics.yaml`;
- MCP tools: `list_runs`, `detect_skew`, `detect_shuffle`, `detect_plans`, `detect_gc`, `detect_oom`, `get_report`, `analyze_run`;
- optional CrewAI that degrades to detectors-only when no LLM is configured.

What it lacks:

- `apply_fix`;
- Kimi-style EvidenceValidator;
- explicit negative baselines for each detector;
- low-risk merge shape for the current evaluated branch.

Verdict: strongest technical base if Commander chooses platform-first.

### 4. `cowork`

Best use: closed-loop UX source.

What it has:

- V1 skeleton;
- ClickHouse schema/ingest/poller;
- CrewAI diagnosis;
- MCP server with `apply_fix`;
- ADR-005;
- DataFlint study and comparison docs;
- Captain's Report with honest blockers.

What it lacks:

- broad detector coverage;
- non-LLM first path;
- EvidenceValidator;
- negative baseline;
- clean merge shape.

Risks:

- `apply_fix` depends on LLM output and can write directly after backup;
- tracked cache/archive/doc noise;
- new `VALIDACAO.md` section 7 is incomplete;
- `root_cause` hardcoding and missing `no_skew_baseline.yaml` are called out by its own report.

Verdict: do not use as base. Port `apply_fix` after converting it to preview-first plus explicit approval.

### 5. `kimi`

Best use: validation and production discipline.

What it has:

- Go core under `go-apex/`;
- EvidenceValidator with provenance/schema/operator/correlation/distribution/structural checks;
- runbooks JSON;
- deterministic T1/T2 direction;
- negative baseline concept;
- comparison and unification docs.

What it lacks:

- full visible platform;
- HyperDX/ClickStack UI;
- `apply_fix`;
- immediate product experience for the IDE.

Verdict: port validator/runbooks/baselines before adding more LLM behavior.

### 6. DataFlint

Best use: market benchmark and parity target.

Official sources checked:

- Product site: `https://www.dataflint.io/`
- GitBook docs: `https://dataflint.gitbook.io/dataflint-for-spark/`
- OSS repo: `https://github.com/dataflint/spark`

Current official picture:

- DataFlint OSS is a Spark UI enhancement installed as a Spark plugin.
- GitHub shows latest OSS release `0.9.9` on 2026-05-18.
- Docs list Spark 4.0.x, 3.5.x, 3.4.x, 3.3.x, and 3.2.x as supported.
- Features include real-time cluster status, run summary, cluster status, error handling, visual SQL plan, stage breakdown, heat map, SQL plan modes, syntax highlighting, alerts, Iceberg integration.
- Alert catalog includes reading/writing small files, Iceberg inefficient replace, partition skew, many small tasks, memory over/under-provisioning, wasted cores, large broadcast, broadcast candidate in sort merge join, large cross join scan, large partition size, long filter conditions, and query failures.
- DataFlint SaaS now positions itself as production-aware AI agents for Spark with Spark MCP, IDE Copilot, Cluster Agent, Review Agent, Fleet Observability, and enterprise/SOC2 messaging.

Important change in competitive framing:

The Apex differentiator cannot be only "MCP in the IDE" anymore. DataFlint now claims Spark MCP plus IDE Copilot. Apex must differentiate through openness, local/on-prem control, explicit validation, transparent thresholds, repo-native governance, custom detectors, and safer human-approved fix flow.

## Differences Versus DataFlint

| Dimension | DataFlint Advantage | Apex Opportunity |
| --- | --- | --- |
| Maturity | Existing OSS/SaaS product, UI, docs, install paths | Build only what Luan needs first; avoid copying entire product surface |
| Install | Spark plugin; no-code spark-submit path | Zero-JAR/event-log path can reduce cluster-injection friction |
| UI | Strong Spark UI/SaaS dashboard | HyperDX via spike gives a local path, but needs polish |
| Alerts | Broad catalog already documented | Version detectors as code, add tests and baselines per alert |
| Agentic/IDE | Spark MCP + Copilot claimed in SaaS | Make MCP transparent, auditable, repo-local, and safe by default |
| Cluster optimization | Claims Cluster Agent/right-sizing | Apex can integrate with local platform and DataShip policies |
| Governance | Product/SOC2 claims | Apex can expose exact rules, thresholds, validator decisions and evidence |
| Privacy | Claims metadata-only and enterprise controls | Apex can run fully local/on-prem with no vendor lock-in |
| Fixes | Claims code-level optimization in IDE | Apex should implement preview-first fixes with explicit approval and backups |

## Best Solution

The best Apex V1 is:

```text
Use spike/apex-v0.1 as the platform spine
Use Kimi as the validation layer
Use Cowork as the closed-loop IDE/fix layer
Use Codex as the safety contract and integration branch
Use DataFlint as the benchmark, not the design to clone
```

Recommended build order:

1. Freeze evaluated branch; do not disturb `origin/gustocezar/feature/desacoplamento-geradores`.
2. Keep this Codex branch local as the decision/control branch.
3. Ask Luan to approve **platform-first** or **contract-first**.
4. If platform-first: create a separate integration branch from `spike/apex-v0.1`.
5. Port Kimi EvidenceValidator/runbooks/negative baseline.
6. Port Cowork `apply_fix`, but convert it to preview-first and explicit approval.
7. Keep Codex Commander tests as the acceptance gate: every path must answer `debug_job(job_id)` deterministically without LLM first.

## Issues To Attribute Next

Most aligned existing issues:

- `#40` branch/evidence inventory: this document closes the comparison work.
- `#38` CrewAI/MCP by `job_id`: next product-visible implementation.
- `#37` SparkListener/ClickStack MVP: platform telemetry path.
- `#41` agentic contracts: safety, memory, MCP, RAG, autonomy.

New issue candidates from the latest comparison:

- Adopt `spike/apex-v0.1` as platform spine or formally reject it.
- Port Kimi EvidenceValidator and negative baseline.
- Convert Cowork `apply_fix` to preview-first guarded fix.
- Define DataFlint parity targets: alerts, UI, MCP, agentic behavior, and security posture.
