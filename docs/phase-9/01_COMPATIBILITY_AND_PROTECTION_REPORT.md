# Phase 9 compatibility and protection report

Date: 2026-11-19 (Africa/Harare).
Status: **GO — baseline clarification received and recorded; additive companion implementation authorized.**

## Verified baseline

Repository: `/Users/user/Documents/BancInc360_Final`. The earlier Downloads workspace path no longer exists. Current Git HEAD is `6d06878a992980971f468535e8486b5eb577ade3`, rather than the historical `ab02f09bc78d7e809ee22cb25f0819680151f16d`. This revision difference is not source drift: the actual working source exactly matches all 79 files in the completed Phase 8B run manifest.

Read the Phase 8B final acceptance report, acceptance JSON, source/run manifest, protected-file checkpoint and source interfaces. Read-only verification performed:

- `acceptance_checks.verify_local_baseline()` passed: 50,000 customers; 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN; no invalid or quarantined customer cases.
- `acceptance_checks.verify_run_manifest(...)` passed against `outputs/final_acceptance/phase-8b-final/tests.xml` and its original run manifest. All 79 current source hashes match; exact JUnit bytes match the completed run receipt.
- All 24 protected file hashes and all 49 pre-existing database/sidecar hashes in `outputs/phase8b/checkpoint.json` still match.
- The prior receipt records 504 tests passed, no failures/errors/skips and 96 gate-combination cases. These are verified prior results; the full suite was not rerun during this stopped Phase 9 inspection.

| Artifact | Verified SHA-256 |
|---|---|
| Canonical CSV | `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993` |
| Canonical manifest | `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c` |
| Policy | `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae` |
| Customer decision/priority/reason digest | `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3` |

## Blocking discrepancy and exact locations

Phase 9 section 1 specifies a **17-column canonical customer-feature contract**. The accepted canonical CSV header and `data_access.FEATURE_COLUMNS` both contain **16 columns**, with exactly the same names and order. The CSV has the expected accepted hash; no column has been lost since acceptance.

Actual contract:

1. `customer_id`
2. `qualifying_events_180d`
3. `events_90d`
4. `recency_days`
5. `transaction_volume_180d_usd`
6. `deposit_events_180d`
7. `product_gap`
8. `behavioural_reason`
9. `products_held`
10. `customer_status`
11. `account_status`
12. `kyc_status`
13. `service_issue`
14. `customer_segment`
15. `account_count`
16. `relationship_activity_percentile`

The same incorrect 17-column description appears in prior Phase 8A/8B reports, including `docs/phase-8a/02_ARCHITECTURE_AND_DATA_FLOW.md`, `docs/phase-8a/10_PHASE_8B_IMPLEMENTATION_SPEC.md` and `docs/phase-8b/05_FINAL_ACCEPTANCE.md`. Those descriptions were inaccurate; this inspection did not edit historical reports or receipts.

The explicit Phase 9 baseline rule says: “If any baseline cannot be verified, report the discrepancy and stop rather than silently establishing a new baseline.” Therefore implementation is stopped. No seventeenth field will be invented, and the accepted CSV/feature contract will not be modified to fit the incorrect prose.

Smallest safe clarification: confirm that Phase 9 must preserve and use the actual accepted **16-column** contract, treating the historical 17-column wording as a documentation error. This would require no canonical-data change, policy change or regenerated baseline. If a seventeenth field is intended, its exact definition and compatibility requirements must first be supplied; adding it is outside this additive implementation's protections.

## Inspected reusable components

These are potential interfaces, not newly implemented capabilities:

- `build_data.run(path, out, cutoff)` accepts a local ZIP containing exactly one CSV, writes a feature CSV, source audit and adjacent manifest to a new output directory, and refuses an existing feature output. A Phase 9 CSV adapter could stage a validated CSV in a generated internal ZIP and call this unchanged builder. This path must be fully validated after the contract discrepancy is resolved.
- `build_data.KNOWN_TYPES` supplies the existing transaction-type allowlist. The builder parses dates with pandas mixed-format, day-first, coercing invalid dates; an adapter must report those problems and fail closed before activation.
- `build_data.run` classifies known non-service-fee events, uses observations strictly before the cutoff, calculates 180-/90-day evidence, deposit counts and existing full-cohort relationship percentile, and preserves source-provided segment metadata.
- Currency input to the builder is already normalized `Amount (USD)`. It does not implement a general raw-currency conversion interface. Phase 9 must not invent FX rates or claim arbitrary-currency support. An explicit compatible USD input contract and its provenance/validation policy would need to be documented and tested.
- `data_access.load_index(path, key=...)`, `row_case`, `provenance_issues`, index table/passport methods and the existing `engine.evaluate` provide source-bound validation and the authoritative six-gate decisions. Explicit isolated Phase 9 key/storage would avoid creation or modification of the accepted alias key.
- `acceptance_checks.decision_fingerprint` and `verify_local_baseline` support exact decision invariance checks without exporting raw identifiers.
- Existing analytics and segment helpers may be reused read-only; no current dashboard loader needs modification for a companion preview.

## Builder input contract found during inspection

`build_data.run` reads these 14 source fields as strings:

`Customer ID`, `Account ID`, `account_customer_id`, `Transaction ID`, `transaction_date`, `Type`, `Amount (USD)`, `dr_cr_indicator`, `products_held`, `customer_status`, `account_status`, `kyc_status`, `service_reasons`, `customer_segment`.

Observed behavior relevant to a future adapter:

- Cutoff is required, a valid timezone-naive date at midnight; historical transactions are strictly earlier than it.
- Identifiers use existing `evidence.identifier`; customer and account-owner identifiers must agree.
- Repeated customers/accounts across transactions are valid. Transaction IDs drive deduplication; the existing builder tracks historical and post-cutoff deduplication separately. A future adapter must detect conflicting duplicates explicitly rather than count every repeated customer as invalid.
- Known types: SERVICE FEE, FOREX_PURCHASE, CASH_DEPOSIT, POS_PURCHASE, ATM_WITHDRAWAL, BILL_PAYMENT. Historical qualifying events exclude SERVICE FEE.
- Amounts must be finite; activity volume sums absolute USD values and rounds to two decimals. No new conversion formula is warranted.
- Product holdings are pipe-separated source evidence. Blank ownership remains unknown; it is not fabricated as an empty product portfolio.
- Customer/account/KYC states use existing allowlists and normalization. Unknown values remain unknown and prevent unsupported eligibility; no default KYC is supplied.
- Source segment is metadata, not a new predictor or eligibility threshold.
- Invalid identifiers/links/dates/amounts/types are audited and skipped by the builder; historical ownership-conflict customers and post-cutoff-only customers are excluded. A future activation validator must report and reconcile those cases, not silently approve incomplete processing.
- Current snapshot evidence is not reconstructed historical eligibility. Snapshot effective dates remain unknown.

No new public input schema, numerical conversion, upload parser or activation policy has been established in this stopped inspection.

## Protection list and possible integration

Keep all 79 accepted source files intact, all 24 protected artifacts intact, and all accepted canonical sources/manifests/evaluation outputs/alias key/audit histories/receipts untouched. The checkpoint already identifies exact files and hashes; it remains unchanged.

A separate local Streamlit companion entry point titled **Dataset Ingestion & Refresh**, backed by a new isolated Phase 9 package and private snapshot registry, appears to be the smallest integration surface. It can offer a dedicated preview instead of changing accepted dashboard loading or navigation. Activation would affect only that companion's selection; return to baseline would select the original accepted dataset read-only. This is a proposed direction only, not a verified implemented workflow.

Further design verification, input limits, reconciliation, immutable snapshots, registry recovery, synthetic fixtures and UI/security tests must occur only after resolving the contract discrepancy. No protected application edit is currently proposed.

## Initial inspection status (superseded by authorization below)

Only this new inspection report was written. No application code, tests, canonical data, aliases, historical reports/receipts or database histories were changed. No upload was processed, snapshot created/activated, model trained, network data transmission performed, public deployment attempted or remote changes pushed.

Stage A is blocked pending the precise contract clarification above. Stages B onward and the remaining implementation/acceptance deliverables are intentionally not started under the user's explicit stop rule. Phase 9 is **NO-GO for implementation at this checkpoint**; the accepted Phase 8B system remains verified and intact.

## Clarification and authorization received — 2026-11-19

The user explicitly confirmed that the accepted **16-column** contract is authoritative and authorized Phase 9 to proceed. All earlier 17-column references are documentation errors. Preserve names, order, types and semantics exactly; add no field and do not change the existing builder. Historical Phase 8B reports/receipts remain untouched. The stop described above is resolved solely by this explicit clarification.

Reverified the 79 accepted source hashes, canonical decision/hash baseline and protected artifacts before implementation. New private checkpoint: `outputs/phase9/checkpoint.json`; source-only rollback archive: `outputs/phase9/rollback-source.zip`. All existing SQLite/sidecar files were hashed before any feature work. Current source HEAD is recorded in that checkpoint.

Safe chosen path: entirely new root-level `phase9_*.py` modules and new tests/documentation, with a separate local Streamlit companion. No accepted source file or navigation entry changes. This deliberately keeps all new Python runtime code inside the existing source-snapshot coverage. The unchanged builder will receive a generated internal single-CSV ZIP in a fresh private snapshot directory; input CSV remains USD-normalized. Snapshot activation is confined to the companion preview and never changes the accepted application's loader/environment.

## Completed implementation checkpoint

The authorized additive path was implemented without modifying any accepted application source. Full acceptance passed 574 tests: all 504 original cases retained plus 70 new, including the original 96 gate combinations. All 79 accepted source hashes, 24 protected artifact hashes and 55 Phase 9 pre-existing database/sidecar hashes remained unchanged. The companion real-browser upload/validate/process/reconcile/preview/activate/rollback/reject sequence passed; original nine-view/replay/review-restart browser acceptance also passed. No further baseline discrepancy was discovered.

Final status: **PASS — controlled local demo ready**. See 02–08 for exact implementation, source limits, evidence, commands and limitations. The initial NO-GO above records the earlier resolved column-count stop, not the final acceptance result.
