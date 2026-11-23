# Dataset shift, calibration and predictive reliability

## Verified shift: large, and not causally explained

The existing receipt and read-only in-memory reconstruction agree:

| Cohort | Eligible customers | Positives | Positive prevalence |
|---|---:|---:|---:|
| January 2026 | 41,259 | 8,022 | 19.4430306% |
| July 2026 | 32,609 | 19,346 | 59.3271796% |

This is approximately **39.884 percentage points** of observed outcome-prevalence difference. It is not proof of a changed real-bank churn rate, model error, seasonality or an economic shock.

### Additional read-only label diagnostics

Actual source events were audited and the existing pure `cohort` function used **in RAM only**, without its writing `run` wrapper, any fitting, prediction or metric calculation. The same existing cohort counts/positive totals were confirmed. Only aggregate labels/feature summaries were inspected; no customer-level label or score artifact was created.

- All **32,609 July customers are also January customers**; July-only identities = 0.
- **8,650 January customers are excluded from July's eligible cohort.**
- January positives among shared customers = **0**; January positives among the 8,650 excluded customers = **8,022**.
- Among shared identities: **13,263** have January label 0 and July label 0; **19,346** change from 0 to 1; no shared customer has January label 1.

Thus the shifted denominator/eligibility and the different-period outcomes are both real features of this extract. The same-identity comparison changes from zero January positives to 19,346 July positives; the shift is not explained solely by comparing different customers. Conversely, dropping most prior positives means the cohorts do not represent the same distribution of prior inactivity states. This is selection/longitudinal outcome structure, **not evidence that identity itself entered a predictor or proof of target leakage**.

Observed recorded non-fee activity also differs by target period: **211,149 events / 33,237 customers** in [2026-01-01, 2026-04-01), versus **43,875 / 13,263** in [2026-07-01, 2026-09-29). These are source activity summaries, not performance/uplift measurements and not verified real-world economic causes.

### Predictor distributions also change

| Existing feature | Training median | Holdout median |
|---|---:|---:|
| recency_days | 7 | 30 |
| qualifying_events_180d | 6 | 10 |
| events_90d | 6 | 4 |
| transaction_volume_180d_usd | 5,988.45 | 9,607.05 |
| deposit_events_180d | 0 | 0 |

These read-only feature summaries show covariate-location differences as well as changed outcome prevalence. They do not establish formal pure label shift (unchanged P(X|Y)), concept drift (changed P(Y|X)), miscalibration or a causal explanation. A prior-probability adjustment is not justified just because the two prevalences differ.

## Source/data-generation assumptions

Source: **1,048,575 transactions, 50,000 customers, 98,475 accounts**, dates 2022-10-01 through 2026-10-30. Required source audit checks pass. Exactly **1,425 customers have 20 rows and 48,575 have 21**; this unusually regular structure was already recorded in the historical artifact. Read-only source inspection also found every Status=Completed. Fixed transaction cardinalities/near-uniform type counts are reasons to scrutinize generator/extraction assumptions, not proof that the source is synthetic, truncated, false or representative of a live bank.

The non-fee first-to-last recorded span has median **225 days**; **10,085 customers** span at most 90 days and **20,120** at most 180 days. This shows heterogeneous observed activity footprints, not a claim that every customer is a short artificial burst. Missing source-generator documentation and feed completeness remain important unknowns.

**Verified mechanisms:** fixed eligibility rule, changed eligible population, changed observed outcomes/activity and changed feature distributions. **Unverified hypotheses:** seasonality, macroeconomic conditions, genuine customer attrition, campaign effects, account lifecycle, source sampling/generation or missing/truncated feeds. No external business cause is established by the file alone.

## Additional temporal validation

Global dates permit additional candidate cutoffs such as 2023-07-01, 2024-01-01, 2024-07-01, 2025-01-01, 2025-07-01, 2026-04-01 and 2026-08-01 under the existing 180d/90d global coverage rule. This is a coverage feasibility check only: eligible class support, per-customer completeness and model performance were not assessed at those cutoffs.

A future authorized protocol should freeze model/selection rules, use multiple forward windows with labels fully matured before each scoring date, distinguish repeated from unseen customers, and consider non-overlapping label horizons where appropriate. Overlapping windows are correlated and not independent replications. Since July was already examined to compare/select models, it cannot become a newly untouched final holdout by relabelling it. Independent future/external validation would be needed for stronger generalization claims.

Deployment on a new dataset requires feature/source/eligibility/drift validation and fresh evaluation evidence; ingestion compatibility alone is insufficient. Retraining may be necessary if relationships change, but should not be automatic or assumed sufficient to fix incomplete labels. The existing results establish one recorded chronological experiment, not stable operational predictions.

## Calibration/evaluation inventory

| Validation item | Actual evidence | Current status / missing work |
|---|---|---|
| ROC-AUC / AP / trapezoidal PR area | Stored per model; metric code computes them | Present, single holdout; not accuracy |
| Precision / lift | Stored top-500 with prevalence/size | Present, one K; all methods tie at precision=1 |
| Precision-recall curve | Computed inside `metrics`, arrays not saved as curve artifact | AP/area available; no full retained curve/sensitivity report |
| Probability calibration / calibrator | No calibration implementation/artifact found | **MISSING** |
| Calibration curves / in-the-large / expected-vs-observed rates | No saved results or mean predicted probability | **MISSING**; cannot infer from prevalence alone |
| Brier score / heldout log loss | Not in metric output/artifacts | **MISSING**; HGB's `loss='log_loss'` is a training objective, not a reported validation log loss |
| Segment-level calibration/performance | Not reported | **MISSING**; source segment dates/denominators must be defined |
| Threshold sensitivity / FP/FN / confusion matrices | No operating-threshold evaluation | **MISSING**; top-500 ranking is not an approved classification threshold |
| Aggregate confidence intervals | Existing 200-repeat paired customer bootstrap of frozen holdout predictions | Present for AUC/AP only; conditional on one extract/fitted models |
| Per-customer uncertainty intervals | No validated method/artifact | **MISSING**; aggregate bootstrap is not a customer risk interval |
| Multi-period predictive stability / external validation | One chronological repeated-customer holdout | **MISSING** |

Existing logistic aggregate 95% bootstrap intervals: ROC-AUC **[0.963388, 0.967179]**, AP **[0.981556, 0.983357]**. These values are read from the prior JSON, not recalculated. The bootstrap excludes refitting/tuning/source uncertainty; its recency-minus-HGB AUC interval includes zero. Do not extrapolate its conditional precision to new customer populations or claim individual confidence bounds.

## Safest future output

**Research-only relative inactivity ranking/uncalibrated score**, explicitly not churn probability or banking permission, is the safest potential presentation after the required artifact/target/validation conditions. There is **no fitted customer-level score available now**. Calibrated percentages are not defensible on current evidence. Risk bands need a predeclared, evaluated basis; arbitrary low/medium/high cutoffs must not be invented.

A future authorized study should measure probability reliability as well as ranking stability. A rank-only research demo need not claim successful calibration; it must disclose absent/failed calibration and avoid percentage-risk wording. Actual calibrated probabilities require an independently evaluated train/calibration/test protocol and satisfactory results before that label is used. No new performance figures, calibration calculations or customer predictions were produced here.
