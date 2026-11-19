# Phase 8A — AI training, artifacts and inference readiness

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Verified historical experiment, not current deployment

**VERIFIED artifact evidence:** `outputs/phase5/evaluation/evaluation.json` and `evaluation_repeat/evaluation.json` contain matching metric and prediction-vector fingerprints for all three approaches. Source ZIP hash matches both experiment manifests and the canonical feature manifest; experiment code/canonical-feature fingerprints match current bytes. Audit evidence: `evidence/model_and_baseline_audit.json`. No fitting, training CLI or model deployment was executed in Phase 8A.

| Approach | ROC-AUC | Average Precision | Precision@500 | Lift@500 |
| --- | ---: | ---: | ---: | ---: |
| recency_only | 0.940630 | 0.968649 | 100% | 1.685568 |
| logistic_regression | 0.965207 | 0.982397 | 100% | 1.685568 |
| histogram_gradient_boosting | 0.942177 | 0.965445 | 100% | 1.685568 |

Average Precision is the step-integral PR metric. The artifact separately stores trapezoidal PR area; do not interchange them, particularly for tied recency scores. **UNVERIFIED in this audit:** independent numerical recomputation from all original score vectors; only score hashes, not those vectors, were saved. The numbers above are verified against the recorded matching historical runs, not newly reproduced by retraining now or externally validated production results.

## Common experiment contract

Implementation: `historical_evaluation.audit_source/cohort/validate_temporal_coverage/evaluate/metrics/run`; CLI `scripts/evaluate_history.py`.

- Target: 1 iff no valid known non-SERVICE FEE activity in [cutoff, cutoff+90 days). This is **observed future inactivity**, not verified churn, closure or customer intent.
- Train cutoff 2026-01-01, observation [2025-07-05, 2026-01-01), label [2026-01-01, 2026-04-01).
- Holdout cutoff 2026-07-01, observation [2026-01-02, 2026-07-01), label [2026-07-01, 2026-09-29).
- Eligibility: ≥2 qualifying observation-window events. Training cohort **41,259**, positives **8,022**, prevalence **19.4430%**; holdout **32,609**, positives **19,346**, prevalence **59.3272%**. All 32,609 holdout customers also occur in training. No random row split; not unseen-customer generalization.
- Five numeric predictors: recency_days; qualifying_events_180d; events_90d; transaction_volume_180d_usd; deposit_events_180d. No customer identifier, banking segment, current KYC/status/holdings, balances/income, account count, service issue or future last-transaction snapshot enters the predictor list.
- Qualifying future events construct labels only. Recency can use older pre-cutoff history; window count/volume/deposits use inclusive lower and exclusive upper bounds.
- Missing handling: absent count/deposit events in a valid window become zero; this is absence of observed events, not imputation of unknown raw records. Raw required source IDs/dates/amounts/types/ownership are audited and fail if invalid. Fitted input arrays must be finite and nonnegative. Eligible rows have prior events and valid recency.
- Categorical preprocessing: none; categorical/snapshot variables are explicitly excluded. Currency input is provided USD-equivalent volume, not a mixture of raw currency units (report 08).

## Model-specific inventory

| Approach | Training/preprocessing/parameters | Inference and artifact | Approval/deployment |
| --- | --- | --- | --- |
| Recency-only | No estimator fit; score is raw historical recency_days, higher = more inactivity ranking | Offline score array/hash and metrics; no weights needed | Experimental evaluated baseline, not a registered fitted method |
| Logistic regression | log1p of five inputs; StandardScaler fitted on train only; LogisticRegression C=1, lbfgs, max_iter=1000, default L2, no class weighting, seed 42 | predict_proba only inside evaluate immediately after fitting; no saved scaler/coefficients/intercept/pipeline | Experimental; no standalone customer inference API, not operationally approved |
| Histogram gradient boosting | log1p five inputs; max_iter=150, learning_rate=.08, max_leaf_nodes=15, min_samples_leaf=30, l2_regularization=1, early_stopping=False, seed 42; remaining get_params stored | predict_proba only inside evaluate; no saved fitted trees/preprocessor | Experimental; not operationally approved/deployed |

`VERSION=historical-inactivity-v1` versions the experiment definition. `evaluation_code_sha256` versions code; source/feature/cohort/label/score hashes bind evidence. A score-vector hash is **not a fitted-model fingerprint**. Serialized estimator versions/fingerprints are MISSING because no fitted estimator artifact exists. Repository/output scans found no .pkl/.pickle/.joblib/.onnx/.skops/.pt/.h5 model files in the inspected project scope. Objects are local to evaluate and are not returned as persisted pipelines.

Recorded versions: NumPy 2.0.2, pandas 2.3.3, scikit-learn 1.6.1, SciPy 1.13.1, threadpoolctl 3.6.0, joblib 1.5.2; seed 42 and numerical thread limiting. Full boosting defaults and per-model UTC training/score hashes are in the artifact. No dependency version changed in this audit.

## Operational recency claim needs correction

**VERIFIED:** the app does not use a trained predictor. `engine.evaluate` computes illustrative triage priority as .45 × min(recency/90,1) + .35 × relationship activity percentile + .20 × current service issue. Gates determine eligibility separately. The Inactivity page explicitly describes observed recency/frequency.

Therefore **the operational score is not the evaluated recency-only baseline**: the experiment ranks by uncapped raw days, while operations uses a capped composite and current snapshot service context. Do not attach the recency ROC-AUC to the composite queue score, call it a live probability or describe logistic/boosting as approved alternatives.

## Leakage and uncertainty

VERIFIED code safeguards: pre-cutoff features, separate future labels, training-only scaler, no current snapshot features, fixed chronological cutoffs, minimum history and historical cohort grouping. Source coverage ends 2026-10-30, beyond both label windows. **UNVERIFIED:** real ingestion-time availability/completeness and timezone; event-time correctness is not independent ingestion attestation.

The extract has 20/21 total rows per customer, highly regular segment/product/currency patterns and synthetic reference rates. These artifacts limit generalization. Prevalence shifts from 19.44% to 59.33%; repeated customers and a single split limit independence. Perfect top-500 precision is an observed dataset result, not guaranteed customer targeting or intervention benefit. The paired bootstrap is conditional on frozen fitted predictions and excludes refitting/source/model-selection uncertainty. Boosting's small AUC gain over recency is not clearly established by the paired interval; its AP is lower. Logistic is strongest in this recorded experiment, but remains unapproved.

## Experimental AI Comparison panel feasibility

**GO candidate:** a read-only historical metrics table from validated, whitelisted JSON fields, visibly labeled experimental, with cutoff/cohort/target/version/data-code fingerprints and limitations. Use Current operational method: deterministic rules plus descriptive recency, and Historical evaluated recency baseline as distinct labels. Show no new operational rating, priority, calibrated probability or approval control.

**MISSING prerequisites for live fitted inference:** saved trusted fitted preprocessing + estimator, exact feature ordering/dtypes, artifact hash/version and dependency contract, demonstrated training lineage, corruption/staleness handling, valid per-customer cutoff eligibility, read-only inference tests and explicit team/model approval scope. Enabling live inference would require a separately authorized artifact-producing training step; it is not available merely by reading JSON. Do not refit on page load or load user-supplied pickle/joblib files.

**VERIFIED stale copy:** `ui_views.audit_validation()` still says no reproduced performance evaluation is available, contrary to the artifacts. Phase 8B should correct that wording to distinguish available offline evidence from unavailable approved live inference, without changing G3 or model approval.
