# Phase 8B — proposed implementation-ready specification

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Approval and objective

**CONDITIONAL GO candidate specification only.** The following features are audit-supported candidates, not team-approved implementation or bank-approved products/methods. Obtain explicit team approval before changing functionality. Do not deploy/publish restricted data, retrain models or alter operational method approval as part of this scope.

Objective: let a viewer distinguish source banking segment, observed behavioral bands, actual Savings evidence and historical experimental performance while preserving every current engine decision, priority, reason, provenance fingerprint and review control.

## Protected files/contracts

Do not modify `engine.py`, `evidence.py`, `data_access.py`, `analytics.py`, `build_data.py`, `replay.py`, `review_service.py`, `audit_store.py`, `deployment_data.py`, `historical_evaluation.py`, canonical CSV/manifest, alias key, historical experiment artifacts or existing SQLite histories. Keep the 17-column feature contract, Phase 7 design tokens, native routes and existing session keys. No dependencies, product thresholds, risk bands or model-approval flags are added.

In particular, `analytics.portfolio_frame()` must still exclude the raw customer_segment field. Do not weaken its privacy test to add the new context. A new allowlisted sidecar helper avoids altering the existing protected analytics/hash contract.

## Work packages and exact proposed files

| Package | Files expected to change/create | Outputs / complexity estimate |
| --- | --- | --- |
| B0 — acceptance baseline protection | MODIFY `scripts/run_final_regression.py`, `scripts/verify_final_acceptance.py`, `tests/test_acceptance_gate.py`; NEW `tests/fixtures/required_test_inventory.json` | Freeze/verify current 443 IDs and their prior JUnit provenance, including all 96 combinations; fail deletion of any current case. Low implementation complexity, critical priority |
| B1 — safe source segment metadata | NEW `segment_context.py`, `tests/test_segment_context.py`; MODIFY only Customer 360 presentation in `ui_views.py` | Alias-safe, allowlisted source segment/current-snapshot explanation. Low–medium |
| B2 — scoped segment analytics and Savings explanations | MODIFY relevant `ui_views.py` renderers and presentation helpers in `ui_components.py`; NEW `tests/test_intelligence_views.py` and/or `tests/test_product_context.py` | Filters and evidence context, no new eligibility/ranking. Medium due to filter/state/privacy regression surface |
| B3 — historical AI comparison | NEW `experimental_evidence.py`, `tests/test_experimental_evidence.py`; MODIFY Inactivity/Audit render sections in `ui_views.py` | Validated historical JSON comparison; live fitted inference explicitly unavailable. Medium |
| B4 — acceptance and documentation | Extend behavior-specific tests; new Phase 8B report/runbook after implementation approval | Full source-bound acceptance retaining all 443 plus new cases; desktop/tablet/mobile rehearsal. Medium validation effort |

These are relative complexity estimates, not measured schedules. B0 precedes all integration acceptance; B1 precedes banking filters; B3 can follow independently after artifact-validation tests. No changes to `app.py` routing or `ui_shell.Workspace` are required for the minimal scope.

## B0: correct the retention baseline first

The current runner passes `outputs/phase7/tests.xml`, enforcing 308 prior IDs. Change the authorized implementation to use an explicitly selected, hash-pinned current prior baseline (`outputs/final_acceptance/verified_final/tests.xml`, 443 IDs) or a reviewed noncustomer required-ID fixture. Do not compare the new run with itself. Add negative tests deleting any newly added protection case and a gate-matrix case; both must fail. Preserve source/JUnit freshness checking and rejection of failures/errors/skips. Do not update the frozen dataset/policy/decision reference.

## B1: proposed metadata API

`segment_context.py` should contain small pure functions, not a classifier:

- `BANKING_SEGMENTS`: the verified literal labels Retail, SME, Corporate, NGO/NPO, Trust. This is a display allowlist, not bank suitability policy.
- `banking_segment_frame(index)`: read index.values internally, normalize only exact known case/whitespace variants, return alias + banking_segment + origin marker. Unknown/missing/unrecognized strings → Unknown. Never return raw customer_id or arbitrary source text.
- `selected_banking_segment(index, alias)`: return safe label, `source-provided current snapshot`, `effective date unknown`, data/policy reference and a fixed explanation: membership is supplied by customer_segment, not inferred from transactions.
- `filter_banking_segment(frame, context, selected)`: one-to-one alias join into a copy; validate uniqueness; preserve original core columns/order, priorities and ratings. Return a display subset only.

Optional cache must key on immutable index/data version and never return caller-mutable cached objects. Do not infer historical membership or use segment as a predictor. New/missing labels must not create eligibility or a canonical-data rewrite.

Customer 360: add a compact native context card/caption beside existing snapshot evidence. Preserve existing table order and shared selected alias. Do not print raw source text when unrecognized.

## B2: filter/UI behavior

Use native styled controls and Phase 7 helpers. Add Banking segment (source snapshot) selectors to Inactivity, Relationship Value and Product Opportunity; an Overview breakdown/filter is optional after scope labels are correct. Keep per-view new widget keys distinct from existing keys. Default ALL must reproduce prior rows/charts exactly. Changing a banking filter should reset that table's page through existing pagination context without silently selecting another global customer.

- Keep full-population KPIs 50,000/2,052/20/47,928 in their declared global scope; display filtered subtotal separately. These are acceptance reference values, never hardcoded UI outputs.
- Apply banking segment and existing outcome/activity filters as display intersections. Empty subsets show a truthful empty state, not fallback to another segment or synthetic rows.
- Rename the existing Activity segment label to Observed activity band while retaining its key/values; source banking labels and behavioral bands must never be conflated.
- Relationship-value percentile remains global observation-cohort rank. Do not replace it with a within-segment rank or modify operational priority. Segment-level medians/counts are descriptive display summaries only.
- Do not add a segment filter or rank override to the operational manager queue in the minimal scope. Queue, Passport, review and replay behavior remain unchanged.

Savings evidence context must call `index.passport(alias)` and reuse existing fields: known holdings/gap, historical qualifying deposit evidence, actual G4/G5/final statuses/reasons, cutoff, source/policy fingerprints and current-snapshot uncertainty. It must say staff-review discussion, never approved offer/contact authorization. Segment-specific bank suitability is Unavailable because no catalogue/rules exist. Other observed labels may appear only as held-product metadata; do not suggest lending/insurance/FX products or invent terms. Add no new review/write/contact control.

## B3: historical comparison contract

`experimental_evidence.py` should parse only a fixed server-controlled, trusted JSON artifact using existing JSON/file/hash utilities. No model fitting, binary deserialization, user path/upload, API call or probability estimation. Whitelist displayed fields; do not dump raw artifact paths, arbitrary text or all metadata blindly.

Validate artifact_version/experimental_only, source/feature/code fingerprints, cutoff/configuration/cohort association, finite/range-valid metrics and declared AP definition. A dataset/version/code mismatch or missing file yields Unavailable/stale, never fallback numbers. DEPLOYED/DEMO may not have this ignored artifact; the absence must be explicit and must not change data mode or operational permissions. Sharing derived evidence externally still needs permission.

Panel zones:

1. **Current operational method:** deterministic six-gate rules plus descriptive recency/composite triage; no fitted model used. Do not attach recency-only experiment AUC to the composite queue score.
2. **Historical evaluation:** recency-only, logistic and histogram boosting metrics at January→July cutoffs, train/holdout size/prevalence, shared-customer limitation and 90-day observed-inactivity target. Models remain experimental.
3. **Per-customer fitted inference:** Unavailable — no saved fitted preprocessing/estimator artifacts. Do not display fabricated probabilities or refit to fill the gap. If a future separately authorized phase adds it, score the imported historical cutoff, not pretend current real-time customer risk.

Correct `ui_views.audit_validation()` stale text about no reproduced evaluation, distinguishing existing historical evidence from absent approved/live inference. No model approval status, policy hash or review payload is changed.

## Currency display boundary

Current USD aggregation is internally consistent. A read-only explanation may name Amount (USD), provided synthetic mid-rate provenance and the existing volume formula. If showing audit validation totals, bind them to the specific source/feature hash and report stale/unavailable for other releases. No source ZIP parsing on every UI rerun, raw mixed-currency sum, new exchange conversion or product monetary threshold is needed. Actual FX exposures/product ranking remain outside scope.

## Regression and acceptance criteria

All criteria are mandatory:

- Retain all 443 current IDs; new tests in report 09 pass; no failures/errors/skips in the authorized full acceptance run.
- CSV, manifest, policy, exact per-customer rating/priority/reason digest, alias key and historical outputs unchanged. Global counts remain the reviewed reference through all new filter/panel interactions.
- Known/unknown/malicious segment values, alias-safe one-to-one joins, selected-customer continuity, pagination and empty/scoped filter behavior verified.
- Product explanations match actual G4/G5/final engine outputs for all relevant states; model/segment interest cannot bypass existing restrictions or create an approval control.
- AI comparison faithfully renders validated historical artifact values and missing/stale/error states; no live fitted inference, training, binary loading, operational score/rating mutation or new bank approval claim.
- All nine routes, explicit data modes, replay Pending/reset, isolated fresh-process review persistence, stale rejection and Phase 7 responsive layout pass.
- Reports distinguish source segments from behavioral bands; current snapshots from historical features; observed inactivity from churn; historical metrics from customer inference.
- Run the complete corrected source-bound acceptance after integration using a fresh directory, compare required 443-ID baseline and review the final report. No public deployment/data publication is part of acceptance.

The full existing test suite includes a synthetic estimator-fitting reproducibility fixture. Unlike this no-training audit, the implementation validation phase must explicitly authorize that existing isolated test if running the whole suite; it does not authorize retraining real models or modifying artifacts.

## Rollback

No data contract, schema, review history or model artifact migration is proposed. Preserve a reviewed pre-8B code snapshot. If a new view/helper fails acceptance, revert only its new helper/UI/test wiring and rerun the baseline; do not delete histories, rotate aliases or restore old database files over new events. The acceptance-baseline hardening should remain unless its own tests fail. Do not automatically regenerate frozen decision references. Any unexpected decision/hash change stops integration and requires diagnosis before further work.

## Explicit exclusions

No clustering for its own sake; no learned/hybrid product model without valid targets; no new commercial product catalogue/terms; no changes to G1–G6 or approval flags; no live logistic/boosting inference without a separately authorized artifact/validation step; no transaction-level replay claim; no bank authentication/regulatory claim; no external publication without written permission.
