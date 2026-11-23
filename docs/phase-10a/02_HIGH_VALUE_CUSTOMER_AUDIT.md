# High-value customer investigation

**Verdict: PARTIAL.** Higher observed activity is explicitly identified and explainable; confirmed commercial high value is not.

## Exact implemented definition

`build_data.run` (`build_data.py:79`–91) forms qualifying transactions strictly before the observation cutoff, counts 180-/90-day activity, sums **absolute** finite normalized USD transaction amounts in the preceding 180 days, rounds volume to cents and computes:

`relationship_activity_percentile = round(rank(volume_180d_usd, method='average', pct=True), 4)`

This is a global cohort percentile, not a profit margin, balance, deposit balance, net flow, income, customer lifetime value or weighted relationship-value score. Absolute sums can count turnover in both directions; they do not measure the bank's economic return. Frequency and recency are separately displayed but are not additional inputs to this percentile.

`analytics.activity_band` (`analytics.py:28`) classifies percentile <0.4 as Lower activity, [0.4,0.8) as Middle and >=0.8 as Higher. Current account count and known product breadth are context (`analytics._frame`, lines 41–48), not terms in a value formula. The operational composite priority also includes activity percentile, but its recency/service weighting is triage, not commercial value.

Read-only current counts: **10,003 Higher**, **20,000 Middle**, **19,997 Lower**; the slight top-band difference from exactly 20% follows rounded ranks/ties and the inclusive 0.8 boundary. No `HIGH_VALUE` classification, value threshold, value target/model or bank-approved commercial definition was found.

## Interface and reproducibility

`ui_views.relationship_value` (`ui_views.py:106`–115) displays the formula and explicit non-profitability disclaimer; sorts by percentile descending then alias; filters by source banking segment, observed activity band and existing outcome; retains global percentiles. `customer_360` (line 58) exposes selected activity, volume and current breadth/account context and explains their meaning.

Reproduce without inventing a customer:

1. Use the accepted canonical dataset; source SHA is recorded in 08.
2. Relationship Value Intelligence → Banking segment All → analytics outcome ALL → Observed activity band Higher activity (80th+).
3. The first displayed row is the highest available activity percentile, tie-broken by alias; use Inspect/Open Customer 360 to read its recorded volume/percentile and context.
4. Explain: “This is one of the highest-activity observed relationships, not a verified highest-profit customer.” No confidential customer row needs to be copied into the report.

A second already-existing, non-confidential synthetic example is `SYNTHETIC-SUPPORTED` in the stored Phase 9 browser candidate: five deposits, recency 26 days and percentile **0.875**. `SYNTHETIC-CAUTION` has three events and percentile 0.5. These values were read from the existing snapshot through the unchanged index; no new rows were created. The companion displays the actual gates, while detailed relationship analytics remain in the original app. The synthetic higher percentile demonstrates activity ranking only, not profitability.

## Segment appropriateness

Source counts: Retail 40,000; SME, Corporate, NGO/NPO and Trust 2,500 each. `segment_context.BANKING_SEGMENTS`, `banking_segment_frame`/`filter_banking_segment` (`segment_context.py:6,20,31`) provide allowlisted alias-safe source labels. `ui_components.banking_segment_selector` (line 128) filters the displayed subset without altering global ranks or manager priority.

Thus all five segments can be inspected, but no segment-specific economic normalization, profitability threshold, product policy or validated cross-segment comparability is implemented. Assignment criteria and effective dates are unknown. Appropriateness as a commercial value classifier across very different segments is **UNVERIFIED**, not established by the existence of a segment selector.

## Tests and implications

Accepted passing cases include `tests/test_analytics.py::test_activity_segments`, `test_metrics_and_distributions_reconcile`; `tests/test_intelligence_views.py::test_all_default_then_segment_pagination_and_customer_continuity[...]`, `test_relationship_activity_and_global_outcome_intersect_without_reranking`; and `tests/test_segment_context.py::test_filter_preserves_all_values_order_and_input`.

The 2,052 SUPPORTED cases are not a high-value list: **only 23** are in the global Higher activity band. All have 2–3 known products, but neither product breadth nor gate permission proves profitability. Do not describe supported count as high-value customers or projected sales.

Smallest safe next action is an agreed, clearly named value-proxy definition and demonstration using existing evidence. This can improve clarity without edits. If explicit high-value classification or profitability is required, obtain appropriate economic data/definitions and authorize a separate additive analysis; do not change accepted ranks, thresholds or decisions to manufacture coverage. A genuine profit/LTV capability cannot be closed by renaming the page.
