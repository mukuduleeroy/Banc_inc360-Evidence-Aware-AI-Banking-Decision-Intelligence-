# Phase 8A — product recommendation model feasibility

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Target inventory

Source schema has 64 columns; inventory and aggregate checks are in `evidence/data_audit.json` and `product_target_metadata.json`. No targets were created or fitted during this audit.

| Possible target/evidence | Exists? | Leakage/validity assessment |
| --- | --- | --- |
| Current products_held | VERIFIED snapshot | Useful for ownership suppression/gaps, not future adoption; no effective-date history |
| Current loan_types/card_types/card_schemes | VERIFIED snapshot metadata | Not dated acquisitions or offer responses; no training label for future purchase |
| Customer-product ownership changes over time | MISSING | Repeated transaction rows carry the same supplied holdings snapshot; 0 conflicting source portfolio strings per customer does not create history |
| Product acquisition/adoption timestamps | MISSING explicit fields | Cannot derive them from current ownership or last customer transaction |
| Account opening event/type | PARTIAL evidence | 98,475 accounts have consistent opening date/type; dates 2016-01-15 through 2022-01-15, all before source transaction coverage starts 2022-10-01 |
| New account opening in 2026 target windows | No positives in inspected dates | Existing openings do not overlap the required transaction observation/target design; not viable product adoption labels |
| Account type → commercial product mapping | UNVERIFIED | Source labels Fixed Deposit, Foreign Currency, Call Deposit, Savings, Current are metadata, not an approved suitability/catalogue mapping |
| Historical offers/campaign assignment | MISSING | No offered-product/time/treatment history |
| Offer acceptance/rejection/campaign response | MISSING | Transaction Status is Completed, not offer acceptance; KYC states are not product response labels |
| Approved eligibility/suitability outcomes | MISSING | Current G4/G5 checks are prototype rules, not independently labeled bank adjudications |
| Customer-product interaction history | PARTIAL | Transactions have type/currency/account links, but no verified product-offer interaction/adoption trail |
| Last service/digital interaction dates | VERIFIED timestamp-like snapshots | Do not encode product identity, offer or response; cannot substitute as supervised labels |
| Future transaction inactivity | VERIFIED constructible proxy | Relevant to historical engagement, not validated product preference/acceptance or intervention uplift |

Although account-opening metadata is real in the supplied schema, its entire date range precedes available transaction observations. Historical closed-account coverage/survivorship and product lifecycle completeness are also UNVERIFIED. It cannot rescue a defensible product recommender for the January/July 2026 design.

## Options

| Criterion | A — explainable rules/context | B — rules + separately evaluated ML rank | C — fully learned product recommender |
| --- | --- | --- | --- |
| Data availability | Current ownership and historical behavior exist | Product-ranking target missing | Adoption/offer/response/eligibility history missing |
| Technical feasibility now | High for existing Savings-only read-only context | Low for defensible product ML; possible future research after target approval | Not defensible now |
| Explainability | High: gap/rationale/gates/cutoff | Depends on validated target/model; rules must remain final authority | More difficult; historical preference is not suitability |
| Leakage risk | Controlled by current-vs-historical separation | High if snapshot holdings used as future acceptance | High without ownership history and temporal target construction |
| Banking suitability risk | Disclose prototype/segment-policy gaps; no offers | ML must never bypass G4/G5/G6 | High; scoring cannot replace bank policy |
| Effort estimate | Low–medium UI/testing work, no training | High: new labels/design/artifacts/validation | Highest: complete product lifecycle/intervention data and bank review |
| Regression impact | Limited if views-only and frozen decisions preserved | Broad model/provenance/ranking/approval tests | Broad new policy and validation contracts |
| Demo value | Strong, honest and immediately evidence-based | Mostly a research story until real labels exist | Risk of misleading claims exceeds short-term value |

## Recommendation

**CONDITIONAL GO for Option A** with existing Savings evidence and source-segment context, explicitly review-only. Segment labels may organize evidence, not invent relevance rules. Show other observed products only as current holdings until an approved catalogue/suitability mapping exists. An existing prototype SUPPORTED outcome is not verified suitability for every banking segment.

**DEFER Option B** until time-stamped product response/adoption/eligibility data and a target/holdout design exist. Do not use inactivity probability as an unvalidated proxy for product purchase probability. Even then any ML rank must remain separate unless an approved operational integration is defined and G3/G4/G5/G6 tests pass.

**NO-GO for Option C with current data.** Do not train an ownership classifier and present its accuracy as recommendation acceptance. Current ownership correlations, including regular segment/product patterns, could be memorized without predicting future adoption or causal benefit.

Future requirements: versioned catalogue; dated holdings/acquisitions/closures; offer/campaign/treatment/response records; policy eligibility outcomes; historical effective dates; sufficient positives and negatives; customer-grouped chronological evaluation; leak-free features; separate propensity versus suitability versus uplift definitions; model artifact/provenance/approval controls. No artificial labels, product terms or bank policies may substitute.
