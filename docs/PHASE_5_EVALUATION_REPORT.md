# Phase 5 historical inactivity evaluation

Executed 2026-11-16 on authorized local competition data. Experimental offline evaluation only; the approved application method remains the unchanged deterministic six-gate rules. No model scores were connected to the queue, eligibility or review service.

## Historical availability audit

Source: `/Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip`; SHA-256 `4a7919a7a98f8340d2d7589ec8cfdbe352742686df97cb6e8d6bd58d93fd4e1b`. The ZIP contains one CSV with 1,048,575 transaction rows, 50,000 customers and 98,475 accounts. Fresh audit found zero invalid identifiers/dates/amounts, duplicate transaction IDs, ownership mismatches, conflicting account ownership or unknown transaction types. Coverage: 2022-10-01 00:19 through 2026-10-30 23:52. Event time is `transaction_date`, parsed day-first and timezone-naive; source timezone and ingestion timestamps are unavailable. The coarse `Date`, onboarding and account-opening fields parsed without invalid values and were not after the corresponding event, but none enters the model.

The supplied extract has 1,425 customers with 20 transaction rows and 48,575 with 21. This unusual construction limits external validity even when chronological leakage is prevented. Coverage supports observed-window labels; it does not independently attest complete bank transaction capture, actual churn or account closure. Current KYC/status/holdings and other snapshots lack historical effective dates and are excluded.

## Frozen evaluation design

- Training observation date: 2026-01-01; observation window [2025-07-05, 2026-01-01); target [2026-01-01, 2026-04-01).
- Holdout observation date: 2026-07-01; observation window [2026-01-02, 2026-07-01); target [2026-07-01, 2026-09-29).
- Qualifying activity: known valid non-SERVICE FEE transaction, consistent with the existing builder; no claim of verified settlement semantics.
- Eligibility: at least two qualifying transactions in the preceding 180 days. One row per eligible customer and cutoff.
- Target 1: zero qualifying events in the future 90-day half-open window. Future events construct labels only. Training labels end before the holdout date.
- Predictors: recency floor-days since latest pre-cutoff event; qualifying 180-day count; 90-day count; 180-day absolute USD volume; 180-day cash-deposit count. Each is reconstructed independently per cutoff. No current customer/account/KYC status, holdings, balances, segment, account count, service issue or last-transaction snapshot.

Training: **41,259 customers**, 8,022 positives, **19.443031%** target prevalence. Holdout: **32,609 customers**, 19,346 positives, **59.327180%** prevalence. All 32,609 holdout customers also occur in training. This is a chronological repeated-customer evaluation, not unseen-customer validation. There is no random row split. July predictors reconcile to the canonical feature artifact on every eligible row, with zero differences across all five measures (volume compared at its documented two-decimal precision).

## Models and measured results

Recency score increases with days since last event. Fitted models use log1p of the five predictors. Logistic regression uses a training-only StandardScaler, L2 default penalty, C=1, lbfgs, max_iter=1000, no class weighting, seed 42. Histogram boosting uses 150 iterations, learning rate .08, 15 leaves, minimum leaf size 30, L2=1, early_stopping=False and seed 42. Remaining defaults are fixed by scikit-learn 1.6.1 and recorded in the artifact for boosting. Single-thread numerical fitting is used. Hyperparameters were fixed before the holdout comparison; no tuning on holdout labels.

| Model | ROC-AUC | PR-AUC (AP) | Precision@500 | Lift@500 | Fit time | Fit/predict/metrics |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| recency_only | 0.940630 | 0.968649 | 100.0% | 1.685568 | 0.0000s | 0.0314s |
| logistic_regression | 0.965207 | 0.982397 | 100.0% | 1.685568 | 0.0320s | 0.0611s |
| histogram_gradient_boosting | 0.942177 | 0.965445 | 100.0% | 1.685568 | 0.3241s | 0.4696s |

PR-AUC means **average precision**, a step integral; the artifact also records trapezoidal PR area, which differs for tied recency scores. Precision@500 uses score descending then stable keyed alias ascending. Lift divides precision by holdout prevalence. Recorded end-to-end runtime for the initial source audit, cohort reconstruction, fitting and 200 paired bootstrap samples: **96.28s**, including local import/runtime overhead. Later repetitions may differ in time.

## Comparison with supplied claims

The local original setup request and `Banc-Inc360_Submission_Evidence_Report.docx` report concept figures: recency ROC-AUC .9406, PR-AUC .9686, Precision@500 100%, lift 1.686; logistic .5394, .6129, 68%, lift 1.146. Original training code, feature preprocessing and run artifact were not supplied. The two locally available later concept-proposal DOCX files do not supply an original executable evaluation.

The **recency metrics reproduce to the reported precision**. The newly specified logistic pipeline gives ROC-AUC **.9652**, PR-AUC **.9824**, Precision@500 **100%**, rather than the reported .5394/.6129/68%. That is a new reproducible experiment under the stated historical configuration, not reproduction of an unavailable original logistic implementation. Feature/preprocessing/regularization differences are possible explanations; their actual historical cause cannot be established. No result was forced to match a prior figure. No previous histogram-boosting metric was available for comparison.

Recency has better AP than histogram boosting (.96865 versus .96544). Boosting's small ROC-AUC advantage over recency is uncertain: the paired 95% interval for recency-minus-boosting AUC is [-0.003375, 0.000414], including zero. Logistic ranks better on this holdout, but neither its high score nor perfect observed top-500 precision establishes calibrated risk, production accuracy or intervention benefit.

## Uncertainty and reproducibility

Two hundred paired customer bootstrap samples, seed 42, hold fitted predictions fixed. ROC-AUC 95% intervals: recency .93833–.94288; logistic .96339–.96718; boosting .93981–.94434. These conditional intervals exclude training/refitting variability, model-selection uncertainty, the substantial prevalence shift, source-generation artifacts and external validity. One historical split provides no production or fairness certification.

```sh
.venv/bin/python -m pip install -r requirements-evaluation-lock.txt
.venv/bin/python scripts/evaluate_history.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --out outputs/phase5/evaluation-new
```

Choose a new output directory; the script refuses overwrite. Optional packages are isolated in `requirements-evaluation*.txt`; the application requirements and lock remain unchanged. Downloaded official wheels were checked against PyPI SHA-256 metadata before local installation; the application itself needs no internet. Installed versions and Python version are captured in `evaluation.json`. CPU discovery is explicitly capped by the CLI to avoid a sandbox-blocked physical-core probe; numerical thread limiting is already in the evaluator.

Versioned artifact: `outputs/phase5/evaluation/evaluation.json` (`historical-inactivity-v1`), audit JSON and metrics CSV. It includes data/code/canonical fingerprints, cutoff/feature/label definitions and fingerprints, seed, model parameters, training UTC times, score fingerprints, metrics, uncertainty, versions and reproduction command. No raw identifiers or individual predictions are exported. The repeat-run comparison is recorded separately under `outputs/phase5/reproducibility.json`. The canonical customer CSV remains unchanged.
