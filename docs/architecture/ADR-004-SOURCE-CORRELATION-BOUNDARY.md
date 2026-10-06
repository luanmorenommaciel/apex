# ADR-004 — Source correlation privacy boundary

- Status: proposed; no implementation is authorized by this document
- Date: 2026-09-23
- Decision owner: Luan
- Origin: L4/F4.1 in `docs/lanes/L4_PROPOSAL.md`

## Context

F4.1 asks the product question that the existing telemetry cannot answer:
which source line or notebook cell produced a stage. The JAR currently records
stage metrics, plan fingerprints and optional Spark SQL `execution_id`, but no
source locator. `SparkListenerStageSubmitted` is already observed by the JAR,
so Spark may supply a `StageInfo.details` stack trace. That trace is not a safe
telemetry payload: it can include absolute paths, user names, notebook internals
and free-form application text.

The current privacy boundary is deliberate. `CONTRACT.md` requires paths to be
dropped before storage, and the collector deletes `file_path`. The JAR also
redacts plan text before egress. Source correlation must preserve those rules;
it cannot obtain a useful UI by sending a raw stack trace and relying on a
downstream consumer to hide it.

This is a design decision, not a request to add a column or start a listener
change. It establishes the questions that must be resolved before a Task-Spec
or implementation can be accepted.

## Decision requested

No product decision has been accepted yet. The recommended direction for owner
approval is an opt-in, additive source locator with these limits:

1. Resolve the first application frame in the JAR, then discard the raw stack
   trace before egress.
2. Emit a locator only when the job supplies an approved source root and the
   frame can be normalized to a relative path below that root. Absolute paths,
   home directories, URIs, query text and source snippets must never be stored.
3. Represent notebooks only when the runtime provides an explicit stable logical
   notebook and cell identity. Do not infer a notebook location from a synthetic
   stack frame; otherwise emit `unknown`.
4. Keep the locator optional. Missing, redacted, ambiguous or invalid source
   data is an honest `unknown`, never a guessed file or line.
5. Treat a source locator as diagnostic metadata for a self-hosted team, not as
   a cross-run primary key. Plan fingerprints and existing job/execution keys
   retain their current meanings.

If the owner does not approve storing a repository-relative path, the safe
fallback is to retain only an opaque per-installation reference. That fallback
can support internal joins but cannot honestly name a source line in Serve or
the Console without a separately designed local resolver.

## Proposed additive shape

The following is a proposal for a future contract decision, not a schema change
in this ADR:

| Field | Meaning | Privacy boundary |
|---|---|---|
| `source_kind` | `file`, `notebook_cell`, or `unknown` | enum only; absent means unknown for historical events |
| `source_locator` | repository-relative path plus one-based line, or an approved logical notebook/cell locator | optional; no absolute path, URI, source code, query text or user home segment |
| `source_ref` | opaque, per-installation stable identifier for the normalized locator | optional; not a global identity and never a substitute for a display locator |

`source_locator` must be omitted when the source root is absent, the frame is
outside it, normalization fails, or the result violates the approved syntax and
length limits. A consumer may display it only as a hint attached to the exact
stage evidence; it must not claim that the locator identifies a plan shape or a
future run.

The choice of payload location — attributes versus additive typed columns — is
deferred. The first implementation must justify that choice against the existing
contract, Collector mapping, ClickHouse DDL and compatibility plan.

## Alternatives considered

### Emit the full stack trace

Rejected. A full trace carries more than the product needs and conflicts with
the existing rule that source paths are dropped. Redacting it later leaves a
large, difficult-to-test PII surface and does not establish a stable source
identity.

### Emit a plain absolute path and line

Rejected. Absolute paths expose user names and machine layout, do not work
across developers or containers, and are unstable after relocation.

### Emit an opaque hash only

Acceptable only if the owner rejects repository-relative locators. It preserves
some correlation without leaking a path, but it cannot answer the user-facing
question "which line?" unless a trusted local resolver is designed separately.

### Emit a repository-relative locator behind opt-in configuration

Recommended pending owner approval. It is actionable for the self-hosted team
while keeping the configured root and absolute environment details out of
telemetry. It remains source metadata rather than a cross-run identity.

### Infer notebook identity from a stack trace

Rejected. Notebook frames are runtime-specific and often synthetic. A line
number without a stable cell identity is misleading; emit `unknown` unless an
explicit notebook/cell identity is available.

## Consequences

### Positive

- F4.1 gains a bounded path to useful source correlation without weakening the
  existing redaction policy.
- Non-SQL, generated-code and notebook workloads preserve honest unknowns.
- A future Engine/Serve/Front surface can distinguish a proven locator from an
  unavailable one instead of fabricating correlation from timing or plan text.

### Costs and risks

- Repository-relative paths can still be sensitive operational metadata; owner
  approval, syntax restrictions and tests are required.
- Source locations move with edits and must not be used as a durable join key.
- Spark, notebook vendors and container layouts may expose frames differently.
- The feature crosses JAR, contract, Collector, Infra and presentation lanes;
  an additive field alone does not prove end-to-end behavior.

## Preconditions for implementation

Before a Task-Spec or implementation PR, record owner decisions for:

1. whether repository-relative locators are permitted at rest;
2. the opt-in configuration name, source-root semantics and allowed path syntax;
3. the notebook identity provider and behavior when it is unavailable;
4. the payload location and migration/compatibility plan; and
5. the first public consumer: Engine, Serve, Console, or documentation only.

No implementation may broaden this ADR into source-code capture, raw stack
storage, live intervention or multi-tenant access control.

## Acceptance evidence for a future implementation

1. Unit tests select an application frame and discard the raw stack trace.
2. Tests prove that an absolute path, user-home component, URI, email, query
   text and source snippet never reach the emitted payload.
3. Valid frames under the configured root produce a bounded relative locator;
   frames outside it produce `unknown`.
4. Notebook tests require an explicit stable logical notebook/cell identity;
   synthetic or incomplete frames remain `unknown`.
5. Contract, Collector and ClickHouse tests prove the optional fields survive
   the chosen path without reinterpreting historical events.
6. Consumer tests render a locator only when it is present and valid, and label
   every other state as unavailable.
7. An authorized runtime pass covers a Spark SQL job, an RDD/non-SQL control,
   and one missing-source control. Offline tests alone do not prove delivery or
   vendor-specific stack behavior.

## Rollback

The intended future change is additive and opt-in. Disabling source correlation
must stop emitting new locators without invalidating historical telemetry.
Consumers must tolerate absent fields. If redaction, compatibility or runtime
evidence fails, revert the feature implementation and keep the current
no-source-correlation behavior; this ADR itself records the unresolved decision
and needs no data migration.

## Related work

- `docs/lanes/L4_PROPOSAL.md` — F4.1 motivation and sequencing.
- `CONTRACT.md` — current telemetry and redaction boundary.
- `docs/architecture/ADR-003-AQE-REPLAN-DETECTION.md` — current ADR format and
  precedent for separating owner acceptance from offline evidence.
- Issue #115 and PR #126 — execution-to-stage attribution are separate from
  source correlation. Neither proves a source locator.
