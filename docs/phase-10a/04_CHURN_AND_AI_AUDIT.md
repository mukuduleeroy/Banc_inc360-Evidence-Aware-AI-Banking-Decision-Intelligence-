# Churn-risk and AI investigation

## Churn-risk verdict: PARTIAL

There is no operational churn probability or confirmed-churn label. `ui_views.inactivity_intelligence` (`ui_views.py:86`) explicitly presents **observed historical recency**, coverage bands and filters, not predicted future inactivity. `analytics.recency_band` (`analytics.py:24`) uses <=30, <=60, <=90 and >90 days. The accepted population contains **26,734 customers with recency >90 days**, median recency **107 days**. Neither number is a churn count.

`build_data.run` (`build_data.py:79`–91) uses valid known non-SERVICE FEE events strictly before the observation cutoff. Counts/volume/deposits use the preceding 180 days; events_90d the preceding 90 days; recency can use an earlier qualifying event outside those windows. Current source status/KYC/holdings do not become historical predictors.

Operational `engine.evaluate` (`engine.py:30`) uses the unchanged composite:

`0.45 * min(recency_days / 90, 1) + 0.35 * relationship_activity_percentile + 0.20 * current_service_issue`

Missing/invalid evidence is separately gated; valid inputs yield the formula above, while implementation guards unavailable numeric values. This is review triage across recency, activity and current service context, not a calibrated churn probability or profitability score. Manager ordering uses unrounded score, then alias (`data_access.build_index`, line 163); display may round to three decimals. The offline recency baseline instead uses raw **uncapped recency only**. They are different scores.

### Reproducible inactivity case

Use Inactivity Intelligence with outcome ALL, segment All, recency >90 days and coverage 4+ events. Inspect the first engine/data-backed alias → Customer 360/Decision Passport. The explanation shows actual historical recency/history and gate reasons; it does not assert that the customer will leave. Read-only verification also found **546** SUPPORTED cases have recency >90, illustrating that a disengagement signal and gated permission for a Savings discussion can coexist; neither is a confirmed churn event.

For safe what-if explanation, existing Evidence Replay permits KYC Pending and reset, showing changed gate/outcome without altering canonical data. It is explicitly **simulation**, not transaction-level event replay or historical treatment evidence. No new replay was run in this audit.

Tests include `tests/test_navigation.py::test_replay_reset_and_no_customer_action_path`; `tests/test_analytics.py::test_recency_boundaries`; `tests/test_historical_evaluation.py::test_exact_boundaries_and_fee_exclusion`, `test_future_mutations_change_labels_only`, `test_snapshot_columns_never_predict`, `test_training_target_cannot_overlap_holdout`; `tests/test_gate_protection.py::test_real_replay_reset_never_changes_canonical_or_audit`.

## Practical AI verdict: MET, historical experimental scope only

A real historical fitting/evaluation implementation and two prior matching result artifacts exist. This meets a scoped practical AI-and-analytics demonstration; the brief does not explicitly require deployed fitted inference. It does not justify describing the application as a live ML churn predictor.

Artifacts inspected directly:

- `outputs/phase5/evaluation/evaluation.json` and `outputs/phase5/evaluation_repeat/evaluation.json`.
- `outputs/phase5/evaluation/historical_data_audit.json`.
- `historical_evaluation.py:51` `cohort`, `:66` temporal validation, `:73` `metrics`, `:81` `evaluate`, `:113` `run`.
- Runtime historical reader `experimental_evidence.py:54` and panel `ui_components.py:161`, rendered by Inactivity (line 103) and Audit (line 247).

The reader returned **Verified / VERIFIED_HISTORICAL_ONLY** during this read-only audit. Artifact SHA-256 `ee516bb25c0e0c467b7d5d8fffdb9a8f4fe50bc76c2fd6d4c399376594a97200`; evaluation-code SHA `3895e2801a63861d637fea3bc48a9b06be129ee541bc68d0480661d6b895155d` matches current source. Source/feature association verifies. The two artifacts match all displayed metrics and score fingerprints. That verifies recorded reproduction; no experiment was rerun here.

### Cohorts, periods and target

| Cohort | Observation window | Target window | Customers | Positives | Positive prevalence |
|---|---|---|---:|---:|---:|
| Training cutoff 2026-01-01 | [2025-07-05, 2026-01-01) | [2026-01-01, 2026-04-01) | 41,259 | 8,022 | 19.4430306% |
| Holdout cutoff 2026-07-01 | [2026-01-02, 2026-07-01) | [2026-07-01, 2026-09-29) | 32,609 | 19,346 | 59.3271796% |

Eligibility: >=2 qualifying events in the preceding 180 days. One row per eligible customer per cutoff. **32,609 identities are shared** between cohorts; this is chronological repeated-customer evaluation, not unseen-customer generalization. Holdout metrics apply to these 32,609, not all 50,000 customers.

Exact target (`historical_evaluation.cohort`, lines 55–64): label 1 iff **zero known valid non-SERVICE FEE events** in `[cutoff, cutoff+90 days)`. This is observed next-90-day inactivity, not verified churn, closure or dissatisfaction. Known events are CASH_DEPOSIT, FOREX_PURCHASE, POS_PURCHASE, ATM_WITHDRAWAL, BILL_PAYMENT; SERVICE FEE is excluded. Valid finite USD amounts and identifier/link/date/source prerequisites are audited before construction.

Five predictors only: recency_days, qualifying_events_180d, events_90d, transaction_volume_180d_usd, deposit_events_180d. KYC, account/customer status, current holdings, segment, service issues, balances, income and current last-transaction snapshots are excluded. Future rows affect labels, not historical predictors. Pre-cutoff recency may reference history earlier than the 180-day count window.

### Methods and verified metrics

Baseline: untransformed raw holdout recency, higher meaning more likely inactive. Logistic regression: log1p of all five historical features → training-fitted StandardScaler → LogisticRegression(C=1, max_iter=1000, solver=lbfgs, random_state=42), no class weighting. HGB: log1p of those features, max_iter=150, learning_rate=.08, max_leaf_nodes=15, min_samples_leaf=30, l2_regularization=1, early_stopping=False, seed=42. All fitting occurs inside the offline evaluator; runtime panel reads JSON only.

| Method | ROC-AUC | Average Precision | Precision@500 | Lift@500 |
|---|---:|---:|---:|---:|
| Recency only | 0.940630 | 0.968649 | 1.000000 | 1.685568 |
| Logistic regression | 0.965207 | 0.982397 | 1.000000 | 1.685568 |
| Histogram gradient boosting | 0.942177 | 0.965445 | 1.000000 | 1.685568 |

AP is sklearn's average_precision_score (step-integral PR metric), not the separately recorded trapezoidal PR area. ROC-AUC is ranking discrimination, **not accuracy**. Precision@500 is retrospective target-label precision, not offer conversion or retained customers. All three top-500 values tie at 1; this ranking slice does not establish incremental operational benefit. Logistic regression has higher ROC-AUC/AP than this baseline; HGB has slightly higher ROC-AUC but **lower AP** than recency. Do not claim both fitted methods outperform every baseline metric.

### Fitted/saved/deployed distinction and limitations

- Existing code/receipts establish prior fitting; the earlier complete suite includes an isolated synthetic estimator reproducibility test. No retraining was performed during Phase 10A.
- No saved fitted model/preprocessing artifact (.pkl/.pickle/.joblib/.onnx) was found outside the virtual environment; the receipts contain metrics/hyperparameters/fingerprints, not reusable fitted estimators.
- No operational inference exists; G3 permits the deterministic method and rejects unapproved model-driven actions (`engine.evaluate`). Runtime display explicitly says fitted preprocessing/models are not saved/approved for live inference. No per-customer probabilities are available.
- Single temporal holdout; repeated identities; large prevalence shift; sparse/synthetic-looking source patterns (1,425 customers with 20 transactions, 48,575 with 21); unknown ingestion availability/completeness attestation; unknown timezone/current snapshot dates. Dataset authenticity/nature is not established merely by that pattern.
- Source event range through 2026-10-30 covers target end globally, but does not prove every customer's future extraction is complete. Missing events can influence the inactivity label.
- Existing 200-repeat paired bootstrap is conditional on frozen predictions/one extract; it excludes model refitting, selection and source uncertainty. It does not resolve deployment validity or business causal effects.
- No verified churn calibration/threshold operating point, external validation or causal retention/revenue uplift is established.

Convincing live defence: show the validated historical panel, exact target/cohorts, comparison against recency, model/code/source provenance and explicit unavailable inference. Use the existing deterministic case/Passport to demonstrate banking controls separately. No model fitting is needed for the pitch, and no live-model claim should be made.
