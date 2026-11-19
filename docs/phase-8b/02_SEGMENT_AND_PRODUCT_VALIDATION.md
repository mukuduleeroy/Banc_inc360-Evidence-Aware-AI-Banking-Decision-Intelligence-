# Segment and Savings evidence validation

## Source context and privacy

The validated source contains Retail (40,000), SME (2,500), Corporate (2,500), NGO/NPO (2,500) and Trust (2,500). These are recorded labels, not inferred clusters. Assignment criteria and snapshot effective dates are unknown. Case/whitespace normalization returns only those five allowlisted labels; missing, malformed, arbitrary or malicious values become Unknown. The local canonical snapshot has no Unknown segment rows.

`segment_context.py` reads the existing source segment position internally and returns only `customer` presentation aliases, `banking_segment` and fixed `segment_origin`. Aliases must match the established format, be unique and cover every filtered analytic row. Duplicate aliases, missing joins, private input columns and unallowlisted context labels are rejected. Original frame columns, index, row order, values, priorities and ratings are preserved. Helpers return detached frames; neither source nor analytics frames are mutated. Segment is never added to `engine.Case` or used as a predictor, gate, priority term or eligibility rule.

Customer 360 explicitly labels the segment as a source-provided snapshot and explains that it is not inferred from clustering or transaction behaviour. It retains the globally selected customer.

## Filters and state

Inactivity, Relationship and Product views default to All. The existing outcome filter is applied, then the banking segment subset; existing recency, coverage, observed activity and opportunity filters continue to intersect with that subset. Pagination uses the original keys and resets to page 1 on context changes. Global customer selection changes only through explicit existing selection/open actions.

Filtered subtotals are labeled separately from unfiltered population KPIs. Relationship percentiles are filtered after their existing global calculation; they are not recomputed within segments. The manager queue has no new segment filter or ranking change. `activity_segment` retains its values/key; its visible label is now Observed activity band.

Real-data AppTest coverage verifies All table equivalence, segment/outcome/activity intersections, empty Unknown results, pagination reset, global selection continuity, exact existing percentiles/order and product KPI invariance. All nine existing views remain covered by native navigation tests and actual browser checks.

## Savings evidence and gate authority

The Savings panel uses `index.passport(alias)` for product-gap evidence, actual G4/G5 status/reason codes/reasons and final rating. It displays known holdings using existing allowlisted ownership parsing, historical deposit count and sanitized recorded rationale, cutoff, source/policy hashes and current-snapshot limitations.

Required disclosure: **This is a prototype Savings discussion opportunity for staff review, not an approved banking offer or customer-contact authorization.** Segment-specific bank suitability policy is unavailable. No terms, rates, lending/FX suggestions or new product eligibility are invented. All six gates and human review still apply.

Tests cover supported evidence, pending KYC, frozen accounts, already-held Savings, absent rationale, caution and invalid ownership. G4/G5 objects and outcome must match the authoritative passport exactly. Extra segment/model-score display columns cannot change the explanation or queue.

If the global selection falls outside the opportunity subset, the page explicitly retains it and asks for an explicit customer selection. It does not silently render another customer's explanation. Empty results remain honest; for example, Trust has no already-held Savings rows in this snapshot.

No report contains raw customer identifiers or customer-level confidential examples. Private local screenshots and test receipts remain subject to the existing data restrictions.
