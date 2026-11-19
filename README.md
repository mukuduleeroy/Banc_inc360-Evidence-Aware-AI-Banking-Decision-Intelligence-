# Banc-Inc360 — evidence-aware banking decision MVP

Streamlit-native nine-view prototype for portfolio oversight, Customer 360, observed inactivity, relationship activity, savings opportunities, six-gate Decision Passports, controlled Evidence Replay, manager review and validation evidence. All actions require staff review; no automated outreach or financial approvals.

Phase 2 baseline verified November 16, 2026: **124 tests passed**, complete queue evaluated across **50,000** real customer rows, **2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN**, and the corrected source rebuild matched canonical features. See `docs/PHASE_2_IMPLEMENTATION_REPORT.md` and the other Phase 2 reports.

Phase 3: **182 tests passed**; all nine views rendered in Chrome, with native navigation, real-data analytics and a separately labeled non-actionable simulation. Engine/data-layer code and the canonical feature file remain unchanged. See `docs/PHASE_3_IMPLEMENTATION_REPORT.md`, `docs/PHASE_3_UI_VALIDATION.md`, `docs/PHASE_3_DATA_METRICS.md` and `docs/PHASE_3_PRESENTATION_WALKTHROUGH.md`.

Phase 4: **229 tests passed**. Durable SQLite cases, explicit unverified demo reviewers, immutable application events/passport snapshots and stale-evidence blocking are implemented. An actual Streamlit restart preserved a local approval. See [implementation](docs/PHASE_4_IMPLEMENTATION_REPORT.md), [schema and backup](docs/PHASE_4_AUDIT_SCHEMA.md), [workflow](docs/PHASE_4_REVIEW_WORKFLOW.md), [validation](docs/PHASE_4_VALIDATION_REPORT.md) and [presentation](docs/PHASE_4_PRESENTATION_SCENARIO.md). Verified preview: `http://127.0.0.1:8503`. Approval remains local only.

Phase 5: **261 tests passed**; historical inactivity evaluation reproduced twice with identical metrics, all-nine-page browser acceptance and actual review persistence after restart passed. Experimental models remain offline and do not authorize actions. See [evaluation](docs/PHASE_5_EVALUATION_REPORT.md), [acceptance](docs/PHASE_5_SYSTEM_ACCEPTANCE.md), [performance](docs/PHASE_5_PERFORMANCE_REPORT.md), [presentation runbook](docs/PHASE_5_PRESENTATION_RUNBOOK.md) and [limitations](docs/PHASE_5_LIMITATIONS_AND_PROVENANCE.md).

Normal presentation startup: `.venv/bin/python scripts/presentation.py start` → http://127.0.0.1:8505. Initialize once with `scripts/presentation.py init`; reset explicitly with `scripts/presentation.py reset` after stopping the server. Reset retains previous database generations and backups. Evaluation dependencies are optional in `requirements-evaluation-lock.txt`; the application runs without them.

## Local setup

Use an isolated environment. This workspace has Python 3.9.6; the dependency resolver selects compatible releases. Python 3.12 or 3.13 is preferred for a future environment refresh if available.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -v
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

On Windows use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. `requirements.txt` records direct dependencies (Streamlit 1.50 minimum for the table width API used here); `requirements-lock.txt`, when generated, records the verified environment.

## Data configuration

The default is `outputs/customer_features.csv`. Set `BANCINC_FEATURES_PATH` to override it:

```sh
export BANCINC_FEATURES_PATH=/absolute/path/to/customer_features.csv
```

`.env.example` documents the variable; the app does not automatically load `.env`. Missing features stop real-data loading with an actionable error; synthetic gate demonstrations require deliberate selection or DATA_MODE=DEMO. Invalid schema or unreadable features produce a coded error. A matching `.manifest.json` sidecar is required for real recommendations; missing/mismatched provenance withholds all sales cases.

Rebuild from the authorized original ZIP:

```sh
.venv/bin/python build_data.py --zip /absolute/path/to/dataset.zip --out outputs/rebuilt-new --cutoff 2026-07-01
```

Use a new output directory: the builder refuses to overwrite an existing feature CSV. Its matching sidecar records the source/features hashes and cutoff. For historical features the builder excludes transactions at or after the cutoff, invalid links/dates/identifiers, unknown types, non-finite amounts and duplicate transaction IDs; future-only customers do not enter the historical cohort. History uses the preceding 180 days; older events can inform recency. Current holdings, customer/account status and KYC are separate snapshot suitability inputs. Service issues are a current triage input; neither the triage score nor activity percentile is a predictive probability or profitability measure.

## Structure and verification

- `app.py`: Streamlit entry point, customer indicators, passport, filtered queue and session audit.
- `engine.py`: deterministic G1–G6 evaluation and nine synthetic demonstration cases.
- `build_data.py`: chunked ZIP CSV extraction and local data audit.
- `tests/`: engine policy and synthetic chronological feature tests.
- `scripts/verify_ui.py`: Streamlit AppTest workflow verification; run with `.venv/bin/python scripts/verify_ui.py`.
- `outputs/`: sensitive local features and verification artifacts, excluded from Git.

History policy is unchanged: 0–1 events ABSTAIN, 2–3 CAUTION, 4+ pass. Only SUPPORTED cases enter the sales review queue. Savings Account is the only product with a prototype discussion policy; other products abstain. Staff must verify suitability. No model is approved or used for actions.

## Privacy and limitations

Never commit datasets, customer features, local databases or secrets. `.gitignore` excludes these files, but cannot protect files already tracked; Git now exists, so verify tracked paths and history before distributing artifacts. Customer IDs are masked in the UI. Free-text staff notes must avoid sensitive information. Audit records exist only in Streamlit session state and are lost on session reset; no durable audit or identity/access controls are implemented.

The queue examines the top 1,500 candidates before gate filtering. The customer selector exposes up to 250 filtered candidates. Current snapshots cannot establish historical eligibility. Model comparison values in the submission are reported findings, not independently reproduced metrics. See the verification reports for tested scope.

## Troubleshooting

Use the virtual environment interpreter for every command. For download timeouts retry pip with `--timeout 180 --retries 5`. If the data file is missing, configure its path or rebuild it; synthetic demos are not substitute banking evidence. If port 8501 is busy add `--server.port 8502`. Stop Streamlit with Ctrl-C.
# Banc_inc360-Evidence-Aware-AI-Banking-Decision-Intelligence-
# Banc_inc360-Evidence-Aware-AI-Banking-Decision-Intelligence-

## Phase 2 provenance, validation and identity

`evidence.py` is the central validation layer; `data_access.py` builds the complete immutable decision index and cached content-based imports. Required columns remain unchanged. Unknown states/holdings, invalid numeric evidence and conflicting product gaps fail closed with reason codes. All occurrences of duplicate IDs are quarantined; missing history is never imputed to zero. Status/product labels normalize only exact known case/whitespace variants. The current recognized portfolio labels are documented in the Phase 2 implementation report.

For an existing canonical CSV without a manifest, compare a fresh source build first:

```sh
.venv/bin/python scripts/reconcile_phase2.py --zip /absolute/path/to/dataset.zip --features outputs/customer_features.csv --out outputs/phase2/recheck-new
```

Choose a previously unused output directory. The script never replaces the canonical CSV. If values differ, review the comparison and obtain approval before a separate replacement. If identical, it creates the matching missing manifest; a different existing manifest is not overwritten. Manifests are trusted local build evidence, not bank-signed attestation; snapshot effective dates remain unknown.

Presentation aliases share one private deterministic mapping across queue, selector, passport and session notes. The random local key is generated once at ignored `outputs/.presentation_alias_key` (0600 permissions). Keep it private and preserve it for stable aliases. A detected collision blocks import; missing/rotated keys produce a new mapping. Raw IDs are not searchable/displayed by the UI. Data, manifest, key and policy/code changes invalidate the two-entry in-process index cache.

Reproduce current queue evidence:

```sh
.venv/bin/python -m pytest -v -ra
.venv/bin/python scripts/compare_phase2.py --baseline-ref 01b2729
.venv/bin/python scripts/verify_ui.py
```

The supplied-data regression explicitly skips only when authorized local features are absent; present features require verified provenance. Synthetic tests/scenarios remain separately labeled. No ML approval, authenticated staff authorization or automatic action is implemented. Durable local audit is described in the Phase 4 reports.

## Nine-view workspace

`app.py` registers native `st.navigation` pages under `views/`. Shared shell/components live in `ui_shell.py`, `ui_components.py` and `ui_views.py`; descriptive analytics are isolated in `analytics.py`. The Phase 2 engine/index remains the only permission authority. Aliases follow the customer across pages. The analytics outcome filter applies to charts/tables; full-population KPIs and manager lanes keep their own declared scopes.

The Relationship Value view explains the existing observed-volume percentile proxy; it is not profitability or lifetime value. Inactivity is observed historical recency/frequency, not a trained future prediction. Savings gaps are candidate evidence only; every actionable review case still requires SUPPORTED.

Evidence Replay uses `replay.py` to copy permitted evidence fields, revalidate and compare actual engine gates. Changes are explicitly SIMULATED, resettable, non-actionable and never written to the dataset or review notes. Original lineage failures cannot be erased. Synthetic demonstration mode is a separate workbench with no real portfolio KPIs.

Audit & Validation Evidence parses recorded JUnit/report artifacts rather than hardcoding a test count. Missing or stale reports are unavailable/historical, not passing certification. Legacy session review notes remain non-durable; Phase 4 local review events use SQLite and do not constitute authenticated approval.

Reproduce UI evidence and actual aggregate metrics:

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase3/tests.xml
.venv/bin/python scripts/verify_ui.py
.venv/bin/python scripts/report_phase3_metrics.py
```

The separately verified local preview is `http://127.0.0.1:8502`. Browser screenshots and a Chrome/CDP verification helper are documented in the Phase 3 walkthrough; they use existing Chrome and Node, with no new package. All artifacts/screenshots stay in ignored outputs and should be reviewed before external sharing.

## Phase 6 deployment data safety

Use explicit `DATA_MODE=LOCAL`, `DEPLOYED` or `DEMO` (LOCAL is the compatible default). Public demo: `DATA_MODE=DEMO`, `BANCINC_RUNTIME=CLOUD`. Real deployments require verified written BancABC permission, a privately provisioned versioned artifact and configured fingerprint/version/alias secret. Missing real data never silently becomes demo. Cloud SQLite is labeled ephemeral; local audit remains unchanged. No competition data was published. See [deployment audit](docs/PHASE_6_DEPLOYMENT_AUDIT.md), [parity evidence](docs/PHASE_6_DATA_PARITY_REPORT.md) and [configuration guide](docs/PHASE_6_DEPLOYMENT_GUIDE.md). A nonsecret template is in `.streamlit/secrets.example.toml`; never commit actual secrets or private_data.

## Phase 7 visual refinement

The original student prototype now uses centralized banking-blue design tokens, accessible reading/status colors, a clear independent-student identity, responsive KPI/gate cards and labeled replay comparisons. No official bank assets or external font dependencies were added. **308 tests passed**, all 291 previous cases retained; 36 route/viewport combinations passed at 1440/1280/768/390px, and local review survived an actual server restart. Protected engine, data, review and evaluation artifacts remain unchanged.

See [visual audit](docs/PHASE_7_VISUAL_AUDIT.md), [design system](docs/PHASE_7_DESIGN_SYSTEM.md), [implementation](docs/PHASE_7_IMPLEMENTATION_REPORT.md) and [validation](docs/PHASE_7_VISUAL_VALIDATION.md). Private captures are indexed at `outputs/phase7/presentation_evidence/README.md`. Local visual preview: http://127.0.0.1:8507 (isolated visual-demo database). Public competition-data release remains unauthorized.

## Mandatory final regression and gate protection

Every integrated improvement must pass the complete regression suite and source-bound acceptance before presentation. Run `.venv/bin/python scripts/run_final_regression.py --out-dir outputs/final_acceptance/run-new` with an unused directory. The runner rejects failures, errors, skips, removed baseline tests, changed source/JUnit evidence and unexpected full-population decision changes. Experimental models remain offline; product suggestions and scores cannot bypass G1–G6. See [protection requirements](docs/DECISION_INTEGRITY_PROTECTION.md) and [final acceptance](docs/FINAL_ACCEPTANCE_REPORT.md). This is local technical acceptance, not production authorization or permission to publish competition data.
