# Phase 10C — model and pipeline feasibility

Audit date: 2026-11-20 (Africa/Harare). **Read-only investigation; no implementation, fitting, scoring or artifact creation is authorized.** Overall recommendation is CONDITIONAL GO for a possible future isolated research capability, not readiness to run a model now. Detailed conditions are in 06.

## Verified accepted state

Current HEAD: `6d06878a992980971f468535e8486b5eb577ade3`, plus existing uncommitted Phase 9/10B additions. Actual content, not HEAD alone, matches the accepted Phase 10B run manifest: **96 covered source/test/config/asset files**, **647 recorded passing tests**, zero failures/errors/skips, **96 gate-combination cases**. The prior JUnit bytes and run provenance verify. The original index was read with its existing key and full frozen digest checked: **50,000 / 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN**, 16 feature columns. Phase 10B's original Higher activity count remains 10,003. These are verified accepted results, not a newly executed suite. Full preservation method is in 07.

## Existing models and exact input contract

Implementation: `historical_evaluation.py:8`–18 constants, `:51` cohort, `:81` evaluate, `:113` run. Artifacts: `outputs/phase5/evaluation/evaluation.json`, `outputs/phase5/evaluation_repeat/evaluation.json`, associated `historical_data_audit.json` and `metrics.csv`.

Only these **five ordered columns** enter fitted models:

| Order | Feature | Semantics / numerical domain |
|---|---|---|
| 1 | recency_days | Floor whole days from cutoff to latest known qualifying event strictly before it; finite nonnegative integer; earlier pre-window history may be used |
| 2 | qualifying_events_180d | Known qualifying event count in [cutoff−180d, cutoff); integer; training cohort requires >=2 |
| 3 | events_90d | Count in [cutoff−90d, cutoff); nonnegative integer, <=180d total |
| 4 | transaction_volume_180d_usd | Sum of absolute finite normalized USD amounts in 180d window; nonnegative; not profit/balance |
| 5 | deposit_events_180d | CASH_DEPOSIT count in 180d window; nonnegative integer, <=total |

All five names exist in the **16-column canonical contract**, but that contract has a different overall order and eleven additional fields. A future adapter must select the exact five-feature order explicitly. Raw customer ID/index, aliases, current KYC/status/holdings, source segment, account count, global activity percentile, service issue, balances/income and Phase 10B labels are **not predictors**. Never pass all sixteen columns or the first five canonical columns into a model.

The canonical builder rounds USD volume to two decimals; historical cohort construction uses floating-point grouped sums, then recorded canonical comparison checks volume at two decimals and other inputs at eight. The existing receipt reports zero comparison differences. This establishes semantic/precision agreement for the audited July subset, not an untested bit-for-bit inference guarantee. Any future implementation must lock precision/dtypes and test parity explicitly.

## Preprocessing and estimators

| Method | Actual implementation | Reuse status |
|---|---|---|
| Recency-only baseline | Raw, uncapped holdout recency as ranking score; no fitting (`evaluate:95`) | Formula reusable as descriptive comparator; not fitted AI or probability |
| Logistic regression | np.log1p on all five inputs; StandardScaler→LogisticRegression(C=1, max_iter=1000, lbfgs, seed=42); default no class weighting | Constructor/recipe reusable; fitted scaler and coefficients not retained |
| Histogram gradient boosting | np.log1p on all five inputs; max_iter=150, learning_rate=.08, max_leaf_nodes=15, min_samples_leaf=30, l2=1, early_stopping=False, seed=42 | Constructor/recipe reusable; fitted trees not retained |

`log1p` is deterministic and unfitted. The logistic scaler is inside a pipeline fitted **only on training input**, then reused for holdout transform/predict; it is not fitted on combined data. HGB has no scaler and early stopping does not consume the holdout. One-thread limits, seeds, stable customer sorting and alias-based tie-breaking support reproducibility. Exact numerical behavior remains dependency/platform sensitive.

Both recorded real-source runs match displayed metrics and score SHA-256 values; evaluation-code hash matches current code. Installed and recorded versions match: NumPy 2.0.2, pandas 2.3.3, scikit-learn 1.6.1, SciPy 1.13.1, threadpoolctl 3.6.0, joblib 1.5.2. Optional pinned evaluation requirements exist. Prior synthetic tests cover local reproducibility and feature allowlisting; none were executed here because those tests fit models.

## Saved objects, versions and reproducibility limits

**No fitted reusable runtime model/preprocessing artifact was found.** The offline `evaluate` function creates models locally and returns only metrics and score arrays; `run` writes aggregate JSON/CSV metadata and fingerprints, not fitted models or per-customer scores. No .pkl/.pickle/.joblib/.onnx/.skops/.safetensors model bundle was found outside dependency/VCS directories. JSON artifacts contain hyperparameters, not learned coefficients/scaler statistics/trees.

Existing versions record experiment `historical-inactivity-v1`, code/source/feature/cohort fingerprints, cutoffs, seeds, timestamps and dependencies. Canonical manifests record schema_version=1, builder_version=`phase2-cohort-1`, event_definition=`known-nonfee-finite-amount-v1`. There is **no deployable fitted-model version/checksum, inference schema/loader, persisted preprocessing state or calibrated inference contract**. Do not mistake experiment metadata or score hashes for estimator weights.

The existing CLI could reproduce another offline evaluation to a fresh directory without editing protected code, **after separate authorization**. It is not executed in this audit. Repeating that CLI alone still would not save a reusable fitted object. A future new isolated trainer must capture/persist the complete pipeline, bind its metadata, and demonstrate parity; the protected evaluator need not be changed. Additional fitting is necessary to obtain those objects unless a separately verified saved artifact is later supplied. Existing aggregate metrics cannot reconstruct learned weights.

## Verified historical results (not new performance calculations)

| Method | ROC-AUC | Average Precision | Precision@500 | Lift@500 |
|---|---:|---:|---:|---:|
| Recency | 0.940630 | 0.968649 | 1.000000 | 1.685568 |
| Logistic regression | 0.965207 | 0.982397 | 1.000000 | 1.685568 |
| HGB | 0.942177 | 0.965445 | 1.000000 | 1.685568 |

ROC-AUC is not accuracy; AP is the step-integral average_precision_score, not the separately stored trapezoidal PR area. Precision@500 concerns retrospective inactivity labels, not retention uplift. Logistic is a reasonable parsimonious **research candidate**, not a validated operational selection. All models tie at this top-500 precision; HGB AP is lower than recency. A single inspected holdout does not justify a production winner or new performance claims.

Reuse is technically feasible for data/cohort definitions, model recipes, metric code and evidence handling. Reusing a **fitted model now is not possible** from available artifacts. No model was trained, loaded or used for customer-level prediction during Phase 10C.
