# Verified historical experimental AI evidence

## Scope and trusted receipt

The runtime reader displays only the existing server-controlled `outputs/phase5/evaluation/evaluation.json`. SHA-256: `ee516bb25c0e0c467b7d5d8fffdb9a8f4fe50bc76c2fd6d4c399376594a97200`. Experiment: `historical-inactivity-v1`, experimental only. The hash is a reviewed content pin, not a fallback metric. No uploaded/user-selected artifact or serialized estimator is accepted.

The reader verifies schema/version, experimental scope, exact experiment configuration and five historical features, artifact/source/feature/code fingerprints, current manifest/cutoff/rows, cohort sizes/positives/prevalence, shared customers, exact model inventory, requested/effective top K, finite bounded metrics, lift/prevalence consistency and prediction-fingerprint syntax. Only whitelisted fields reach the UI. Missing evidence is Unavailable; receipt/data/code mismatches are Stale; malformed/inconsistent metadata is Unavailable. Those states expose no metric table and do not switch data mode.

Source SHA-256: `4a7919a7a98f8340d2d7589ec8cfdbe352742686df97cb6e8d6bd58d93fd4e1b`.
Evaluation-code SHA-256: `3895e2801a63861d637fea3bc48a9b06be129ee541bc68d0480661d6b895155d`.
Canonical feature SHA-256: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`.

## Existing experiment, not new training

Training cutoff 2026-01-01: 41,259 customers, 8,022 target positives (19.4430%). Holdout cutoff 2026-07-01: 32,609 customers, 19,346 target positives (59.3272%). Shared customers: 32,609. Observation window 180 days; target window 90 days; minimum events 2; seed 42; K 500.

Features: recency, qualifying events / 180d, events / 90d, transaction volume / 180d USD, deposit events / 180d. Current KYC/status/holdings and banking segments are not model predictors.

| Existing historical comparator | ROC-AUC | Average Precision | Precision@500 | Lift@500 |
|---|---:|---:|---:|---:|
| Recency-only baseline | 0.940630 | 0.968649 | 1.000000 | 1.685568 |
| Logistic regression | 0.965207 | 0.982397 | 1.000000 | 1.685568 |
| Histogram gradient boosting | 0.942177 | 0.965445 | 1.000000 | 1.685568 |

These rounded report values come from the pinned prior JSON; the UI reads validated full-precision artifact values. Average Precision is the step-integral PR metric (`pr_auc_average_precision`), not the separate trapezoidal PR area. Two existing real-source evaluation receipts are compared by final acceptance, without rerunning real-data training.

The target is zero qualifying known non-service-fee events in the following 90-day interval: observed inactivity, not verified churn or account closure. This is a limited chronological repeated-customer holdout. Its changed prevalence, repeated identities and top-500 precision do not establish retention uplift, generalization to new customers, production calibration or deployment validity.

## Operational and live-inference separation

Panel A describes the existing deterministic six-gate operational engine and descriptive recency/composite triage. The offline raw-recency comparator is not that composite priority formula.

Panel B shows the verified historical comparison and limitations on Inactivity Intelligence and Audit & Validation Evidence. Old Audit wording that denied existing reproduced evaluation was corrected.

Panel C states: **Unavailable — fitted preprocessing and model artifacts have not been saved or approved for live inference.** No per-customer probabilities are invented. Runtime imports neither estimators nor evaluation/fitting functions and performs no fitting, prediction, deserialization, model approval or G3 change. The only fitting during validation is the pre-existing isolated synthetic reproducibility test explicitly permitted by the user.
