# Phase 8A — executive audit summary

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Decision

**CONDITIONAL GO** for a small, read-only Phase 8B: expose validated source banking segments, add analytic segment filters, explain the existing Savings discussion evidence, and display verified historical experimental metrics. **NO-GO** for live logistic/boosting inference, new segment-specific suitability policies, a learned product recommender or operational ML ranking with current artifacts/data.

## Verified baseline and strengths

- **VERIFIED:** 50,000 unique validated customer feature records; SUPPORTED 2,052, CAUTION 20, ABSTAIN 47,928. Full per-customer decision/priority/reason digest still matches the frozen reference. Source: `data_access.load_index`, `acceptance_checks.decision_fingerprint`, `evidence/data_audit.json`.
- **VERIFIED recorded baseline:** 443 passing tests, 96 gate-combination cases, zero recorded failures/errors/skips; exact JUnit and 72-file source-run fingerprints remain valid. `outputs/final_acceptance/verified_final/`, `evidence/model_and_baseline_audit.json`.
- **VERIFIED fresh audit subset:** 442 passed, 1 deliberately deselected in 35.09s, no failures/skips/pytest warnings. The excluded historical reproducibility test fits estimators, contrary to this phase's no-training restriction. This is not a fresh 443-test acceptance certificate. See report 09 and `evidence/safe_tests.xml`.
- **VERIFIED:** nine native views, unchanged Phase 7 design tokens and interactions, explicit LOCAL/DEPLOYED/DEMO modes, six-gate authority, non-actionable replay, fresh-evidence review and SQLite snapshots/events. Code: `app.py`, `ui_shell.py`, `ui_views.py`, `design_system.py`, `engine.evaluate`, `review_service.ReviewService`, `audit_store.AuditStore`.

## Findings that matter for Phase 8B

| Finding | Status | Consequence |
| --- | --- | --- |
| Source banking segments exist: Retail, SME, Corporate, NGO/NPO, Trust | VERIFIED | No clustering model is needed to reveal them |
| Segment retained in feature/index but deliberately absent from public analytics frame and Customer 360 | VERIFIED gap | Add allowlisted display metadata separately; preserve existing privacy contract |
| Behavioral recency/frequency/activity bands exist | VERIFIED | Explain them separately from source banking segments; they are not ML clusters |
| Ten ownership labels recognized; only Savings Account has a prototype suggestion policy | VERIFIED | Enum is not a bank-approved product catalogue; no invented segment/product policies |
| Existing Savings rule is segment-agnostic | VERIFIED | Non-retail SUPPORTED is prototype rule conformity, not verified segment-specific suitability |
| Historical experiment metrics are present and repeat-run fingerprints match | VERIFIED artifact evidence | A historical comparison panel is feasible without training |
| Saved fitted estimators/scalers/trees and standalone inference endpoint | MISSING | Live logistic/boosting scores cannot honestly be shown |
| Operational score is evaluated recency-only baseline | FALSE as stated | Actual operational method is six rules plus composite triage; raw-day recency-only is an offline comparator |
| Product adoption/offer-response/eligibility targets | MISSING | Learned recommendation is not defensible now |
| Account-opening fields exist, but all openings precede transaction coverage | VERIFIED limitation | They do not provide positive adoption events for the 2026 windows |
| USD conversion consistency | VERIFIED within one cent per row | No calculation rewrite is indicated; add explanation/validation tests only |
| Audit page says no reproduced evaluation exists | VERIFIED stale copy | Correct wording without changing approval status |
| Runner retains tests against Phase 7's 308 IDs, not latest 443 | VERIFIED acceptance gap | Harden baseline selection before accepting Phase 8B; do not claim current 443 have been removed |

## Source segment population

| Segment | Customers | SUPPORTED | CAUTION | ABSTAIN |
| --- | ---: | ---: | ---: | ---: |
| Corporate | 2,500 | 126 | 0 | 2,374 |
| NGO/NPO | 2,500 | 123 | 3 | 2,374 |
| Retail | 40,000 | 1,517 | 15 | 38,468 |
| SME | 2,500 | 150 | 2 | 2,348 |
| Trust | 2,500 | 136 | 0 | 2,364 |

These are aggregate observations, not bank suitability classifications. `build_data.run()` carries `customer_segment` from the source snapshot, not from a classifier; no effective-date history exists.

## Critical protections and scope

Keep `engine.py`, `evidence.py`, `data_access.py`, `build_data.py`, `replay.py`, `review_service.py`, `audit_store.py`, `historical_evaluation.py`, canonical CSV/manifest and historical outputs unchanged for the recommended 8B scope. New display helpers must not change gate inputs, priority, reasons, dataset/policy hashes or review payloads. A model panel must never imply registered/approved model action.

The original data contains identifiers and personal/financial fields; source rates explicitly say Synthetic treasury reference rate, but that does not certify that all customer information is synthetic or public-safe. Competition section 11 restrictions remain; no written external-release approval was verified (`docs/PHASE_6_DEPLOYMENT_AUDIT.md`). No deployment/publication occurred.

Integrity verification found **no changes to application sources or 190 existing data/model/database/acceptance outputs**; alias key unchanged. Evidence: `evidence/integrity_verification.json`. Database records were not inspected through a write-capable connection; test-only storage was isolated. Full specification: report 10; feature classification and approval conditions: report 11.

## Report index

- [01_EXECUTIVE_AUDIT_SUMMARY.md](01_EXECUTIVE_AUDIT_SUMMARY.md)
- [02_ARCHITECTURE_AND_DATA_FLOW.md](02_ARCHITECTURE_AND_DATA_FLOW.md)
- [03_CUSTOMER_SEGMENTATION_AUDIT.md](03_CUSTOMER_SEGMENTATION_AUDIT.md)
- [04_PRODUCT_OPPORTUNITY_AUDIT.md](04_PRODUCT_OPPORTUNITY_AUDIT.md)
- [05_AI_MODEL_AND_TRAINING_AUDIT.md](05_AI_MODEL_AND_TRAINING_AUDIT.md)
- [06_RECOMMENDATION_MODEL_FEASIBILITY.md](06_RECOMMENDATION_MODEL_FEASIBILITY.md)
- [07_SIX_GATE_INTEGRITY_AUDIT.md](07_SIX_GATE_INTEGRITY_AUDIT.md)
- [08_CURRENCY_AND_VALUE_VALIDATION.md](08_CURRENCY_AND_VALUE_VALIDATION.md)
- [09_REGRESSION_AND_TEST_GAP_REPORT.md](09_REGRESSION_AND_TEST_GAP_REPORT.md)
- [10_PHASE_8B_IMPLEMENTATION_SPEC.md](10_PHASE_8B_IMPLEMENTATION_SPEC.md)
- [11_FINAL_RECOMMENDATION.md](11_FINAL_RECOMMENDATION.md)
