# Target, observation chronology and leakage assessment

## Exact formal target

Let Q_i contain the customer's recorded events with a known transaction type other than SERVICE FEE, valid audited identifier/account linkage/date and finite Amount (USD). For cutoff t:

```text
Eligible(i,t) = count{e in Q_i : t−180 days <= event_time(e) < t} >= 2
Y(i,t) = 1 if count{e in Q_i : t <= event_time(e) < t+90 days} = 0
         0 if that future count is at least 1
```

Implementation: `historical_evaluation.py::audit_source:29`, `cohort:51`–64. Unit of observation is one customer across their linked accounts at a cutoff, not an individual transaction/account. A valid event on any account can make the customer negative. Eligibility uses only pre-cutoff events. Structural zero counts for absent 90d/deposit groups are created within an already-observed cohort; this is not permission to impute an unknown/missing feature field during future inference.

Known non-fee types: CASH_DEPOSIT, FOREX_PURCHASE, POS_PURCHASE, ATM_WITHDRAWAL, BILL_PAYMENT. Fees never count as activity. The predicate does not require positive amounts, minimum volume, a transaction channel or current Active/KYC status. It does not explicitly filter transaction `Status`. Read-only source aggregation confirms **all 1,048,575 current rows are Completed**, including all **873,812 non-fee rows**, so no failed-status contamination was found in this extract. A future source with failed/reversed/pending events would need an explicit compatible admission/target policy; the existing five-feature snapshot cannot establish that on its own.

**Reasonable label: future 90-day recorded qualifying-transaction inactivity, conditional on complete observation of this extract.** It is not verified churn.

| Concept | What can be established here? |
|---|---|
| Observed inactivity | Retrospectively no qualifying event in a defined observed interval |
| Predicted inactivity | Future model output for that outcome; not generated in this audit and no ready fitted inference exists |
| Customer attrition / relationship termination | Requires independent business outcome evidence; not identified by this target |
| Account closure | Neither the target nor an as-of cohort rule; no dated closure mechanism in this experiment |
| Retention outcome | Requires customer/intervention follow-up; not proven by inactivity ranking or top-500 precision |

A passive valuable customer can be inactive without leaving; service fees can continue while the label is positive; a recorded transaction can occur without a commercially valuable relationship. These distinctions matter for banking interpretation.

## Exact chronology

| Cutoff | Predictor/count window | Future label window | Eligible customers / positives |
|---|---|---|---:|
| 2026-01-01 | [2025-07-05, 2026-01-01) | [2026-01-01, 2026-04-01) | 41,259 / 8,022 |
| 2026-07-01 | [2026-01-02, 2026-07-01) | [2026-07-01, 2026-09-29) | 32,609 / 19,346 |

Recency can use valid earlier pre-cutoff history outside the 180d window. Boundaries are timezone-naive; cutoff is midnight, lower observation boundary inclusive, upper feature boundary exclusive, target lower boundary inclusive and upper boundary exclusive. Training labels mature before the holdout prediction timestamp. The July 16-column snapshot is historical, not a current November snapshot or evidence of a newly prospective prediction.

## Missing coverage, closure and unsupported customers

`cohort` omits customers with <2 qualifying events in-window. At July, **17,391 of the original 50,000** are outside this model's tested cohort. They must not silently receive zero or fabricated model scores. Their existing operational outcome remains untouched.

`validate_temporal_coverage` checks **global** source minimum/maximum covers each 180d observation and 90d target window, and training target ends before holdout cutoff. The raw file spans 2022-10-01 00:19 through 2026-10-30 23:52; July's horizon is inside global bounds. This does **not** prove complete per-customer/account/channel feeds, absence of ingestion delays or full follow-up. `future.reindex(..., fill_value=0)` treats no observed future record as no activity: an incomplete extraction is not distinguished from true inactivity. Right-censored cutoffs beyond the global coverage guard must not be labelled valid negatives/positives.

Current Closed/Dormant/Restricted statuses are neither model inputs nor dated closure eligibility. The target can combine intentional closure, dormant relationships and unobserved events. A future “active-customer churn” claim would need as-of status/closure evidence and a defined competing-risk/censoring policy. Adding a timeless current status as historical eligibility would itself risk leakage. Do not modify the accepted feature contract or retrospectively impute closure facts.

## Leakage and availability findings

| Check | Evidence / finding | Assessment |
|---|---|---|
| Future events in predictors | `cohort:55`–61 filters timestamp<t before windows/recency; future rows only construct labels | No direct target-period transaction leakage found in inspected code |
| Current snapshots as predictors | Exact five-feature allowlist; tests mutate KYC/holdings without changing X/y | Explicitly excluded; current fields must remain excluded |
| Event time vs availability | transaction_date is used; ingestion/availability/completeness timestamps absent/unverified | Point-in-time availability **UNVERIFIED**; event-before-cutoff alone does not prove the record was known then |
| Scaling/encoding | log1p unfitted; scaler fitted in training pipeline only; no fitted encoding/global future statistics | Correct inspected train/holdout separation; learned state not saved for inference |
| Identity | IDs/index/aliases absent from predictor columns; alias only breaks score ties | No direct ID predictor; repeated customers/dependent behaviors still constrain generalization |
| Duplicates/grouping | Source audit records zero duplicate transaction IDs/ownership conflicts; one row/customer/cutoff, sorted | No random transaction-row split; source audit is dataset-wide and not a deployment feed proof |
| Same-cutoff feature/label windows | Feature ends before t, target starts at t | Disjoint by code; exact boundary tests exist |
| Different-cutoff overlap | January target is inside part of July historical window | Not inherently leakage: that behavior is already historical by July. Do not confuse overlap with future information at the actual prediction time |
| Repeated identities | All 32,609 July identities occur in January; no unseen holdout entities | Longitudinal evaluation, not independent new-customer validation; may be optimistic for other uses |
| Feature amounts/units | Amount (USD) is accepted normalized source input | Historical FX/backfill/ingestion availability not fully attested; no new conversion may be invented |
| Model selection | LR/HGB/recency already compared on the one July holdout | Choosing a winner from that holdout is not a fresh locked final evaluation |
| Coverage/labels | Global range checked, per-customer future completeness assumed | Censoring/selection risk remains; passing tests cannot prove complete real-world activity capture |

Relevant accepted tests: `tests/test_historical_evaluation.py::test_exact_boundaries_and_fee_exclusion`, `test_lower_observation_boundary_inclusive`, `test_future_mutations_change_labels_only`, `test_snapshot_columns_never_predict`, `test_minimum_two_in_window`, `test_grouped_customers_and_order_invariance`, `test_temporal_coverage_rejected`, `test_training_target_cannot_overlap_holdout`. They verify controlled code behavior, **not absence of every real-data leakage or availability issue**. No test was run here.

No confirmed direct future-label predictor leakage was found. Important source-availability, as-of status, feed-completeness, repeated-customer and selection risks remain. Those are explicit feasibility conditions, not findings that the operational engine should be changed.
