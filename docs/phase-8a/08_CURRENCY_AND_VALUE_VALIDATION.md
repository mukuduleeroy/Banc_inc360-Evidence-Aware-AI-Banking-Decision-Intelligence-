# Phase 8A — currency and relationship-value validation

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Actual fields and conversion evidence

**VERIFIED source fields:** currency, amount, exchange_rate_per_usd, Amount (USD), rate_date, units_per_usd_mid_rate, units_per_usd_sell_rate, rate_source, account_currency and dr_cr_indicator. Currency labels are EUR, GBP, USD, ZAR and ZWG; each has 209,715 source rows. All source rate_source values are **Synthetic treasury reference rate**, not externally verified/executable bank FX quotes.

Using the supplied quote convention, `amount / exchange_rate_per_usd` reconstructs USD-equivalent value. Across all 1,048,575 rows:

- 0 missing/nonfinite/nonpositive rates; 0 invalid raw or provided USD amounts.
- Provided exchange_rate_per_usd equals provided mid-rate with maximum absolute difference **0.0**; no row uses the sell-rate value in the checked data.
- 0 invalid rate dates and 0 date mismatches against transaction_date (naive day comparison).
- 0 rows differ by **more than one cent** between provided Amount (USD) and rounded reconstructed value, allowing 1e-8 floating comparison slack. Some EUR/GBP/USD comparisons differ by one cent; this is not exact bit equality and is consistent with source/rounding precision. ZAR/ZWG rounded values match in this check.

| Currency | Rows | Difference > one cent | Maximum rounded absolute difference (USD) |
| --- | ---: | ---: | ---: |
| EUR | 209,715 | 0 | 0.01 |
| GBP | 209,715 | 0 | 0.01 |
| USD | 209,715 | 0 | 0.01 |
| ZAR | 209,715 | 0 | 0.00 |
| ZWG | 209,715 | 0 | 0.00 |

These are internal consistency checks, not independent verification of rates, transaction completeness or source authenticity. Evidence: `evidence/data_audit.json`, `product_target_metadata.json`; source ZIP hash matches the verified feature/evaluation manifests.

## What the application actually aggregates

**VERIFIED:** `build_data.run()` reads **Amount (USD)** and sums its absolute value for valid known non-fee historical events. It does not sum the raw `amount` field across currencies and does not perform a second conversion. `historical_evaluation.cohort()` uses the same supplied USD field. Transactions at/after cutoff and SERVICE FEE rows are excluded from the historical activity measure.

At cutoff 2026-07-01, the 180-day window has **315,445** qualifying rows. The supplied-USD absolute sum is **316,964,804.53**, exactly matching the canonical sum of per-customer transaction_volume_180d_usd. Reconstructed unrounded amount/rate absolute sum is **316,964,802.26046145**; the approximately **2.26954 USD** aggregate difference is consistent with summing rounded provided amounts versus unrounded conversion values. No canonical value was recalculated or changed.

All source transaction Status values are Completed in this extract. The builder's documented event definition checks type/link/date/identifier/finite amount and excludes fees; it does not independently filter settlement status. That is harmless for this observed all-Completed source but a future-ingest validation gap, not proof that all future failed/pending rows should count.

## Value and ranking semantics

`relationship_activity_percentile` is average percentile rank of each customer's 180-day absolute provided-USD activity within the observation-time cohort, rounded to four decimals. `analytics.activity_band()` merely bins that value at .4/.8. It is **not profit, revenue, balance, net cash flow, disposable income or lifetime value**.

`engine.evaluate()` uses .35 of that percentile in its illustrative composite triage score. Recency contributes .45 and a current service-issue indicator .20. There is no currency-specific ranking, FX exposure preference, segment-adjusted rank or product acceptance probability. Currency amounts become comparable through the provided USD-equivalent input; the operational rank is not calculated from mixed raw units.

Direction labels are DR/CR; the current activity proxy intentionally uses absolute volume, not net debit/credit cash flow. No product-specific monetary affordability/eligibility threshold exists. Savings rationale is a deposit-event count condition, not a validated deposit amount, salary or investment-capacity rule. Foreign Currency Account is recognized as held but is not generated as a recommendation from FOREX_PURCHASE events.

## Missing-rate and test limitations

The builder rejects nonfinite/malformed provided USD amounts. It does not inspect raw FX rate fields; if a future file retained a finite but incorrect supplied USD amount, the current builder would not detect the rate inconsistency. Canonical features also lack per-currency breakdowns/rates, so the UI cannot reconstruct source FX calculations from the aggregate alone. No raw-amount fallback should be introduced.

Existing tests cover malformed/inf USD amounts, nonnegative measures, historical windows and volume/percentile reconciliation (`test_cohort`, `test_data`, `test_evidence`, `test_analytics`). **MISSING:** a dedicated mixed-currency amount/rate fixture, rate-date mismatch, missing/zero-rate and conversion-tolerance test suite. This audit supplies read-only aggregate reconciliation, not a newly implemented ingest control.

## Recommendation

**INFERRED:** the current artifact shows correct USD normalization; a calculation rewrite is not indicated. Phase 8B may add an explanation/validated-source-check display tied to the current artifact hash and clearly synthetic reference-rate provenance. Keep existing values, ranks and gate inputs unchanged. Add focused currency-validation tests before future ingestion work. Any genuine future correction requires a separately versioned rebuild and reviewed baseline/model impacts; it must not be a silent visual-phase change.
