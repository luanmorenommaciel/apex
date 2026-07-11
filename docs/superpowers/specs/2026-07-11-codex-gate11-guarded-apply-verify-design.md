# Gate 11 Design: Guarded Apply/Verify

Date: 2026-07-11
Branch: `gustocezar/feature/codex-desacoplamento-geradores`
Prepared by: Codex

## Decision

Add a guarded apply path named `apply_recommendation`, not a raw `apply_fix`.

## Why

Gate 10 created recommendation and preview. The next safe step is to allow a selected preview to be applied only when the caller proves that the human-approved diff is still the current diff.

## Components

- `build_fix_preview`
  - returns `before_sha256`, `after_sha256`, and `diff_sha256`;
- `preview_recommendation`
  - returns an approval token bound to job, recommendation, target, hashes, and diff;
- `apply_recommendation`
  - requires `apply_root`;
  - requires the matching approval token;
  - writes only after guard checks pass;
- `verify_recommendation_apply`
  - verifies final file content hash.

## Approval Token

The token is a deterministic hash over:

```text
job_id
recommendation_id
target
before_sha256
after_sha256
diff_sha256
```

It is not a secret. It is a proof that the caller is applying exactly the preview that was reviewed.

## Safety

- No `apply_root`, no write.
- Outside `apply_root`, no write.
- Invalid token, no write.
- Changed source file, token mismatch and no write.
- Apply returns verification evidence.
- `apply_fix` remains unavailable.

## Out Of Scope

- No automatic Spark re-run.
- No before/after ClickHouse telemetry comparison.
- No branch push.
- No general arbitrary code patching.

## Next Gate

Gate 12 should compare execution evidence:

```text
before finding -> guarded apply -> re-run job -> collect telemetry -> compare finding status
```
