# Phase 3 — complete banking intelligence interface

Completed **November 16, 2026 (Africa/Harare)**. The Phase 2 baseline was verified locally before editing: **124 tests passed in 12.59 seconds**, with 50,000 evaluated customers and the reported decision distribution reproduced.

## Architecture and preservation

The existing `app.py` command remains the entry point. It now owns a Streamlit-native `st.navigation` / `st.Page` shell. Nine small scripts under `views/` route to rendering functions in `ui_views.py`; a separate synthetic demonstration route is registered only in synthetic mode.

- `ui_shell.py`: source/provenance indicators, shared alias search/selection and durable session selection state.
- `ui_components.py`: native wrapping metric cards, accessible chart labels/data tables, pagination, passport presentation and session review notes.
- `analytics.py`: deterministic descriptive aggregations over the authoritative Phase 2 index. Its public frames omit raw customer IDs and unrestricted free text; callers receive detached frames.
- `replay.py`: isolated permitted counterfactuals routed through `row_case()` and the unchanged engine. Simulated output is explicitly marked non-actionable.
- `validation_evidence.py`: reads internally reconciled JUnit counts and checks source-rebuild reports against the loaded dataset hash. Missing/stale evidence is not presented as verified.
- `.streamlit/config.toml`, `assets/brand.svg`: native navy/teal/light theme, presentation toolbar and local vector branding. No unsafe HTML, remote fonts or CSS layout hacks.

**`engine.py`, `evidence.py`, `data_access.py`, `build_data.py`, the canonical feature CSV and its manifest are byte-for-byte unchanged from the start of Phase 3.** The index's complete evaluation, gates, historical thresholds, cache keys and aliases remain authoritative. No dependency was installed or added; charts use existing Altair 5.5.0, already supplied by Streamlit and pinned in the lock file. No model, database, authentication or external banking API was introduced.

The Phase 2 policy fingerprint remains `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`. Dataset SHA-256 remains `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. Preservation proof and case-inventory comparison: `outputs/phase3/preservation.json`.

## Page-by-page status

All nine real-data views are **implemented and verified** with AppTest and rendered Chrome navigation. This describes the scoped interface, not production banking readiness.

| View | Implemented behavior |
|---|---|
| Executive Overview | Full-population permission KPIs, typed-evidence quality, observed engagement, descriptive relationship segments, savings ownership and overlapping abstention reasons; analytics outcome filter is explicitly scoped |
| Customer 360 | Alias search/shared selection, recency and frequency, observed volume, activity percentile, account/product breadth, current status/KYC, rationale and linked passport/replay |
| Inactivity Intelligence | Exact observed-recency definition, cutoff/lookbacks, recency/frequency distributions, descriptive filters, pagination and customer drilldown; no future prediction claims |
| Relationship Value Intelligence | Existing volume-percentile proxy, formula and tie/rounding explanation, descriptive segments, current breadth, ranking and drilldown; no profit/revenue/lifetime-value claim |
| Product Opportunity Intelligence | Savings ownership gaps, recorded rationale, engine-supported staff-review candidates, separate already-held/unknown-ownership contexts and passport links; no offer/contact action |
| Decision Passport | Selected alias, actual G1–G6 engine rows, reasons/codes, candidate action, evidence, method/policy/data provenance and required staff action; existing session notes retained |
| Evidence Replay | Real selected baseline plus explicitly SIMULATED KYC/account/history/holdings inputs, side-by-side engine outcomes, changed gates, reasons and reset. No transaction-history reconstruction or action authorization |
| Manager Work Queue | Complete Phase 2 index, supported staff-review lane, separate CAUTION/ABSTAIN investigations, full counts, stable filtering/pages, selected passport and session notes |
| Audit & Validation Evidence | Matching source/build fingerprints and row counts, current decision distribution, parsed test reports, cutoff assumptions, known limitations and session notes |

## Shared state and safety

Customer aliases are the only identity in rendered customer tables and selection controls. A durable `selected_alias` state is separate from widget cleanup, so navigation preserves the customer's identity. Table/queue buttons explicitly select their customer before opening a native page. Alias search can reach any customer; only the first 50 matches are offered at a time for efficiency, and an empty search result retains the existing selection with an explanation.

The sidebar's analytics outcome filter affects analytical charts/tables only. Full-portfolio KPIs and manager queue lanes retain their own clearly labeled scopes. Page size is shared; eligibility always precedes pagination. No displayed portfolio number is populated with synthetic examples.

Synthetic mode registers a separately labeled demonstration workbench and suspends real portfolio analytics. Missing data offers that explicit fallback; a malformed real schema produces the centralized coded error rather than invented metrics.

Session review notes retain source, alias, dataset/policy identifiers and outcome. They persist across navigation but remain session-only, with no authenticated approval. Changing customer clears the draft reason to prevent accidental cross-customer reuse. Replay has no review-note or customer-action control and cannot save overrides as real facts.

## Evidence Replay semantics

Only KYC status, account status, historical qualifying-event count and portfolio holdings may be overridden. Other fields, identity, lineage and control flags are rejected as simulation inputs. Overrides are applied to a copy, passed through centralized validation and evaluated by the engine. Missing/unrecognized states and malformed evidence still abstain; source-lineage failures cannot be erased. Derived product gap is recalculated when simulated holdings change. Subwindow/deposit counts remain fixed, so an inconsistent simulated total also fails G1 rather than being silently reconciled to force an outcome.

The browser demonstration began with a genuinely SUPPORTED selected customer. SIMULATED Pending KYC produced ABSTAIN through G4; Reset returned the unmodified SUPPORTED baseline. Unit/AppTest checks also cover frozen accounts, insufficient/invalid counts, already-held savings, reset, customer changes and forbidden overrides. Even a simulated SUPPORTED result has `action_authorized=False`. The canonical file and real decision index do not change.

## Performance and design

The Phase 2 content/policy-aware decision cache is reused. A navigation regression proves all nine views do not trigger another full 50,000-case sweep; only selected passports/replay inputs may be re-evaluated. The two-entry descriptive profile cache is lazy and separate from policy. Large customer tables are filtered/paginated before display, and charts receive small aggregate tables.

Native wrapping containers replaced fixed KPI columns after browser inspection found truncation at a narrow viewport. At 768×1024, the final check found no clipped metric values or document-wide horizontal overflow. The 1440×1080 desktop views also had no document-wide horizontal overflow. Wide tables can scroll internally. Status text accompanies color, every chart has an accessible data table and controls have descriptive labels. This is measured browser/layout verification, not formal WCAG certification.

## Files and verification

New application files: `analytics.py`, `replay.py`, `ui_shell.py`, `ui_components.py`, `ui_views.py`, `validation_evidence.py`, nine `views/*.py` routes plus `views/synthetic_demo.py`, `.streamlit/config.toml`, `assets/brand.svg`.

Updated: `app.py`, `scripts/verify_ui.py`, README. Added helpers: `scripts/report_phase3_metrics.py`, `scripts/verify_browser.mjs`. New tests: `test_analytics.py`, `test_navigation.py`, `test_replay.py`, `test_report_evidence.py`. The four existing cases in `test_ui_validation.py` were adapted only to navigate to the queue before their original safety assertions; all 124 Phase 2 case identities remain present. No existing case was removed, skipped or weakened.

Final automated result: **182 passed, 0 failures, 0 errors, 0 skipped, 0 pytest warnings**, in **34.38 seconds**. All standalone UI verification groups passed. Chrome rendered all nine pages without application exceptions and exercised KYC simulation/reset. Screenshots remain in ignored local outputs; no sensitive screenshot is automatically published.

See [UI validation](PHASE_3_UI_VALIDATION.md), [data metrics](PHASE_3_DATA_METRICS.md) and [walkthrough](PHASE_3_PRESENTATION_WALKTHROUGH.md). Phase 4 should implement durable case/passport/reviewer-linked audit records and transaction-level evidence traceability; unknown snapshot dates, authentication and model evaluation remain explicit limits.
