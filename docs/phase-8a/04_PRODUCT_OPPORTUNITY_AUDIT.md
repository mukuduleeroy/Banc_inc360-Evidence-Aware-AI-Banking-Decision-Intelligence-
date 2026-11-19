# Phase 8A — product opportunity intelligence audit

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Recognized holdings versus recommendations

**VERIFIED:** `evidence.PRODUCT_LABELS` recognizes ten ownership strings: Call Deposit, Credit Card, Current Account, Digital Banking, Fixed Deposit, Foreign Currency Account, Mortgage, Personal Loan, SME Working Capital, Savings Account. All ten occur in the supplied feature portfolios. This is an input-normalization enum, **not an approved commercial catalogue**, product-terms source or segment-policy map.

**VERIFIED:** only **Savings Account** has a prototype suggestion rule. `Case.proposed_product` defaults to it; `engine.evaluate()` G5 rejects other proposed products as UNSUPPORTED_PRODUCT. Insurance is not a recognized supported recommendation. No new product names, terms or eligibility criteria are inferred here.

## Actual capability matrix

| Capability | Status | Evidence |
| --- | --- | --- |
| Existing ownership detection and malformed/unknown handling | IMPLEMENTED / VERIFIED | `evidence.holdings`; invalid ownership does not become an empty portfolio |
| Savings gap detection and consistency check | IMPLEMENTED / VERIFIED | builder gap, `data_access.row_case`, G5 |
| Transaction behavior support | IMPLEMENTED / VERIFIED | At least two historical CASH_DEPOSIT events produce recorded rationale |
| KYC/account/customer restrictions | IMPLEMENTED / VERIFIED | G4; current snapshots have unknown effective dates |
| Product-specific G5 evidence | IMPLEMENTED / VERIFIED for Savings only | Supported label, not already held, usable ownership/rationale |
| Relationship-value consideration | PARTIALLY IMPLEMENTED | Volume percentile contributes .35 to generic triage; not Savings acceptance/suitability modeling |
| Foreign-currency product relevance | NOT IMPLEMENTED | Foreign Currency Account can be recognized as held; no FX event/currency rule creates its opportunity |
| Ranking | IMPLEMENTED / VERIFIED generic triage | .45 capped recency + .35 activity percentile + .20 snapshot service issue; no product acceptance probability |
| Explanations/provenance | IMPLEMENTED / VERIFIED at feature level | rationale, six gate reasons, data/policy/cutoff, snapshots/references |
| Segment-to-product suitability mapping | NOT IMPLEMENTED / MISSING policy | customer_segment is not a Case eligibility input |
| Bank-approved product catalogue/terms | MISSING | No authoritative bank criteria/configuration artifact found |
| Historical product offers/adoption outcome model | NOT IMPLEMENTED / MISSING labels | Report 06 |
| Offer/contact execution | NOT IMPLEMENTED by design | SUPPORTED is staff-review eligibility only |

## Aggregate end-to-end trace of the existing Savings opportunity

No customer-level profile is exported. This traces one actual product opportunity type across the full authorized population:

1. Original `products_held` snapshot strings and pre-cutoff non-fee events enter `build_data.run`. CASH_DEPOSIT count ≥2 records the deposit rationale; it does not prove salary, disposable income or interest.
2. Canonical features contain **40,000** recorded Savings gaps; **12,517** combine a gap with recorded deposit rationale. Holdings are known/parseable for the audited artifact; 10,000 already hold Savings.
3. `row_case()` validates counts and ownership/gap consistency. `evaluate()` applies all six gates; G2 sufficiency, G4 restrictions and G5 relevance may still withhold a candidate.
4. Complete index output is **2,052 SUPPORTED**, not 12,517 approved offers. `ui_views.product_opportunities()` defaults to supported staff review; gap-only views explicitly warn they are not offers.
5. `ui_components.paginated()` retains the current index ordering unless a declared descriptive sort is used. A selected alias opens the authoritative Passport, which shows reasons and source/policy/cutoff evidence.
6. `ReviewService` independently reloads current evidence before a local review, rejects stale/simulated/non-supported approval and persists actor/reason/snapshot only. No communication or bank authorization follows.

Supporting source paths: `build_data.py`, `data_access.py`, `engine.py`, `analytics.py`, `ui_views.product_opportunities`, `ui_components.passport_body`, `review_service.py`, `evidence_trace.py`. Aggregate measurements: `evidence/data_audit.json`.

## Segment/product matrix — current logic, not new bank policy

| Customer segment | Product category | Existing logic | Supporting evidence | Eligibility controls | G5 integration | Missing capability |
| --- | --- | --- | --- | --- | --- | --- |
| Corporate | Savings Account discussion | Same segment-agnostic prototype rule | 2,500 recorded gaps; 760 gaps with deposit rationale | Existing G1–G6; 126 SUPPORTED | Known ownership/gap + rationale; no segment policy | Bank-approved segment suitability and terms missing |
| NGO/NPO | Savings Account discussion | Same segment-agnostic prototype rule | 2,500 recorded gaps; 764 gaps with deposit rationale | Existing G1–G6; 123 SUPPORTED | Known ownership/gap + rationale; no segment policy | Bank-approved segment suitability and terms missing |
| Retail | Savings Account discussion | Same segment-agnostic prototype rule | 30,000 recorded gaps; 9,419 gaps with deposit rationale | Existing G1–G6; 1,517 SUPPORTED | Known ownership/gap + rationale; no segment policy | Bank-approved segment suitability and terms missing |
| SME | Savings Account discussion | Same segment-agnostic prototype rule | 2,500 recorded gaps; 777 gaps with deposit rationale | Existing G1–G6; 150 SUPPORTED | Known ownership/gap + rationale; no segment policy | Bank-approved segment suitability and terms missing |
| Trust | Savings Account discussion | Same segment-agnostic prototype rule | 2,500 recorded gaps; 797 gaps with deposit rationale | Existing G1–G6; 136 SUPPORTED | Known ownership/gap + rationale; no segment policy | Bank-approved segment suitability and terms missing |

The non-retail counts show that the existing rule is segment-agnostic. They **do not verify that a Corporate/Trust/NGO Savings discussion is commercially suitable**. A future segment panel must disclose missing segment-specific policy without silently changing existing engine results. It must not present a literal source label as product eligibility.

## Safest Phase 8B interface

**INFERRED feasible:** read-only segment filters, known holdings/gap/rationale context, explicit G4/G5/final status, suppression reasons and original provenance. Reuse `index.passport(alias)`; do not duplicate suitability logic in a new recommender. Other observed product labels may be shown only as ownership metadata, with no suggestion score, terms or action until approved rules exist. Keep segment-specific policy Unavailable; no synthetic catalogue or fabricated production recommendation engine.
