# Proposed inference and safety architecture — investigation only

**No module, model, loader, score file or interface described below was implemented.** A standalone local research companion is technically feasible and safer than editing accepted dashboards, but it is conditional on 06. There is no ready fitted artifact to load.

## Proposed isolated flow

Validated point-in-time snapshot + reviewed immutable model/preprocessing bundle → research admission/schema checks → five-feature projection → exactly matched preprocessing/inference → independent eligible-customer ranking → evidence/limitations/provenance display.

This flow must remain separate from original `app.py`, Phase 9 activation/registry, Phase 10B fixtures/value proxy, operational Case/G1–G6, original manager priority and review/audit stores. No canonical column is added and no current dashboard loader is changed.

## Snapshot/feature admission

1. Read an authorized compatible snapshot and adjacent lineage without changing the canonical file. Verify feature/source/version/hash/row count/cutoff and as-of availability/coverage assumptions. Never merely change a cutoff label on old features.
2. Explicitly select ordered `historical_evaluation.FEATURES`: recency, qualifying_events_180d, events_90d, USD volume, deposit_events_180d. Eleven other canonical fields remain excluded from model inputs.
3. Require finite nonnegative numeric inputs, valid integer counts/recency, count consistency and >=2 in-window qualifying events, with no missing-field imputation. Distinguish known zero from unknown evidence.
4. Admit only the intended source/event semantics, units, point-in-time definition and training support. Existing source has all Completed statuses, but the predicate does not validate completion; a new source must establish compatible semantics. Unknown FX/feed/eligibility/domain differences must not silently pass because names match.
5. Record unsupported cases separately, with reasons and denominators; no fabricated zero scores. For July, only the 32,609-customer training-compatible cohort has evaluation support; do not imply all 50,000 can be scored.
6. Define as-of active/closed-customer treatment if the desired use is active-customer attrition. Do not use undated current status as a historical predictor/selection shortcut or weaken original KYC/action controls.

The accepted 16-column file contains all five predictors. `data_access.provenance_issues`/load interfaces and existing feature/analytics numeric helpers offer reusable checks, but full six-gate operational evidence validation is not a model-admission specification. Likewise a Phase 9 compatible CSV/candidate is not automatically model-compatible or generalizable. Its synthetic source/size/event semantics require their own research admission.

The source-derived activity percentile, source segment and current service issue may be useful **descriptive** context, but they do not become extra predictors. Any new research feature definition would need explicit versioning/approval; it cannot silently replace the current five or alter accepted sixteen.

## Complete preprocessing/model bundle

A future separately authorized training process must obtain and save a fitted object and preprocessing state in a new private research namespace. Original `historical_evaluation.evaluate` discards estimator objects, so its metrics JSON is insufficient.

For logistic regression, preserve both **log1p exactly once** and the training-fitted scaler/estimator. Current code applies log1p outside the sklearn pipeline; saving only a scaler+LR pipeline then passing raw inputs would be wrong. HGB also expects the original log1p transform, despite no scaler. No refitting, scaling-to-the-current-batch, feature-order guessing or probability calibration may occur during rendering/inference.

Bundle provenance should bind model version/checksum, preprocessing/ordered feature schema/types/units/precision, target/eligibility, training and calibration cutoffs/label maturity, source and training-data fingerprints, code/hash, seed/hyperparameters/dependencies, evaluation receipt, intended domain and calibration status. These are proposed sidecar metadata, **not new canonical feature columns**. Input/model version or hash mismatch must withhold output with an actionable error.

Only reviewed server-controlled artifacts may load. No user-selected pickle/joblib or arbitrary model upload. Choose a trusted, validated format/loader in the authorized design and verify its full bundle checksum/version before use; no serialization format or new dependency is installed or approved here. Matching aggregate metrics alone is not estimator integrity. Current dependency pins match prior experiment versions, but platform/numerical parity must still be tested.

## Research outputs and reproducibility

Safest initial output would be **research-only relative future-90-day recorded-inactivity ranking**, not calibrated churn probability. Display alias, as-of cutoff/horizon, eligibility/score meaning, model/schema/data versions, selected historical evidence and uncertainty/coverage limitations. Any score-derived bands require a defined validated protocol; no bands are proposed as approved today.

Use a distinct namespace, e.g. research-scored / unscored-insufficient-history / unscored-invalid-features / unsupported-snapshot. These would be **new research admission labels**, never SUPPORTED/CAUTION/ABSTAIN. Show full and eligible denominators separately, stable alias/tie policy and unsupported reasons. Do not invent individual probability confidence intervals from aggregate bootstrap results.

Reproducibility requires fixed input hashes/order, exactly saved preprocessing/model, frozen dependency/seed settings, stable alias mapping and score-output fingerprints. Learned state is fitted only in the explicitly authorized training stage, never in UI reruns. A future July demonstration must use a model trained without July outcomes; training on July labels then presenting July scores as holdout would be invalid. Prospective scoring does not require future events at inference, but validating the target requires complete matured future follow-up.

Any authorized future derived score receipt belongs in a fresh private research directory, not existing SQLite, manager review events, Phase 9 snapshots/registry, canonical CSV or old acceptance outputs. It may remain entirely in memory. Local aliases/behavioral scores are still sensitive derived profiles; no public release or external APIs are implied.

## Operational boundaries

- G1–G6 and all thresholds/ABSTAIN-over-CAUTION precedence unchanged.
- No score → SUPPORTED conversion, product suggestion, contact approval or financial action.
- No score term in `.45 recency + .35 relationship activity + .20 service issue`, no reordering of the original manager queue.
- No fitted input hidden behind `uses_model_for_action=False`. G3 explicitly rejects unapproved model-driven actions (`engine.py:49`–51); a caller boolean cannot approve a model.
- G4 eligibility, Savings-specific G5 and G6 mandatory human controls remain intact. Even a high research score cannot overcome current restrictions or authorize outreach.
- No existing audit/review/schema/history writes or Phase 9 activation. Avoid store constructors for passive reading: `SnapshotStore` may initialize/recover registry; `AuditStore` may create/configure storage.
- Research scores never enter original Decision Passport or Evidence Replay as approved evidence. No original nine-view integration is needed.

Future regression must retain all 647 cases, exact 50,000-customer digest/priorities/reasons and protected hashes, and add schema/order/preprocessing parity, no-fit-at-inference, missing/out-of-domain/coverage, artifact tampering, repeatability, privacy and namespace/isolation tests. A frozen valid score artifact and source-bound evaluation would be necessary before a research demo; none was generated in Phase 10C.

Research history admission (>=2 events) is the existing experiment's population definition, **not** the operational G2 sales threshold (>=4 for PASS; 2–3 is CAUTION). A numerically scoreable customer may remain CAUTION/ABSTAIN under original gates. Research-scored/unscored counts must never be confused with the 2,052 / 20 / 47,928 permission distribution.
