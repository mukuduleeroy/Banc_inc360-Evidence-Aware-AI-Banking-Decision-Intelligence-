# Phase 6 deployment audit

Inspected 2026-11-18 (Africa/Harare). Scope: existing local repository plus read-only public GitHub and live Streamlit inspection. No deployment, push, data upload or publication was performed.

## Root cause: observed runtime path failure plus automatic fallback

Live URL: https://mukuduleeroy-banc-inc360-evidence-aware-ai-banking-d-app-mvaava.streamlit.app/

The live application iframe displayed **“Customer features not found. Configure BANCINC_FEATURES_PATH or rebuild from the authorized source. Synthetic demonstrations remain available.”** Its only data-source choice was Synthetic gate demonstrations. This warning uniquely corresponds to the old `if not path.is_file()` branch in `app.py`. That same condition restricts navigation to the synthetic page. Therefore the immediate observed cause is an absent/unresolvable configured feature path, followed by automatic synthetic-only navigation—not an engine disagreement or a 50,000-row filtering problem.

Repository evidence independently establishes a provisioning gap: `outputs/`, every `*.csv` and every `*.zip` are ignored; `git ls-files outputs` and tracked data-file queries return no customer feature artifact or companion manifest. Deployment from the code tree alone cannot reproduce the local data. The default application path was already based on ROOT and portable; the optional BANCINC_FEATURES_PATH could override it with a local-machine absolute path. Environment variables on the developer's machine are not a cloud data transport. No bootstrap downloader or packaged approved artifact exists. The build script needs the authorized source ZIP and writes local outputs; it is not invoked by app startup.

The current public repository is `mukuduleeroy/Banc_inc360-Evidence-Aware-AI-Banking-Decision-Intelligence-`, default branch `main`; local HEAD, local origin/main and read-only `git ls-remote origin refs/heads/main` matched **ab02f09bc78d7e809ee22cb25f0819680151f16d** before Phase 6 edits. Entry point under inspection is `app.py`. The observed live UI matches that entry point's guard. Private Community Cloud deployment settings, exact checked-out commit, secret overrides and logs are not accessible from the public page; the live configured branch/commit and precise resolved path remain unverified. An incorrect absolute override cannot be excluded. No claim is made that cloud secrets were read.

Local inspection found no BANCINC/DATA_MODE/STREAMLIT configuration environment keys, no project `.streamlit/secrets.toml` and no user-global Streamlit secrets file. `.streamlit/config.toml` contains visual/runtime presentation settings, not data provisioning. `requirements.txt` and `requirements-lock.txt` are tracked and were preserved. The running live demo proves a functioning app runtime; dependencies do not account for this missing-file branch.

Read-only evidence: `outputs/phase6/deployed_frame.json`, `deployed_before.png`, `deployed_inspection.log`, `deployed_http.txt`. The Streamlit wrapper body is empty; the app is in its same-origin `/~/+/` iframe. Initial top-level text inspection therefore did not see the warning; iframe inspection confirmed it. HTTP redirect headers alone do not establish app/data health.

## Data safety: publication blocked

The supplied `BancABC 2026 Universities Hackathon Participants Terms and Conditions.pdf`, section 11, states that datasets remain BancABC property, are competition-purpose-only and cannot be copied, distributed, published or shared outside the competition without written approval. It says they **may** be masked/anonymised/synthetic; that is not certification that this particular extract is safe to publish. Local text extraction is in ignored `outputs/phase6/competition_terms.txt`.

Source fields include customer/account/transaction identifiers, email, legal name, national/registration identifiers, mobile, date of birth, income and balances. The derived 17-column feature artifact removes many direct fields but still contains raw customer_id, holdings, status/KYC and financial behavioural measures. Its small size (6,603,715 bytes) does not confer publication permission. Pseudonymous UI aliases do not make the underlying file public-safe. Fixed 20/21 transactions per customer suggest artificial construction, but cannot prove absence of actual or restricted customer information.

No written approval covering this artifact, hosting provider and audience was found in the project material. No data was unignored, committed, uploaded or released. A configuration approval-reference string is an operator assertion after actual document review, not authorization from BancABC or a cryptographic proof. Do not set it merely to bypass the gate.

## Changes

- New `deployment_data.py`: centralized environment/Streamlit-secrets resolution; explicit modes; ROOT-based paths; deployed release hash/version/schema/provenance checks; unchanged-engine index generation; stable secret-key restoration with conflict blocking; cloud audit path semantics.
- Updated `app.py`: no automatic demo fallback. Missing real inputs show an actionable coded error; selecting demo is deliberate.
- Updated `ui_review.py`: centralized portable audit configuration, automatic SQLite initialization and explicit ephemeral-cloud/local-storage notices.
- Added `.streamlit/secrets.example.toml`; ignored real Streamlit secrets, secret variants and private_data; expanded `.env.example` and README guidance.
- Added `scripts/verify_deployment_parity.py` and deployment tests; adapted one legacy fallback assertion and the standalone UI helper to the explicitly requested new no-fallback behavior. No old test identifier was removed.
- Three Phase 6 reports. UI Audit also reads Phase 6 JUnit when available.

Protected engine, evidence validation, feature/index layer, analytics, builder, replay, review service, audit schema, canonical CSV and canonical manifest remain byte-identical. No dependency or banking policy changed. Version metadata for emulation was written only to a separate ignored local manifest copy.

## Persistence

The existing SQLite schema initializes missing databases safely; no cloud copy of a developer's database is required. Local audit paths and historical events are preserved. CLOUD defaults to a fresh repository-relative `outputs/cloud_review.sqlite3` and visibly declares it ephemeral. Community Cloud local files can disappear across restarts/redeployments. Do not claim cloud durability, and do not mistake explicit demo attribution for authentication. No production database was introduced.

Official references: [Community Cloud file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), [secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), [local-file persistence limitation](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data). These deployment behaviors were checked against official documentation on the audit date.

## Open operational work

An owner must inspect the app's configured repo/branch/entry point, runtime path and secret names; obtain written permission before moving competition features to any external host; choose a bank-approved private environment/audience; provision the reviewed artifact and secrets; then publish the reviewed code and run live parity acceptance. None of those external steps is implied by local parity evidence. Until then the public deployment should remain explicitly DEMO, not claim 50,000 live rows.
