# Pre-submit provenance for E2E runs

This is an additive, opt-in governance convention for an E2E run. It records
the authorized intent before an execution without changing the Spark, JAR,
Collector, ClickHouse, Engine, Serve, or CI contracts. Existing task specs and
historical receipts remain valid without being rewritten.

## The custody chain

Create the artifacts in this order:

1. Write an immutable Task-Spec in Markdown. It describes the scope, boundary,
   hypothesis, allowed actions, acceptance criteria, and rollback.
2. Calculate the SHA-256 of the exact Task-Spec bytes. A later edit produces a
   different hash and invalidates authorization for the changed spec.
3. Create an authorization manifest JSON that contains the Task-Spec hash.
   Calculate the SHA-256 of the exact manifest bytes only after it is written.
4. Execute only the authorized scope and create a post-run receipt that records
   the manifest path and manifest hash together with the observed outcome.

```text
Task-Spec (.md) --task_spec_sha256--> authorization manifest (.json)
authorization manifest --authorization_manifest_sha256--> receipt (.json)
```

The manifest must never contain its own hash. If authorization changes, create
a new manifest and point to the earlier one with `supersedes_manifest_sha256`;
do not rewrite the earlier artifact.

## Identity boundaries

`harness_execution_id` identifies one governed harness attempt. It is not a
Spark identifier and must not be substituted for `app_id`, `job_id`,
`stage_id`, `stage_attempt`, `trace_id`, `span_id`, or a Spark SQL execution
identifier. Runtime receipts may record both sets of identifiers, but their
meanings remain separate.

## Authorization manifest

The following fields are required for a manifest. The example is valid JSON;
the SHA-256 values are illustrative only.

```json
{
  "provenance_schema_version": "2.0",
  "task_spec_id": "P1.10",
  "task_spec_path": "docs/lanes/task-specs/P1.10-GATE-TUNNEL-LIFECYCLE.local.md",
  "task_spec_sha256": "91ab182dd438e91f184646a66aa46f2f1c75ff06071e91cda4f96afb48fc6d2d",
  "harness_execution_id": "DD-30-P1.10",
  "authorization_created_at_utc": "2026-08-19T00:42:21Z",
  "authorized_by": "human_operator",
  "authorized_scope": "diagnose gate tunnel lifecycle only; no Spark submit",
  "predecessor_receipt_sha256": "168adea6f34a25a0aa9ded72b35539744e9540a87b275d9715aeddf930bd7d33",
  "supersedes_manifest_sha256": null,
  "temporal_assurance": "local_declared_not_externally_anchored",
  "secrets_included": false
}
```

`task_spec_sha256` is computed before the manifest exists. For an initial
manifest, `supersedes_manifest_sha256` is `null`; a replacement manifest must
reference the SHA-256 of the prior manifest.

## Post-run receipt

The receipt binds execution evidence to the authorization manifest. It must
include the exact Task-Spec and manifest references used by the run. The
following is a valid JSON example:

```json
{
  "provenance_schema_version": "2.0",
  "task_spec_id": "P1.10",
  "task_spec_path": "docs/lanes/task-specs/P1.10-GATE-TUNNEL-LIFECYCLE.local.md",
  "task_spec_sha256": "91ab182dd438e91f184646a66aa46f2f1c75ff06071e91cda4f96afb48fc6d2d",
  "authorization_manifest_path": "evidence/authorization-manifests/P1.10-GATE-TUNNEL-LIFECYCLE-2026-08-19-v2.json",
  "authorization_manifest_sha256": "3fca95d47ea668c370f1632f598357f48b6300927624599f9e5473f65ef0b8ca",
  "harness_execution_id": "DD-30-P1.10",
  "authorization_created_at_utc": "2026-08-19T00:42:21Z",
  "receipt_created_at_utc": "2026-08-19T00:49:00Z",
  "predecessor_receipt_sha256": "168adea6f34a25a0aa9ded72b35539744e9540a87b275d9715aeddf930bd7d33",
  "temporal_assurance": "local_declared_not_externally_anchored",
  "secrets_included": false,
  "outcome": "proven_gap"
}
```

Receipts should record the normal E2E correlation identifiers (`app_id`,
`job_id`, `stage_id`, and trace/span identifiers) only when the execution
actually produces them. A preflight that stops before Spark starts must say so
rather than inventing runtime identifiers.

## Temporal assurance and secrets

SHA-256 proves the integrity of the bytes being compared; it does not prove an
independent creation time. For local experiments, use
`local_declared_not_externally_anchored` and treat timestamps as declared local
evidence. Stronger temporal assurance requires an external anchor, such as a
signed commit, trusted timestamp, or CI attestation.

Set `secrets_included` to `false`. Do not place passwords, tokens, connection
URLs, raw credentials, or environment dumps in a Task-Spec, manifest, or
receipt. Sanitize runtime evidence before it enters a receipt.
