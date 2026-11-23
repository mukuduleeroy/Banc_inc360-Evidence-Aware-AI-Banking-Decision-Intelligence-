# Phase 9 controlled local demonstration

Use authorized local files only. The provided examples are wholly invented and require no restricted customer data. The accepted nine-page application and the Phase 9 companion are separate local interfaces by design.

## Start the original application

From the repository, in one terminal (choose unused port and fresh audit filename):

```bash
cd /Users/user/Documents/BancInc360_Final
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
BANCINC_AUDIT_DB=outputs/phase9/original-demo-new.sqlite3 \
.venv/bin/python -m streamlit run app.py \
  --server.address 127.0.0.1 --server.port 8510 \
  --server.headless true --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8510`. Confirm 50,000 customers and 2,052 / 20 / 47,928 outcomes. Do not point this demonstration at an existing protected audit database.

## Open Dataset Ingestion & Refresh

In a second terminal:

```bash
cd /Users/user/Documents/BancInc360_Final
BANCINC_RUNTIME=LOCAL \
.venv/bin/python -m streamlit run phase9_app.py \
  --server.address 127.0.0.1 --server.port 8511 \
  --server.maxUploadSize 5 \
  --server.headless true --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8511`. The 5 MiB server cap is mandatory; the interface refuses uploads without it. The default private store is `outputs/phase9/private/`. A server-controlled `BANCINC_PHASE9_STORAGE` may select a new isolated Phase 9 store, never canonical directories or old audit folders. The code refuses unmanaged nonempty directories and symlinks. Neither accepted application navigation nor its loader is modified.

## Demonstration sequence

1. Keep observation date **2026-07-01**.
2. Upload `outputs/phase9/examples/synthetic-valid.csv` and click **Validate upload**. Inspect fingerprint, detected/required fields and passed validation.
3. Click **Process validated dataset**. Show 14 accepted source rows, four customers/accounts, no excluded rows and exact decision reconciliation. Processing creates a candidate and does not activate it.
4. Click **Preview candidate snapshot**. Show **1 SUPPORTED / 1 CAUTION / 2 ABSTAIN**, limited alias-only table and actual six-gate explanations. Inspect another alias if useful.
5. Read the prototype-policy/no-banking-authorization disclosure. The outcomes are staff-review permissions, not customer offers.
6. Click **Activate validated preview snapshot**. Show the active companion snapshot ID and local provenance events. Original application remains on its accepted dataset.
7. Click **Return to accepted baseline**. Companion preview returns to 50,000 / 2,052 / 20 / 47,928; original data was not rewritten. The candidate remains preserved for inspection/re-activation.
8. Upload `synthetic-invalid-date.csv`, click Validate and show blocked processing. Also demonstrate `synthetic-unsupported-currency.csv` and `synthetic-missing-fields.csv` if needed. Invalid uploads never produce activatable snapshots.
9. Use **Discard staged upload** to explicitly clear failed/private staging data. Successful processing and upload/date changes also clean their generated staging files.
10. Return to the original application to inspect unchanged passport/replay/manager workflow. No real customer communication is possible through the new feature.

Examples already exist with a README under `outputs/phase9/examples/`. If that folder is absent on another checkout, generate it once with `.venv/bin/python phase9_demo.py`. The generator refuses existing CSV files instead of overwriting them. It reads no competition records.

Stop each server with Ctrl-C in its own terminal. The automated acceptance servers were already stopped; this guide does not imply any preview is currently running.

## Integrity and test receipts

Read-only canonical verification:

```bash
.venv/bin/python -c 'from acceptance_checks import verify_local_baseline; print(verify_local_baseline())'
```

Fresh complete regression (choose a new output directory; never overwrite a previous run):

```bash
BANCINC_AUDIT_DB=/private/tmp/bancinc-phase9-rerun-new.sqlite3 \
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python phase9_acceptance.py \
  --out-dir outputs/final_acceptance/phase-9-rerun-new
```

Final reports: 05 (tests), 06 (baseline invariance), 08 (acceptance). Real synthetic browser receipts/screenshots are in `outputs/phase9/browser_verified/`; original nine-page/restart receipts are in `outputs/phase9/original_app_browser/`.

## Limits to explain honestly

Compatible USD-normalized transaction CSV only, 5 MiB/25,000 rows, 50-alias preview. No automatic FX conversion, arbitrary schema mapping, supplier authenticity certification, live model inference, production database/authentication or bank approval. Current snapshot dates remain unknown. Registry recovery may return the prior committed selection; inspect active state before re-activating. Local storage is owner-trusted and unencrypted. No public deployment or external data transmission is authorized.
