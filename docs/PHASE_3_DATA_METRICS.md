# Phase 3 — actual data metrics and definitions

Measured November 16, 2026 (Africa/Harare). Reproduce with:

```sh
.venv/bin/python scripts/report_phase3_metrics.py
```

The script reads the existing validated feature CSV and authoritative Phase 2 index, emitting only aggregates to `outputs/phase3/metrics.json`. No customer records or synthetic scenarios contribute to the real-data numbers below.

## Provenance and decision reconciliation

Historical cutoff: **July 1, 2026**, exclusive. Feature/data fingerprint: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. The canonical CSV and its manifest are unchanged from Phase 2; no new source build or CSV replacement was required in this interface phase. Matching Phase 2 source-rebuild evidence records 1,048,575 original transactions. The Audit view displays that source count only when the report's before/after feature hashes match the loaded dataset.

| Measure | Actual count |
|---|---:|
| Input feature rows | 50,000 |
| Evaluated unique customers | 50,000 |
| Quarantined identities | 0 |
| Invalid typed-evidence cases | 0 |
| SUPPORTED / actionable staff review | 2,052 |
| CAUTION / investigation | 20 |
| ABSTAIN / no sales action | 47,928 |

**2,052 + 20 + 47,928 = 50,000.** The actionable queue has 83 pages at the default 25 rows per page, with two cases on the last page. It never truncates eligibility evaluation at 1,500 candidates. “Valid typed evidence” is not a claim of suitability, current status freshness or profitability: valid evidence often correctly results in ABSTAIN.

## Observed engagement

Recency is the integer number of days from the observation cutoff to the last valid qualifying non-fee transaction strictly before cutoff. Frequency counts qualifying events in the preceding 180 or 90 days. The 180-day lower boundary is January 2, 2026; the 90-day lower boundary is April 2, 2026, both inclusive. Source timestamps are timezone-naive. These are observations, **not predicted future inactivity** and not the same as the current Dormant account status.

| Observed recency band | Customers |
|---|---:|
| 0–30 days | 16,459 |
| 31–60 days | 3,474 |
| 61–90 days | 3,333 |
| >90 days | 26,734 |

Median observed recency: **107 days**. Median qualifying events over 180 days: **8**.

| Historical event coverage | Customers |
|---|---:|
| 0–1 events / 180d | 17,391 |
| 2–3 events / 180d | 1,154 |
| 4+ events / 180d | 31,455 |

These descriptive coverage bands explain the existing G2 thresholds; they do not independently grant permission or change the engine policy. No future inactivity labels, training/holdout model experiment or reproduced ROC/PR metric was added. The UI shows no invented model accuracy or probabilities.

## Relationship activity proxy

Existing proxy: percentile rank of **the preceding 180-day sum of absolute valid non-fee transaction amounts**, calculated over the observation-time cohort with average ranks for ties and rounded to four decimals. The UI uses the stored validated percentile. Observed volume is labeled in USD only where the supplied field supports it; it is **not balance, deposits held, revenue, profit or customer lifetime value**.

| Descriptive activity segment | Customers |
|---|---:|
| Lower: percentile <0.4 | 19,997 |
| Middle: 0.4 ≤ percentile <0.8 | 20,000 |
| Higher: percentile ≥0.8 | 10,003 |

Median activity percentile: **0.5**. Ties/rounding mean these display bands are not forced to contain exactly 40%/40%/20%. They are not new banking eligibility thresholds.

Current recorded product breadth:

| Products recorded | Customers |
|---|---:|
| 1 | 9,719 |
| 2 | 25,008 |
| 3 | 12,494 |
| 4 | 2,779 |

Median breadth is **2**. Account/product breadth comes from the current source snapshot and is explicitly separated from historical predictors. Snapshot effective dates are unknown; no longitudinal product-adoption claim is supported.

## Savings opportunities and suppression

| Evidence category | Customers |
|---|---:|
| Savings Account gap recorded | 40,000 |
| Savings Account already held | 10,000 |
| Unknown ownership in this supplied dataset | 0 |
| Gap plus recorded behavioural rationale | 12,517 |
| Engine SUPPORTED staff-review candidates | 2,052 |

A gap means only that the known portfolio does not record Savings Account. Recorded rationale derives from repeated qualifying cash deposits, not verified salary or propensity. Only the final authoritative engine SUPPORTED cases appear in the staff-review context. Already-held cases and unknown ownership never become offers. CAUTION/ABSTAIN remain non-actionable investigations. No communication or financial approval is connected.

Current KYC snapshots: **16,667 Verified, 16,666 Pending, 16,667 Review Due**. Current account snapshots: **30,039 Active, 9,961 Frozen, 10,000 Dormant**. These values screen current proposals and must not be described as historical KYC/account state.

## Reasons on abstaining passports

These are non-pass reason codes on customers whose final outcome is ABSTAIN; multiple codes may describe one customer.

| Engine reason code | Customers |
|---|---:|
| CURRENT_RESTRICTION | 39,928 |
| NO_BEHAVIOURAL_EVIDENCE | 27,483 |
| HISTORY_INSUFFICIENT | 17,391 |
| PRODUCT_ALREADY_HELD | 10,000 |
| HISTORY_BORDERLINE | 1,134 |

A borderline-history code is a caution alongside some other blocking gate, not a standalone abstention rule. These overlapping counts must not be summed as unique customers. The remaining 20 overall CAUTION cases are not included in this ABSTAIN-only reason chart.

## Filters, simulations and evidence limits

Executive population KPIs are unfiltered. The explicitly named analytics outcome filter applies to analytical charts/tables; manager lanes have separate controls. Counts on a filtered chart should reconcile to its selected population, not automatically to the full 50,000. Customer alias search changes the shared customer workspace rather than redefining the portfolio.

Replay overrides do not feed these metrics or the index. In synthetic mode, real portfolio analysis is suspended and the controlled demonstration is separately labeled. Missing/invalid features are unavailable or fail closed; they are not filled with example banking records. Local manifests/report artifacts are trusted local evidence, not signed external banking attestations. No profitability, model performance, uplift or future financial result is inferred.
