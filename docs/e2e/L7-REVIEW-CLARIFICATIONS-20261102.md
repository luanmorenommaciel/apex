# L7 evidence review: clarified limits and a minimal JVM experiment

Evidence follow-up completed 2 November 2026. This supplements the [28 October report](L7-REAL-JOB-20261028.md) and [30–31 October report](L7-FOLLOWUP-20261031.md). Their evidence and integrity files remain unchanged. The purpose is to make the existing results more useful to their authors and reviewers; no product behavior or P7.2 decision is changed by this document.

## Exact subject and evidence types

The historical local candidate is commit `dbb9b94e9bd75e50d1e820abfbdd4c446f2ef4ff`, tree `0683db0f637dfc2efb647fe353e15e82de6d48bd`: main `0e84c10b0a950e5b59421fbf768e8352c7ee6b52` plus the recorded heads of #182/#194/#195/#197, with two documented local merge resolutions. It is not an official integration SHA and does not include #185. The source checkout was clean before and after this follow-up.

| Evidence | Observed result | What the denominator means |
|---|---|---|
| Initial Python recheck | 23/23 reported; one negative-control claim withdrawn | The original negative-control entry did not invoke the identity validator. Its historical receipt is retained, with this correction. |
| Focused reconciliation | 16/16 checks passed | Seven recorded transport groups through a shared validator; five mutated negative controls through that same validator; one stage-16 text check; two fingerprint-only counterfactual comparisons; one integrity check. |
| Front recheck | 10/10 checks passed | Extracted actual TypeScript execution, replay of saved DOM text, synthetic controls and source inspection. No new browser. |
| New JVM experiment | 19 fingerprints in 128 fresh-function-object constructions; one fingerprint in 32 fixed-object constructions | Synthetic Catalyst logical plans in one JVM using Spark 4.0.1 and exact APEX fingerprint code. No SparkSession or Spark job. |
| Historical custody | 191/191 manifest-covered files matched | Byte integrity of the retained historical package. |

These denominators overlap and must not be added together as distinct coverage. They are characterization results, not additional E2E scenarios or acceptance of the product. Some checks pass by reproducing an existing limitation. Claude's completed review supplied hypotheses; this follow-up independently checked them. The external review is not an additional runtime execution.

The [reduced results](evidence/l7-20261102/results-summary.json) record the observations and scope. Full historical payloads, source-replay commands and raw logs remain available privately on request after a sensitivity check. The public summary alone cannot independently revalidate those private captures. The new JVM experiment is included below for independent reproduction.

## Transport agreement remains supported

Seven historical argument sets across four tools were recalculated: analysis of each job; forward, reverse and missing-baseline comparison; recall; and unassessed verification. All 21 payloads still match within their three-path group, with the expected job identities and statuses checked. Replaying the actual Python `compare` function with the saved stage/finding inputs reproduces both two-job comparison responses, forward and reverse, field for field. The missing-baseline case was checked for transport equality, identity and status, not replayed through `compare`.

The initial negative-control claim was withdrawn: that script did not call the identity predicate on its mutated trio. In the corrected follow-up, the same validator processes all seven captured groups and five mutations (all three wrong-job responses, one wrong-job response, missing identity, swapped comparison identities, and absent paths). All real groups pass and every mutation is rejected for the expected reason. Three equal wrong-job responses are specifically rejected on identity, despite passing equality. The older 19-check verifier comprised ten recalculations and nine inspections of already-recorded values or outcomes. The new verifier writes outside the historical package.

HTTP, MCP via API and MCP direct ClickHouse share diagnostic implementation. Their agreement establishes consistency for these cases, not an independent proof of the diagnostic policy. This is MCP stdio testing, not MCP-over-HTTP transport or desktop-client onboarding.

## Pod 1: rendering and contract observations

1. **Compare drops unmatched baseline rows.** The actual TypeScript produces 20 current-run rows; stages 0 and 16 are current-only, and their unmatched baseline rows are absent. A synthetic surplus-baseline control reproduces the omission. The earlier rendering oracle agreed with that same policy, so its success does not establish a complete two-sided comparison. The 31 October wording “independent calculations from resource data” also has this limit: the row calculations reused the Console pairing policy; the arithmetic check was not an independent completeness oracle.
2. **The Verify assertion failure was already explained on 27 October.** The actual live-test predicate rejects the populated captured text because its casing/spacing differs from the accepted literals. This is a test-oracle limitation, not evidence that the populated screen failed to render. The earlier failure remains a failure; this follow-up did not edit or rerun that suite to turn it green.
3. **Some displayed labels have weaker evidence than their wording implies.** Equal shuffle bytes enter the `growing` branch through `>=`. The `AQE reshaped` rule receives task count and configured partitions, but not an AQE observation. `assessStage()` invokes it without first requiring an exchange, so the wording alone does not demonstrate an AQE event. Git history attributes these lines to the August implementation, before #182; they must not be presented as regressions introduced by that PR.
4. **Verify rendering is not safety enforcement.** Approval and `applied=false` are fixed JSX labels; mechanism confirmation is a constant SQL NULL. Runtime certification/verdict, predicted saving, noise floor, proposal, replays and identifiers do depend on stored values; cluster width comes from an outcomes join. The synthetic row establishes selected rendering/projection behavior, not a replay, applied fix or safety certification.
5. **Zero persisted findings is ambiguous.** The run-header mapping labels zero findings as healthy without independently establishing that Engine evaluation completed. The 28 October pre/post-Engine captures already illustrated this distinction.

Primary source: [Compare](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/front/src/screens/CompareScreen.tsx), [Verify](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/front/src/screens/VerifyScreen.tsx), [rules](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/front/src/contract/rules.ts), [repository mapping](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/front/src/data/repository.ts).

## Pod 2: fingerprint mechanism and Memory measurement

The JVM experiment builds, in one JVM and without a SparkSession, otherwise identical logical plans containing three ordinary predicates and two ScalaUDF expressions wrapping separate instances of the same pure Boolean function class. Fresh function objects yielded 19 fingerprints over 128 constructions; reusing the same objects yielded one fingerprint over 32 constructions. With the three ordinary predicates retaining their relative order, the construction admits at most 20 operand orders. This is a construction count, not an estimated real-world failure rate. Recomputing SHA-256 of the same normalized string is a hashing sanity check, not an independent semantic oracle.

This reproduces a possible identity-instability mechanism for these ScalaUDF operands: Catalyst sorts commutative operands by `hashCode`, and a ScalaUDF hash includes its unprinted function object. It does **not** establish the cause of the historical stage-16 difference. The historical jobs are separate Spark applications; the probe does not test variation across driver JVMs, Python UDFs or the exact historical plan.

The retained stage-16 texts contain **three operands plus two metadata items** (the `And` operator class and `None`), not five operands. Their printed operand order changes from A–B–A to A–A–B; the two A operands are text-identical, and all three contain `UDF(`. There is therefore no non-UDF operand whose relative order supplies an independent control. The token is compatible with an unnamed ScalaUDF's rendering, but does not identify the function object, class or state by itself. The suggested Delta log-replay markers (`.path`, `.dataChange`, `.deletionVector`, `SerializeFromObject`, `MapPartitions`, `DeserializeToObject`) are absent. Other statistics fields do not identify a particular Delta function. Delta attribution and historical causality remain hypotheses, not findings confirmed by this text check.

By source reading at [#185's pinned head](https://github.com/luanmorenommaciel/apex/blob/a5c2ca45bda8e0898dc20460901fe2e83ab7ae8b/jar/src/main/scala/apex/ApexPlanFingerprint.scala), its successful canonicalization path scrubs the rendered text after ordering has been chosen. That text scrub does not reorder operands. This is useful scope information for its contract discussion, not a runtime result against #185 or a request to change that PR's scope. Do not label the historical difference either a proven semantic change or a proven false alarm.

For Memory, all 16 recorded outcomes agree with `sum(task_count × p50)` over the captured stages. That is an estimate, not a measured sum of individual task durations. It can under- or overestimate depending on the distribution. Full task-duration event logs are not present in this evidence package, so no measured bias for these jobs is claimed. The population remains 15 stored plan rows, eight API-listed shapes, 16 outcomes overall and 14 associated with the listed shapes. Seven plans lie outside the two focal jobs; their individual originating executions are not established by the retained rows alone.

Primary source: [APEX fingerprint](https://github.com/luanmorenommaciel/apex/blob/0e84c10b0a950e5b59421fbf768e8352c7ee6b52/jar/src/main/scala/apex/ApexPlanFingerprint.scala), [Memory aggregation](https://github.com/luanmorenommaciel/apex/blob/0e84c10b0a950e5b59421fbf768e8352c7ee6b52/memory/src/apex_memory/clickhouse.py), and Spark 4.0.1 [commutative ordering](https://github.com/apache/spark/blob/v4.0.1/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/expressions/Expression.scala#L1392), [UDF representation](https://github.com/apache/spark/blob/v4.0.1/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/expressions/ScalaUDF.scala#L49), [tree hashing](https://github.com/apache/spark/blob/v4.0.1/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/trees/TreeNode.scala#L205).

## Pod 3: separate transport, alignment and verdict policies

The historical pair was executed without an intentional tuning intervention, using the same generated input. This is useful as an A/A control, but it does not establish identical runtime conditions or the absence of real metric variation.

- **Reverse comparison has more than a fingerprint change.** Forward regressions include a new MEMORY finding on stage 16 and higher MEMORY confidence on stage 18. Reverse regressions include higher SKEW_ON_JOIN confidence on stage 21 (0.69 to 0.85), as well as the fingerprint change. A new offline counterfactual changed only the current-side stage-16 fingerprint to the baseline value in memory. Executing the actual `compare()` function still returns `regressed` in both directions, with the same finding-level reasons and no fingerprint regression. Thus the finding changes alone suffice in this one recorded pair. This synthetic counterfactual is not a new A/A run, proof of a false alarm, or measurement of a noise floor.
- **Missing fingerprints have inconsistent alignment policies.** Both historical stage-0 captures contain an empty fingerprint. The API pairs the same id and labels it `stage_id+plan_fingerprint`; the Console leaves it unmatched. A synthetic 64-zero sentinel can also match different ids in the API fingerprint tier. The raw stored FixedString was not retained for that case; projection conversion is not established as its cause. The 64-zero case is a synthetic fixture check; neither historical stage-0 capture contained that sentinel. No universal claim about production telemetry is made.
- **Metric direction differs from run diagnosis.** A synthetic GC increase from 100 to 101 with no measured floor produces a metric label of `regressed`, while the run stays `unchanged` with no regression-list entry. That label does not establish a statistically meaningful slowdown.
- **Finding identity can differ from stage identity.** A synthetic stage-id shift with the same fingerprint preserves stage alignment but reports one resolved and one introduced finding. This reproduces a mechanism relevant to the existing identity study; it does not demonstrate an AQE event in the historical jobs.

For the Serve review requested on #182: the [parity gate](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/tools/console_parity_gate.py) imports 11 statement entries from [ch.py](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/src/apex_mcp/ch.py), compares raw read-only ClickHouse results with API results, and checks explicitly described store behaviors. These files match the tested local candidate. This pins that resource-projection boundary; it does not independently settle Console versus diagnostic semantics, real-world fingerprint identity, or all P7.2 behavior. Existing local gate/browser receipts remain complementary to the maintainer's requested review and final-SHA acceptance.

One boundary remains distinct: this gate compares the same `refused` CTE through raw SQL and the API, but does not assert a known refusal count against `assessStage()`. [The Python test](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/serve/tests/test_ch.py#L1225) asserts SQL fragments, while [the Front test](https://github.com/luanmorenommaciel/apex/blob/74fdb0791825aa89c419694ec71f2aa3e6ea4d74/front/src/contract/refusedCount.test.ts#L8) checks a TypeScript transliteration. **Agmar already reports a live check with six synthetic stages and the expected count of three in the PR body.** This distinction was also recorded in [the existing 20 October comment](https://github.com/luanmorenommaciel/apex/pull/182#issuecomment-6278335092); it is reconfirmed here, not a new defect or a claim that SQL was never tested. A versioned seeded expected-count assertion would make that particular proof repeatable in the gate. No SQL defect or automatic merge blocker is established.

Primary diagnostic source: [diagnose.py](https://github.com/luanmorenommaciel/apex/blob/0e84c10b0a950e5b59421fbf768e8352c7ee6b52/serve/src/apex_mcp/diagnose.py).

## Two documentary clarifications

**Timeout:** the first harness explicitly waited up to 75 seconds; the proposed 30-second harness-deadline explanation is not supported by that source. The original browser network failure/nginx 499 remains causally unresolved because its network error detail was not captured. The later approximately 60-second 504 experiments are separate positive observations, not a retrospective explanation of the 499.

**28 October job count:** the manifest records two executed jobs, one without captured width and one with width. The detailed browser/API/MCP walkthrough focuses on the explicitly named second job. “One job” in that walkthrough should not be interpreted as the total number executed in the whole session.

## Options for the team, with impact

| Topic | Choice to clarify | Practical impact |
|---|---|---|
| P7.2 verdict ownership | API-owned verdicts or a maintained Front engine with an explicit parity contract | Either path needs agreed inputs, missing-data handling, measured-floor policy and acceptance assertions; transport equality alone cannot choose it. |
| Compare completeness | Display unmatched baseline rows, or explicitly label a current-run-only view | Makes removed/unmatched work visible, or makes the narrower scope clear. |
| Identity | Define how absent fingerprints and shifted finding stage ids participate in comparison | Avoids presenting stronger correspondence than the data establishes. |
| Evidence labels | Separate estimate, observation, metric direction, evaluated status and certified result | Helps readers avoid interpreting a rendering label or estimate as validated improvement. |

These are review inputs, not assignments or approvals. Ask/P7.11 and the prototype/P7.14 remain separate discussions. Product changes, new runtime investigations and final official-SHA gates need their own scoped work. This follow-up does not complete the wider 525-ID functional audit.

## Reproduce the new JVM experiment

The [standalone JVM directory](evidence/l7-20261102/jvm/) contains the exact pinned copy of the APEX fingerprint implementation, the probe, Scala/Spark dependencies and sbt version. It is a standalone reproducer under `docs/`, not the product implementation or a compilation target of the current product CI workflows. With JDK 17 and sbt available:

```sh
cd docs/e2e/evidence/l7-20261102/jvm
sbt 'runMain FingerprintProbe'
```

The runner checks the fixed-object control, canonical-text SHA agreement and whether the sampled fresh objects produced more than one fingerprint. The observed count of 19 is not a cross-run acceptance threshold; identity hashes and the finite sample can differ on another JVM run. It starts no SparkSession, database or browser. Dependency download and compilation are required on a cold machine.

The [manifest](evidence/l7-20261102/SHA256SUMS) covers this new report, its reduced results and the JVM files. It establishes byte integrity of the public packet, not independent timing, historical payload correctness or team approval.
