# Phase 2 — real-data queue reconciliation

Measured November 16, 2026 (Africa/Harare), using the actual `outputs/customer_features.csv`. No synthetic scenario contributes to these counts. Evidence: `outputs/phase2/queue_comparison.json`; source rebuild comparison: `outputs/phase2/input_integrity_verification/reconciliation.json`.

## Population accounting

| Measure | Actual result |
|---|---:|
| Input customer rows | 50,000 |
| Evaluated unique customers | 50,000 |
| Quarantined missing/duplicate/conflicting identity rows | 0 |
| Invalid-evidence cases retained as ABSTAIN | 0 |
| SUPPORTED | 2,052 |
| CAUTION | 20 |
| ABSTAIN | 47,928 |
| Actionable staff-review queue | 2,052 |
| Default displayed supported page | 25 |
| Supported pages at 25 per page | 83; final page has 2 cases |
| Distinct real presentation aliases | 50,000 |

Reconciliation: **2,052 + 20 + 47,928 = 50,000**, and **evaluated + quarantined = input rows**. “Invalid” is not a synonym for ABSTAIN: valid evidence can correctly show restrictions, an existing product or insufficient history. No malformed row was dropped to improve the supported count.

## Before and after

The reference engine was loaded from audited local Git commit **`01b2729`**. The comparison uses each real customer's historical/current evidence for both versions and reports aggregate results only.

| Behavior | Phase 1 | Phase 2 |
|---|---|---|
| Evaluated population for reconciliation | 50,000 | 50,000 |
| Permission distribution | SUPPORTED 2,052; CAUTION 20; ABSTAIN 47,928 | Same |
| Changed per-customer permission outcomes | — | **0** |
| Real sales queue | Scanned only first 1,500 pre-ranked rows; all were ABSTAIN; **0 supported shown** | Validates/evaluates complete population; **2,052 supported reachable** |
| Display capacity | Could hide supported customers before eligibility | Applied only after eligibility and lane/alias filtering |
| Identity | 1,000 colliding last-three-digit suffixes | 50,000 checked-unique keyed aliases |

Supported counts are calculated from the actual index, not hardcoded as 2,052. No gate was weakened to create cases. The fix is discovery/completeness, not changed banking eligibility. CAUTION and ABSTAIN remain investigation lanes, never actionable sales rows.

## Deterministic selection and caching

Sort key: **exact composite priority descending, alias ascending**. Priority remains 45% capped historical recency, 35% historical activity percentile and 20% current snapshot service issue. It is an illustrative present-day triage score, not a historical prediction, profitability estimate or uplift measure. Display rounds priority to three decimals; ordering uses the exact score.

The dataset, manifest, policy/code fingerprint and persistent alias key determine an index. Same inputs produce the same mapping, counts, ties and pages, regardless of input row ordering. The alias key is private local configuration; changing it changes aliases and tie order by design. Hash collisions are checked and fail the import rather than merging customers.

Cold index evaluation measured **7.09 seconds**; a same-process cached load measured **0.008 seconds**, returning the same immutable index. These are single local measurements, not a benchmark/SLA. Cache entries are keyed by actual content bytes, manifest bytes, key and policy fingerprint, not path/mtime alone. Tests prove invalidation for changed dataset, policy and manifest. Tables/derived count dictionaries do not expose mutable cached decision containers.

Filters never reduce the population used for the global counters. SUPPORTED filtering precedes pagination. Page size is 25 or 50. The customer selected on a page opens a passport with the same alias and evaluation path. An empty filter is explained; any displayed fallback passport is explicitly identified as unfiltered inspection, not a queue match.

## Reproduction

Existing verified artifacts:

```sh
.venv/bin/python scripts/compare_phase2.py --features outputs/customer_features.csv --out outputs/phase2/queue_comparison.json --baseline-ref 01b2729
.venv/bin/python -m pytest tests/test_real_data.py tests/test_queue.py -v
.venv/bin/python scripts/verify_ui.py
```

For a fresh source verification, choose a **new output directory**:

```sh
.venv/bin/python scripts/reconcile_phase2.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --features outputs/customer_features.csv --out outputs/phase2/recheck-new
```

The source script writes a separate candidate. If it differs from canonical data, it records the comparison and does not replace or attest the canonical CSV. Review the changes and obtain explicit approval before any separate canonical replacement. If identical, it can create the matching missing manifest; it refuses to overwrite a different existing manifest. The full source/feature hash checks are local provenance controls, not bank-signed attestation.

Canonical SHA-256: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`, unchanged from Phase 1. Final runtime policy fingerprint and timing are recorded in `queue_comparison.json`; the source-rebuild report also retains its observed fingerprint/timing at that execution point.
