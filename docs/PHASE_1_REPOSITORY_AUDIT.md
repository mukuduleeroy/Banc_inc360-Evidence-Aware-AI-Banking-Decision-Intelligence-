# Phase 1 — repository and prototype audit

Audit date: **November 16, 2026 (Africa/Harare)**. Scope: existing local repository and supplied competition files. No external services, new dependencies, model training, application changes or dataset replacement were used.

## Executive assessment

Banc-Inc360 is a working **single-screen, deterministic Streamlit prototype**, with a reproducible historical feature extract and a six-gate decision function. It is not yet the nine-page decision-intelligence application described in the requirements. The fresh baseline is **24 tests passed**, five existing AppTest workflow groups passed, and both the existing server and a separate fresh startup returned HTTP 200 health responses.

Passing baseline checks overstate workflow completeness. Across all 50,000 feature rows the engine yields **2,052 SUPPORTED, 20 CAUTION and 47,928 ABSTAIN** cases. However, **every one of the top 1,500 candidates scanned by the default app is ABSTAIN**; the default real-data sales queue is empty. Controlled malformed-input probes also reveal cases that incorrectly remain SUPPORTED. These findings were recorded without fixing application logic in Phase 1.

## Inspected architecture and files

| Path | Actual responsibility |
|---|---|
| `app.py` | Sole Streamlit entry point; all UI, data loading, customer selection, ranking, queue filtering and session audit recording |
| `engine.py` | `Case` dataclass, `evaluate()` function, six gate outcomes, composite priority and nine explicitly synthetic scenarios |
| `build_data.py` | CLI ZIP reader; selects first CSV member, reads 14 fields in 35,000-row chunks, derives customer features and writes audit JSON |
| `tests/test_engine.py` | 23 parameterized test cases, including the original nine tests |
| `tests/test_data.py` | One synthetic chronology/invalid-evidence test |
| `scripts/verify_ui.py` | AppTest helper, outside pytest discovery; five workflow groups |
| `requirements.txt` | Three direct requirements: Streamlit, pandas, pytest |
| `requirements-lock.txt` | 42 installed package version pins; all match the inspected environment |
| `.env.example` | Documents an exported feature-path variable; no automatic dotenv loading |
| `.gitignore` | Excludes local environments, CSV/ZIP data, outputs, secrets and databases |
| `outputs/customer_features.csv` | Sensitive default data input: 50,000 customers, 17 columns |
| `outputs/data_audit.json`, `run_log.txt`, other reports | Earlier generated evidence, not a substitute for this audit's fresh execution |
| `outputs/phase1_audit/` | New ignored audit logs, scripts, aggregate results, a separate rebuild and preservation hashes |
| Root Markdown, PDF and DOCX reports | Documentation/submission evidence; not executable implementations |

There is no `pages/` directory, navigation router, backend service, database adapter, saved model, model registry, training pipeline, prediction-label builder or historical evaluation script. No scikit-learn/DuckDB import is required. NumPy and PyArrow are present as dependencies; SQLite is available in Python but unused by the app.

Data flow: local competition ZIP → `build_data.run()` → feature CSV plus audit JSON → Streamlit CSV loader → `Case` → `evaluate()` → passport and filtered queue. Staff decisions append to `st.session_state.audit` only. No network banking call or customer communication path exists.

## Runtime and configuration

The isolated `.venv` uses Python **3.9.6** on Apple Silicon macOS. Installed versions include Streamlit **1.50.0**, pandas **2.3.3**, NumPy **2.0.2**, PyArrow **21.0.0** and pytest **8.4.2**. `pip check` reports no broken requirements. The lock file is an environment freeze, not a hash-verified portable build specification or a declared supported-Python policy.

`BANCINC_FEATURES_PATH` overrides the default CSV path. The builder separately accepts `--zip`, `--out` and `--cutoff`. The UI **hardcodes July 1, 2026 in its explanatory caption**, does not read a cutoff manifest, and has no source-file hash or snapshot-as-of validation. Cached loading takes no explicit path/version/hash argument, so data replacement/provenance changes need explicit cache invalidation.

The app was already healthy at `http://127.0.0.1:8501`. A separate startup on port 8502 was verified and then stopped; the original instance was left untouched. Browser visual behavior and accessibility were not checked. AppTest executes the Streamlit script/widget runtime without rendering a browser.

## Required capability matrix

Classification covers the requested capability as a whole. A working fragment does not establish a complete page. “IMPLEMENTED BUT UNVERIFIED” is not needed for any whole page here; unverified sub-behaviors are listed explicitly.

| Required capability | Classification | Existing verified evidence and remaining scope |
|---|---|---|
| 1. Executive Overview | **NOT IMPLEMENTED** | No portfolio KPIs, population gate distribution, executive summary or navigation page |
| 2. Customer 360 | **PARTIALLY IMPLEMENTED** | Real customer selection, masked label, historical event count/recency, activity percentile and savings rationale render. No account drilldown, current status/holdings panel, transaction timeline or complete cross-capability profile; selector limited to 250 filtered candidates |
| 3. Inactivity Intelligence | **PARTIALLY IMPLEMENTED** | Historical recency and 90/180-day counts exist; recency contributes to illustrative ranking. No dedicated page, future outcome labels, risk bands with approved definitions, evaluated prediction or engagement trend analysis |
| 4. Relationship Value Intelligence | **PARTIALLY IMPLEMENTED** | Historical absolute transaction volume and its percentile are derived; percentile renders. No value page, multi-indicator explanation, product-breadth display or profitability measure. Snapshot account count must not be called historical value |
| 5. Product Opportunity Intelligence | **PARTIALLY IMPLEMENTED** | Savings gap, repeated-deposit rationale and duplicate-product suppression work on valid inputs. No opportunity page/catalog, broader product policies or robust malformed-holdings handling |
| 6. Decision Passport | **PARTIALLY IMPLEMENTED** | **Implemented and verified fragment:** SUPPORTED/CAUTION/ABSTAIN, all six gate rows, action and aggregate evidence. Missing immutable passport ID, source/cutoff/method versions, exact evidence references, snapshot dates and durable record; G1 largely trusts defaults |
| 7. Evidence Replay | **NOT IMPLEMENTED** | Expandable aggregate JSON is not a replay. No cutoff selector, source-event trace, recomputation comparison or historical/current-state separation during replay |
| 8. Manager Work Queue | **PARTIALLY IMPLEMENTED** | Supported-only filtering and capacity exist. Default real queue is empty because filtering follows a 1,500-candidate cap. No queue-row selection, assignment, stable case identity, triage lanes or durable review lifecycle |
| 9. Audit and Validation Evidence | **PARTIALLY IMPLEMENTED** | Local report/test artifacts and a session audit table exist; a synthetic decision can be recorded. No dedicated evidence page, durable store, authenticated reviewer, versioned validation history or restart persistence |

The displayed source modes are **data-source choices**, not navigation between nine pages. The UI does clearly label its synthetic scenario mode. There is no separate enforced presentation-mode toggle; masking is applied to output customer labels, while the search input echoes entered IDs.

## Decision Integrity Engine assessment

| Gate | Implemented checks | Limits and findings |
|---|---|---|
| G1 | Missing/string-invalid customer IDs; caller flags for bad link/date or future snapshot | App passes a masked ID and leaves validation flags at trusted defaults. No ownership lookup, date/cutoff proof, provenance verification or numeric-domain validation reaches the gate |
| G2 | 0–1 qualifying events → ABSTAIN; 2–3 → CAUTION; 4+ → PASS | Thresholds preserved. NaN event count passes because both comparisons are false; definition depends entirely on upstream builder |
| G3 | Unapproved model blocks if caller requests model-driven action | No model is currently used. Approval is a caller boolean, not an approved-method registry; an approved-model call still gets a “rule-based” reason |
| G4 | Non-Active customer; Frozen/Dormant account; non-Verified KYC block | Valid source restrictions work. Empty/unknown account status can pass if customer/KYC are otherwise valid; snapshot freshness unverified |
| G5 | Only Savings Account, must not be held, must have nonblank rationale | Text existence is not suitability validation. Product parse errors become empty holdings and can yield SUPPORTED |
| G6 | Blocks automatic outreach and disabled human-review/staff-verification flags | No actual automated outreach exists. Staff identity, authorization and successful durable logging are not enforced; review is a stated requirement |

`evaluate()` returns a proposed **staff-review permission**, not lending/insurance approval. It always returns `human_review_required=True`. These controls should be retained while their evidence and input validation are strengthened.

## Ranked gaps

| ID | Priority | Finding and evidence |
|---|---|---|
| F01 | P0 | Malformed product holdings silently become `()`, permitting a savings discussion; synthetic AppTest returned SUPPORTED (`app.py:39`, `app.py:59`) |
| F02 | P0 | Numeric/type/provenance gaps: NaN history and missing account status remain SUPPORTED; G1 flags default to pass (`engine.py:7`, `engine.py:29`, `engine.py:33`, `engine.py:37`) |
| F03 | P0 | Default real queue empty despite 2,052 eligible cases; all top 1,500 are ABSTAIN (`app.py:58`; `queue_checks.json`) |
| F04 | P0 before historical prediction claims | Cohort construction sees post-cutoff customers before ranking percentiles. Synthetic probe changes prior customer's rank from 0.5 to 0.6667. No observed impact in this extract: all 50,000 already have pre-cutoff non-fee history |
| F05 | P1 | Audit identity is only a three-digit customer suffix; all 50,000 customers collide with at least one other customer. No staff identity or persistence (`app.py:73`) |
| F06 | P1 | Feature CSV has no cutoff/provenance contract; hardcoded caption and unversioned cache can misdescribe an imported extract |
| F07 | P1 | No evidence replay, actual historical evaluation, full navigation or executive view; core intelligence remains narrow fragments |
| F08 | P2 | Input type/date errors, unknown transaction types, malformed amounts, unsupported ZIP layout and tie determinism need coverage; baseline does not exercise them |
| F09 | P2 | README incorrectly says no Git repository; imported environment inventory and prior reports can become stale. Non-fatal Streamlit width deprecations remain |

## Preservation and evidence

SHA-256 before/after checks confirm no changes to `app.py`, `engine.py`, `build_data.py`, both existing test files, `scripts/verify_ui.py` or the supplied feature CSV. No changes to data contracts or gate thresholds were made. Fresh rebuilds and controlled synthetic probes live only under ignored `outputs/phase1_audit/`; no synthetic source is substituted into the default feature dataset. The UI helper refreshed its generated `outputs/ui_verification.json`, which is not a dataset.

See [data audit](PHASE_1_DATA_AUDIT.md), [test baseline](PHASE_1_TEST_BASELINE.md) and [implementation roadmap](IMPLEMENTATION_ROADMAP.md). Local aggregate evidence: `data_checks.json`, `edge_probes.json`, `queue_checks.json`, `repository_checks.json`, `rebuild_comparison.json`, `preservation.json` in `outputs/phase1_audit/`.
