# Prototype verification — November 16, 2026 (Africa/Harare)

**Current status:** dependency installation, 24 automated tests, five Streamlit AppTest workflow groups, localhost startup/health and a real-data feature rebuild all succeeded. Browser visual acceptance remains outstanding.

## Architecture and inspected inputs

`app.py` is the Streamlit entry point. `engine.py` evaluates dataclass cases through six deterministic gates. `build_data.py` reads the original ZIP in chunks and writes local feature CSV and audit JSON. There are nine original engine tests. Additional regression tests cover missing identifiers, restricted accounts/customers, history boundaries, missing evidence, unsupported products, required staff control and synthetic point-in-time extraction. No external database, model runtime, DuckDB, scikit-learn, FastAPI or frontend build system is required by the existing implementation.

The directory is not a Git repository. An existing `.venv` was present. There are no project-specific AGENTS instructions. Sensitive data stays local; `.gitignore` was added before any repository initialization.

## Dataset verification

The original ZIP and an extracted CSV were located in the user's Downloads directory. Independently counted the extracted CSV using Python's CSV reader: **1,048,575 transactions, 50,000 unique customers, 98,475 unique accounts, 64 columns**. The supplied customer feature CSV contains **50,000 rows and 17 columns**. The ZIP contains one 633,890,061-byte CSV. Transaction date strings cover **October 1, 2022 through October 30, 2026**. No customer records or identifiers are included in this report. Local count evidence: `outputs/local_dataset_verification.json`.

The originally supplied `outputs/data_audit.json`, `run_log.txt` and `validation_summary.json` were historical package artifacts. Fresh rebuild evidence is stored separately; `validation_summary.json` and `test_results.txt` now reflect the successful November 16 execution.

## Engine verification and changes

All nine synthetic cases produced six-gate passports with expected results in a direct standard-library smoke check: one SUPPORTED, one CAUTION, seven ABSTAIN. Four additional checks blocked invalid ID, Frozen and Dormant accounts and unsupported products. Evidence: `outputs/engine_smoke_verification.json`.

G1 now rejects blank/missing customer IDs. Feature extraction excludes invalid identifiers, invalid links/dates and duplicate transaction IDs instead of counting and retaining invalid evidence. Current restriction aggregation preserves restrictive account and KYC snapshots across rows. G2 remains unchanged: 0–1 events ABSTAIN, 2–3 CAUTION, 4+ pass. G3 blocks unapproved models. G4 suppresses restricted customers, Frozen/Dormant accounts and unverified KYC. G5 blocks already-held products and missing rationale; unsupported products now abstain because the prototype only defines a savings discussion policy. G6 blocks automatic outreach or removal of staff review/verification. No business threshold was changed.

The engine trusts caller-supplied validation flags and the app trusts imported feature files. Full source provenance and import validation remain development work.

## Historical analytics

The feature builder uses transactions strictly before its configured observation cutoff, with 180-day and 90-day lookbacks. Current status/KYC/product fields are kept separate from historical features. Current service issues contribute to the illustrative manager triage score, not a fitted historical prediction. There is no predictive model in the app.

There is **no training/evaluation script, saved model or future inactivity label implementation** in this package. January 1 training, July 1 holdout, 90-day future labels, cohort selection and metric reproduction therefore cannot be verified from existing evaluation code. The supplied data extends far enough to cover a July 1 plus 90-day window, but coverage alone does not reproduce an experiment.

| Metric | Recency baseline (reported only) | Logistic regression (reported only) |
|---|---:|---:|
| ROC-AUC | 0.9406 | 0.5394 |
| PR-AUC | 0.9686 | 0.6129 |
| Precision@500 | 100% | 68% |

These values remain supplied findings, not fresh measurements. No model was approved. Reconstructing the evaluation requires explicit label and cohort definitions; inventing these would not reproduce the original experiment.

## Remaining operational limits

Audit records are held only in session state, with no durable audit database or authenticated staff identity. Manager review records the selected detail case; the queue is a filtered display rather than a selectable review workflow. Only SUPPORTED cases are shown, after examining at most 1,500 prioritized candidates. The customer selector shows at most 250 filtered records. Rationale is exploratory and deposits do not establish salary or product suitability. No automatic outreach, loan approval or insurance approval exists.

No browser automation tool is available in this session. The successful Streamlit AppTest execution verifies script behavior but does not establish visual layout, browser interaction or accessibility. Manual browser acceptance remains required before the presentation.


## Final execution status

All **24 tests passed in 8.09 seconds**, including the nine original engine tests and the synthetic chronology/invalid-evidence regression test. AppTest verified real Customer 360 indicators, the Decision Passport and manager queue; synthetic audit recording; KYC/duplicate-product/restricted-customer suppression; supported-only queue filtering; and missing-file fallback. The helper's import path and dataclass scenario selection were corrected before the successful final run. No application threshold changed.

Streamlit is running at **http://127.0.0.1:8501** and its health endpoint returned `ok`. No browser visual or accessibility testing was performed. Non-fatal Streamlit deprecation warnings remain.

The feature builder was rerun on the original ZIP into `outputs/rebuild_verification/`. It processed 1,048,575 transactions and generated 50,000 customers, with zero invalid links/dates or duplicate transaction IDs. Comparison against the preserved supplied feature file found identical customer keys and zero differences in all 16 non-key columns. Evidence: `outputs/rebuild_verification/data_audit.json`, `outputs/rebuild_comparison.json`, `outputs/ui_verification.json`, `outputs/tests.xml` and the environment/test reports. Historical model metrics remain unreproduced for the reasons above.
