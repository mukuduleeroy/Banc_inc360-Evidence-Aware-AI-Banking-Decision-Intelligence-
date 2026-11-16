# Banc-Inc360 — evidence-aware banking decision MVP

Local Streamlit prototype for Customer 360, transparent relationship activity indicators, six evidence gates, Decision Passports and a manager review queue. All actions require staff review; no automated outreach or financial approvals.

Verified November 16, 2026: dependencies installed, 24 tests passed, Streamlit AppTest workflows passed, and the source-data feature rebuild matched the supplied features. See the environment and verification reports for details.

## Local setup

Use an isolated environment. This workspace has Python 3.9.6; the dependency resolver selects compatible releases. Python 3.12 or 3.13 is preferred for a future environment refresh if available.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -v
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

On Windows use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. `requirements.txt` records direct dependencies; `requirements-lock.txt`, when generated, records the verified environment.

## Data configuration

The default is `outputs/customer_features.csv`. Set `BANCINC_FEATURES_PATH` to override it:

```sh
export BANCINC_FEATURES_PATH=/absolute/path/to/customer_features.csv
```

`.env.example` documents the variable; the app does not automatically load `.env`. Missing features produce guidance and clearly labeled synthetic gate demonstrations. Invalid schema or unreadable features produce an error.

Rebuild from the authorized original ZIP:

```sh
.venv/bin/python build_data.py --zip /absolute/path/to/dataset.zip --out outputs --cutoff 2026-07-01
```

The builder excludes transactions at or after the cutoff, invalid links/dates/identifiers and duplicate transaction IDs. History uses the preceding 180 days; older events can inform recency. Current holdings, customer/account status and KYC are separate snapshot suitability inputs. Service issues are a current triage input; neither the triage score nor activity percentile is a predictive probability or profitability measure.

## Structure and verification

- `app.py`: Streamlit entry point, customer indicators, passport, filtered queue and session audit.
- `engine.py`: deterministic G1–G6 evaluation and nine synthetic demonstration cases.
- `build_data.py`: chunked ZIP CSV extraction and local data audit.
- `tests/`: engine policy and synthetic chronological feature tests.
- `scripts/verify_ui.py`: Streamlit AppTest workflow verification; run with `.venv/bin/python scripts/verify_ui.py`.
- `outputs/`: sensitive local features and verification artifacts, excluded from Git.

History policy is unchanged: 0–1 events ABSTAIN, 2–3 CAUTION, 4+ pass. Only SUPPORTED cases enter the sales review queue. Savings Account is the only product with a prototype discussion policy; other products abstain. Staff must verify suitability. No model is approved or used for actions.

## Privacy and limitations

Never commit datasets, customer features, local databases or secrets. `.gitignore` excludes these files, but cannot protect files already tracked; this directory currently has no Git repository. Customer IDs are masked in the UI. Free-text staff notes must avoid sensitive information. Audit records exist only in Streamlit session state and are lost on session reset; no durable audit or identity/access controls are implemented.

The queue examines the top 1,500 candidates before gate filtering. The customer selector exposes up to 250 filtered candidates. Current snapshots cannot establish historical eligibility. Model comparison values in the submission are reported findings, not independently reproduced metrics. See the verification reports for tested scope.

## Troubleshooting

Use the virtual environment interpreter for every command. For download timeouts retry pip with `--timeout 180 --retries 5`. If the data file is missing, configure its path or rebuild it; synthetic demos are not substitute banking evidence. If port 8501 is busy add `--server.port 8502`. Stop Streamlit with Ctrl-C.
# Banc_inc360-Evidence-Aware-AI-Banking-Decision-Intelligence-
