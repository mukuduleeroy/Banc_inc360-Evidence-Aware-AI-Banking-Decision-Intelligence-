# Phase 8A — customer segmentation audit

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Source and membership

**VERIFIED:** source `customer_segment` is carried into `build_data.run()` state as `segment`, then into the canonical `customer_segment` feature and `DecisionRecord.values`. It is **source-provided**, not predicted, clustered, manually assigned through the UI or inferred from balances/turnover. The builder retains an observed snapshot value, without effective-date history. This is current supplied classification, not reconstructed historical membership.

Source-to-feature aggregate checks found **0 mismatches** and **0 customers with conflicting source segment strings**. Labels are literal: Corporate, NGO/NPO, Retail, SME, Trust. Evidence: `evidence/data_audit.json`; code `build_data.run`, `data_access.FEATURE_COLUMNS/build_index`.

| Segment | Customers | SUPPORTED | CAUTION | ABSTAIN |
| --- | ---: | ---: | ---: | ---: |
| Corporate | 2,500 | 126 | 0 | 2,374 |
| NGO/NPO | 2,500 | 123 | 3 | 2,374 |
| Retail | 40,000 | 1,517 | 15 | 38,468 |
| SME | 2,500 | 150 | 2 | 2,348 |
| Trust | 2,500 | 136 | 0 | 2,364 |

## Capability classification

| Requested capability | Classification | Evidence |
| --- | --- | --- |
| Banking segment membership in data/index | IMPLEMENTED / VERIFIED | Source field and 17-column feature contract |
| Traceable source versus inferred membership | PARTIALLY IMPLEMENTED | Source lineage known in builder; no UI membership explanation/effective date |
| Banking segment in Customer 360 | NOT IMPLEMENTED | `ui_views.customer_360` displays status/KYC/holdings and historical measures, not segment |
| Banking segment dashboard filters | NOT IMPLEMENTED | Shared analytics filter is outcome; relationship Activity segment is behavioral |
| Segment-specific transaction analysis | NOT IMPLEMENTED | No source-segment UI grouping or transaction drilldown; historical aggregates exist |
| Segment-specific value/inactivity/product views | NOT IMPLEMENTED | No banking-segment filter/group computation in these views |
| Recency/frequency/activity behavioral grouping | IMPLEMENTED / VERIFIED | `analytics.recency_band/frequency_band/activity_band` and corresponding filters |
| Learned clustering or manual reassignment | NOT IMPLEMENTED | No estimator/cluster artifact or assignment UI |
| Banking segment historical effective dates | UNVERIFIED | No such field/history identified |
| Bank-approved taxonomy interpretation/eligibility meaning | UNVERIFIED | Literal source labels do not establish commercial policy |

**UNVERIFIED assignment rationale:** the field identifies the supplied membership, but no bank criteria explaining why a particular customer was assigned that label were found. A future source-origin explanation must not invent a financial or regulatory classification rationale.

## Behavioral grouping is different

`analytics.recency_band`: 0–30, 31–60, 61–90, >90 days, plus Unavailable. `frequency_band`: 0–1, 2–3, 4+ events, plus Unavailable. `activity_band`: lower <40th, middle 40th–<80th, higher ≥80th percentile, plus Unavailable. These are rule-derived descriptions, not learned customer clusters or comprehensive RFM segmentation. `relationship_activity_percentile` is a full observation-cohort volume rank, not a within-banking-segment rank.

**VERIFIED presentation risk:** `ui_views.relationship_value` labels its behavioral selector Activity segment. A user may confuse that with Retail/SME/etc.; the code itself does not map one to the other. Rename the future label to Observed activity band while retaining its existing widget key/values and formulas.

## Privacy and integration boundary

`analytics._frame()` explicitly excludes raw `customer_segment`; `tests/test_analytics.test_privacy_safe_frame_is_detached_from_cache` asserts that exclusion. The raw source field is unvalidated free text from the UI perspective; `row_case()` does not use or validate it. Do not weaken the privacy test or add arbitrary raw strings to the existing frame.

**INFERRED feasible addition:** a separate pure helper can read existing index values internally and return only alias + allowlisted banking label + source/current-snapshot explanation. Unknown/missing/unrecognized labels must display Unknown, not be guessed from customer identity or financial activity. Separate sidecar metadata can join on checked unique aliases without modifying the canonical feature contract, existing analytics frame, engine inputs or priorities.

Filtering should restrict displayed analytic rows only. Keep full-population KPIs clearly labeled, preserve shared customer selection, reset pagination through the existing context mechanism and retain original row order. Do not recalculate the operational percentile within a selected segment or use the source segment as a historical predictor.

## Recommendation

**INFERRED:** no new clustering model is necessary for the requested near-term story. Existing source banking labels and interpretable behavioral indicators are sufficient for readable read-only comparisons. Cluster learning without an operational question, validation target or stable historical feature contract would add model risk, artifacts and acceptance burden without filling the actual display/filter gap. Defer clustering unless a distinct use case and evaluation design are approved.
