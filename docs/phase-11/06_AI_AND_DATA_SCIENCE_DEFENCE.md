# AI and data-science defence — 20 direct answers

Use the current historical panel plus existing artifact provenance, not a live prediction claim. Principal sources: `historical_evaluation.py`, `outputs/phase5/evaluation/evaluation.json` and repeat JSON, `experimental_evidence.py`, `docs/phase-10c/01`–`06`. All figures below are recorded experimental evidence, not a new Phase 11 model run.

| # | Judge question | Concise truthful answer / evidence |
|---:|---|---|
| 1 | Why use machine learning? | To test whether several pre-cutoff transaction features rank future recorded inactivity better than simple recency. The actual experiment compares three methods on a defined target. ML is not necessary to bypass suitability/eligibility; current actions remain deterministic. |
| 2 | Why logistic regression? | It is a parsimonious fitted comparator and has the best recorded AUC/AP among these three methods. Five inputs, log1p, training-only StandardScaler, C=1, lbfgs, max_iter=1000, seed=42 (`evaluate`). One examined holdout does not certify a production winner. |
| 3 | Why compare against recency? | A strong simple baseline tests whether ML adds information beyond an obvious banking activity signal. Offline baseline uses raw uncapped recency; original operational priority is a separate composite. |
| 4 | Why histogram gradient boosting? | It tests nonlinear structure against the linear comparator and recency: log1p inputs, 150 iterations, learning rate .08, 15 leaves, minimum leaf 30, L2=1, no early stopping, seed=42. HGB's AP is below recency here; do not claim universal improvement. |
| 5 | Exact target? | Eligible customer has >=2 qualifying events in prior 180d; positive iff zero known non-SERVICE FEE events in [cutoff, cutoff+90d), negative otherwise. It is recorded inactivity conditional on complete observation, not confirmed attrition (`cohort`). |
| 6 | Observation window? | Counts/volume/deposits use [cutoff−180d, cutoff); events_90d uses its last 90d. Recency may use an earlier qualifying event before the window. January window starts 2025-07-05; July starts 2026-01-02. |
| 7 | Prediction horizon? | 90 days, lower boundary inclusive and upper exclusive. January target [2026-01-01, 2026-04-01); July [2026-07-01, 2026-09-29). These are retrospective labelled periods, not today's live forecasts. |
| 8 | What does ROC-AUC .965207 mean? | On the recorded eligible holdout, it summarizes how well the logistic score ranks an inactive-label customer above an active-label customer, with standard tie treatment. It is discrimination under this sample/design, not a bank-wide future guarantee. |
| 9 | Why not 96.5% accuracy? | Accuracy depends on a classification threshold and class distribution. No such operating-threshold accuracy is reported. AUC integrates ranking behavior across thresholds; converting it into an accuracy claim is wrong. |
| 10 | Why isn't Precision@500 retention success? | It is the observed inactivity-label fraction in the top 500 ranked cases; all three methods equal 1. Lift 1.685568 compares that to 59.3272% holdout prevalence. It is not response, contact approval, conversion or retained customers. |
| 11 | Why no live customer probabilities? | Calibration is unverified, no fitted scaler/model is saved, no approved inference path exists and the target is not verified churn. The UI explicitly shows unavailable live inference rather than fabricated probabilities. |
| 12 | Why not deploy the model? | Dataset/coverage/availability assumptions, large shift, one repeated-customer holdout, missing calibration and missing reusable fitted state remain. G3 does not register a fitted action method. Phase 10C recommends existing historical evidence for this pitch. |
| 13 | What leakage controls exist? | Pre-cutoff feature filtering, separate future labels, five-feature allowlist, training-only scaling, one row/customer/cutoff, no ID/current KYC/holdings input and exact boundary/future-mutation tests. These do not certify ingestion availability, complete feeds or every real-data leakage risk. |
| 14 | What validation remains? | Multiple forward periods/domains, source/censoring/selection analysis, calibrated probability assessment, Brier/heldout log loss, reliability curves, threshold/FP-FN analysis, subgroup support/stability and independent validation. Existing bootstrap is aggregate, conditional on frozen predictions, not individual risk uncertainty. |
| 15 | Why does prevalence shift? | Verified January 8,022/41,259 (19.443%) versus July 19,346/32,609 (59.327%). All July identities are shared and January-negative; January positives are among 8,650 excluded later. Eligibility/outcome/predictor distributions differ; seasonal/economic/generator causes are unverified. |
| 16 | Inactivity versus churn? | Observed inactivity is absence of recorded qualifying events in a window; predicted inactivity would estimate that future label. Churn/closure/relationship termination requires separate business evidence. Passive valuable relationships and fees can persist without qualifying activity. |
| 17 | What are the sixteen canonical columns? | customer_id; qualifying_events_180d; events_90d; recency_days; transaction_volume_180d_usd; deposit_events_180d; product_gap; behavioural_reason; products_held; customer_status; account_status; kyc_status; service_issue; customer_segment; account_count; relationship_activity_percentile. Names/order/semantics remain unchanged (`data_access.FEATURE_COLUMNS`). |
| 18 | Which five were model predictors? | Ordered recency_days, qualifying_events_180d, events_90d, transaction_volume_180d_usd, deposit_events_180d. Eleven other canonical fields, segment/profit assumptions and Phase 10B classifications are excluded. Model eligibility >=2 is not G2 sales PASS >=4. |
| 19 | Why not simply reuse the trained model? | Recipes/hyperparameters/metric and score hashes were saved, not fitted coefficients/scaler means/trees. `evaluate` discards estimator objects after returning metrics/scores; `run` persists aggregate results only. A future authorized process must fit/capture a complete trusted bundle, including log1p exactly once, and validate it. |
| 20 | What before bank deployment? | Approved target/product/model policies, source/availability/completeness and current eligibility evidence, reproducible trusted artifacts, calibration/generalization/security/access validation, isolated regression and controlled outcome pilot. A high score would still not authorize outreach, product/credit approval or a financial transaction. |

## Exact historical comparison to show

| Method | ROC-AUC | Average Precision | Precision@500 | Lift@500 |
|---|---:|---:|---:|---:|
| Recency only | 0.940630 | 0.968649 | 1.000000 | 1.685568 |
| Logistic regression | 0.965207 | 0.982397 | 1.000000 | 1.685568 |
| Histogram gradient boosting | 0.942177 | 0.965445 | 1.000000 | 1.685568 |

Training: **41,259 / 8,022 positives**, holdout **32,609 / 19,346**, shared identities **32,609**. AP is the step-integral average_precision_score; trapezoidal PR area is a separate stored statistic. Existing two runs match displayed metrics and score fingerprints. No new fit, prediction, calibration calculation or metric was performed in Phase 11.

## Anticipate deeper follow-ups

- Prevalence difference alone does not prove miscalibration, pure label shift or economic causes; predictor distributions change too. Do not perform an ad hoc prior correction on stage.
- Original source rows are all Completed in the Phase 10C audit, but the generic qualifying predicate does not filter Status. New sources need semantic/domain validation, not just matching column names.
- Global date coverage does not guarantee every customer/channel feed is complete; absent future rows can mean inactivity or missing extraction. Account closure is not separately dated/modelled here.
- All 32,609 July cases satisfy historical model eligibility; 17,391 original customers do not. No zero/made-up score should be assigned to unsupported cases.
- Positive/negative labels and feature summaries recomputed read-only in Phase 10C were not customer-level model predictions. Future predictive work remains conditional and unimplemented.
- The exact accepted 647-case source-bound receipt is historical. Phase 11 performs no model training and no full test rerun; the freeze metadata exception must not be hidden behind that count.
