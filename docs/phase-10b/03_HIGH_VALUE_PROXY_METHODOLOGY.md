# Explainable high-relationship-activity value proxy

## Explicit classification

New label: **High Relationship Activity — Potential Value Review**. It is an explanatory classification, not profitability, operational eligibility or a new score. `phase10b_value.classify_activity` reuses existing `analytics.activity_band`; it never recalculates percentile ranks.

The existing original builder (`build_data.run`) sums absolute finite normalized USD qualifying transaction amounts in **[cutoff−180 days, cutoff)**, rounds volume to cents, then uses average-tie global percentile rank rounded to four decimal places. The accepted Higher activity band is **percentile >=0.8** (`analytics.activity_band`). Its original name and values remain unchanged.

The companion uses the accepted canonical **50,000-customer** population and its original key/aliases. With cutoff 2026-07-01, the observation window is **[2026-01-02, 2026-07-01)**. Source/policy/manifest and full keyed decision digest are verified before any source-derived classification is displayed; no missing/stale source silently falls back to synthetic data.

Classification inputs are the accepted global percentile, recorded USD activity and valid observation cutoff. Missing/invalid percentile, USD activity or cutoff yields **Unavailable — insufficient activity evidence**, not a positive classification. Otherwise existing Higher activity gives the new label; other valid bands give **Outside high-activity review band**. The original rank, band, customer identity, outcomes, reasons and exact operational priority are left untouched. There is no seventeenth canonical column; the new labels exist only in detached analytical frames.

## Reconciliation

| Original source-derived population | Count |
|---|---:|
| Total/global ranking denominator | 50,000 |
| Existing Higher activity (80th+) | 10,003 |
| New High Relationship Activity label | 10,003 |
| Outside review band | 39,997 |
| Unavailable evidence on accepted extract | 0 |

Counts are calculated from source-derived values, not hardcoded in runtime logic. Boundary rounding/ties explain why the inclusive >=0.8 band is not exactly 10,000. Classification totals reconcile to the original population and each positive label must correspond to the existing Higher activity band. Synthetic upsell counts are separate.

## Segment, breadth and explanation

`value_frame` reuses `analytics.portfolio_frame` and the alias-safe `segment_context` helpers, preserving every original analytic column, value/order and rank. Segment selectors filter the display only; they never rerank within Retail/SME/Corporate/NGO/NPO/Trust. Global denominators/metric cards remain 50,000 regardless of filter. Unknown/empty segment results are honest; no fabricated customer is selected.

Each source-derived explanation displays safe customer alias; recorded segment; existing activity band/global percentile; absolute historical USD activity; known product breadth/account count; observation window; ranking population and unchanged threshold; why the original percentile meets or does not meet the boundary; source/policy hashes; and unknown current-snapshot/segment effective dates.

Breadth/account count and segment are descriptive context, not new value-score factors or bank commercial eligibility. Current holdings/status are not historical predictors. The companion table is paginated in 25-row slices and sorted only for presentation by existing percentile descending then alias; original index/manager priority is not modified.

## Required limitation

**This classification identifies customers with higher historical transaction activity. It does not establish confirmed profitability, customer lifetime value or future revenue.**

Absolute turnover is not net flow, balance, bank revenue, margin or profit. Global comparisons across source segments are not economically calibrated. The raw source has some balance/income snapshot fields, but those are outside this accepted feature contract and do not justify inventing profitability, fee income, LTV or future revenue. No economic estimates or new segment-specific thresholds were added.

The original Savings cross-sell, historical experimental AI and six-gate operational decisions remain independent. A high-activity label cannot authorize a product recommendation or bypass G3/G4/G5/G6. It does not turn a restricted or already-held-product case into SUPPORTED.
