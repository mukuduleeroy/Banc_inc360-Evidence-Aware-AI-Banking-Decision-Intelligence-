# Implementation roadmap — presentation-ready Banc-Inc360

Plan date: **November 16, 2026 (Africa/Harare)**. Target presentation: November 20. This is a plan only; Phase 1 did not implement the changes below. Sequence is ordered by safe delivery value, not a promise of fixed-duration completion.

Keep the existing Python/Streamlit architecture, three direct dependencies, six gate names and SUPPORTED/CAUTION/ABSTAIN outcomes. Preserve all 24 passing tests and the current 0–1 / 2–3 / 4+ history policy. Reuse the 50,000-row competition features; keep synthetic demonstrations isolated. No lending/insurance approvals, automatic outreach or live banking APIs are in scope.

## Phase 2 — trustworthy inputs and a working real-data queue (next)

**Purpose:** repair the safety and demonstration blockers before expanding UI scope.

**Files to modify/create:** `app.py`, `engine.py`, `build_data.py`, `tests/test_engine.py`, `tests/test_data.py`, `scripts/verify_ui.py`, `README.md`; a small shared `data_access.py` for consistent CSV/holdings validation and case construction, plus `tests/test_data_access.py` and `tests/test_queue.py` if extraction improves testability. Avoid a larger service layer.

**Features:**

- Validate one customer per row, real internal identifiers, finite nonnegative counts/recency, percentile within 0–1, booleans and current-status enums. Treat missing/invalid evidence as unknown and ABSTAIN with actionable reasons.
- Parse holdings once through a strict shared helper. A parse failure must never become proof of an empty portfolio. Use the same construction path for detail and queue.
- Keep raw internal keys separate from collision-resistant display aliases. Run G1 before masking; no raw ID in rendered passport, queue or screen-sharing search labels.
- Evaluate eligibility across the population before applying the review capacity, or scan until capacity is filled. Remove the semantic dependence on a top-1,500 pre-filter cap. Add deterministic tie ordering using internal keys, not ambiguous aliases.
- Bind each import to a verified sidecar manifest: cutoff, source hash, qualifying-event definition version, feature schema version, build version and snapshot-as-of/unknown status. Include the manifest/file version in cache keys. Replace the hardcoded cutoff caption.
- Separate observation-time cohort construction from present-day snapshot checks; use a documented historical cohort for percentiles. Validate type/amount/ownership before deduplication and before counting events.
- Represent method approval as explicit trusted configuration. Leave ML unapproved; accurate G3 reasons must distinguish rule and approved-model paths.

**Data dependencies:** current feature CSV, original ZIP, current audit JSON, source account ownership columns and current snapshot domains. Snapshot effective dates are not supplied; preserve “unknown” freshness rather than inventing it.

**Contract justification:** preserve the existing 17 CSV columns and types. Introduce a versioned companion manifest rather than silently inserting mandatory columns. A stricter import policy changes invalid-input behavior deliberately and must be documented. If the temporal-cohort fix changes values on future data, record the definition/version and comparative evidence; do not overwrite existing features without a separate verified build. Do not change history thresholds or broaden product eligibility.

**Acceptance criteria:**

- All current 24 tests remain passing; malformed holdings, NaN numeric evidence and unknown account state fail closed.
- Valid competition cases retain current permission results unless an explicitly documented validation rule requires otherwise.
- A full-population reference evaluation and the UI use identical case construction. Supported cases beyond candidate 1,500 can enter the queue; the current default dataset must produce a nonempty eligible queue up to configured capacity, not the present false-empty state.
- Altering only post-cutoff event/customer rows cannot alter historical features or cohort ranks. Changing current snapshots can change current eligibility but cannot change historical predictors.
- Imported cutoff/provenance is verified or visibly unavailable with actions withheld. Existing artifacts remain readable for inspection without being silently trusted for sales eligibility.
- Display aliases are unique for this dataset; audit actions retain internal identity locally without exposing it in the UI.

**Tests to add:** malformed/null/incorrect-shape holdings, missing/duplicate IDs, NaN/infinity/negative/out-of-range evidence, status/boolean normalization, unknown types/bad amounts, ownership conflicts, invalid-first duplicate, exact cutoff/180-day/90-day boundaries, future-only cohort invariance, current-snapshot independence, cached-file replacement, manifest mismatch, deep-queue eligible case and tie stability.

**Risks/safeguards:** stricter validation may reduce eligibility; report reasons and compare counts rather than loosening controls to populate the queue. Preserve existing source files, write new builds under ignored outputs, verify hashes, keep bank policy assumptions explicit and retain controlled synthetic cases for unavailable evidence.

## Phase 3 — coherent navigation and the three intelligence capabilities

**Purpose:** turn verified fragments into a clear demonstration journey.

**Files:** `app.py`; a small `ui_views.py` containing render functions; optional `analytics.py` for shared aggregate calculations; `scripts/verify_ui.py`; `tests/test_analytics.py`; existing README/report documents. Use the installed Streamlit API; avoid a new frontend framework or duplicated page-specific engines.

**Features:** add sidebar navigation for all nine named views while retaining existing detail/passport/queue behavior. Executive Overview shows real population totals, date coverage, permission counts and limitations. Customer 360 shows historical indicators alongside separately labeled current status/KYC/holdings and account breadth. Inactivity shows recency/event coverage and descriptive engagement bands with explicit definitions. Relationship Value shows activity, transaction volume and product breadth with rationale; do not call activity profit or current breadth historical. Product Opportunity shows the savings-only supported policy, gaps and suppression reasons. Decision Passport shows all gate inputs, outcomes, policy version, method, cutoff and evidence references. Evidence Replay/Audit views must clearly identify incomplete backends until Phase 4 is complete.

**Data dependencies:** Phase 2 validated feature loader/manifest and full-population gate outputs. Optional live source-event drilldown waits for Phase 4; do not invent events from aggregates.

**Acceptance:** each named view is reachable, uses the same selected internal customer and shared gate function, distinguishes historical/current/synthetic evidence, and explains why an action is supported or withheld. Portfolio counts reconcile to 50,000 rows and the engine. No unsupported sales case is enabled through a different page. Initial render/refresh is suitable for the presentation machine; cache aggregate results by data/version rather than repeatedly re-evaluating all customers on every widget change.

**Tests:** all routes render for real and synthetic sources; displayed numeric metrics reconcile to features; population gate totals reconcile; selected customer survives navigation; status/holdings reason text matches G4/G5; no raw identifiers in presentation outputs; empty/search-error states are understandable. Extend AppTest to inspect contents, not merely dataframe existence.

**Risks/safeguards:** nine thin views can exaggerate capability; label descriptions and experimental indicators honestly. Do not attach predictive probabilities or profit labels to descriptive measures. Preserve the current session workflow while adding navigation incrementally.

## Phase 4 — evidence replay, manager case workflow and durable audit

**Purpose:** make staff review traceable and survive application restart.

**Files:** `app.py`, `ui_views.py`, `engine.py` (passport metadata only), new focused `evidence_store.py` and `audit_store.py`, `build_data.py` only if an optional evidence sidecar is required, `tests/test_replay.py`, `tests/test_audit_store.py`, `tests/test_queue.py`, `scripts/verify_ui.py`, `.gitignore` only if new storage suffixes require exclusion.

**Features:**

- Build a local indexed evidence sidecar from the original source, using standard-library SQLite if useful. Store source event references/derived totals needed for replay under ignored outputs. Keep the original customer feature contract intact.
- Replay the selected customer's eligible transaction evidence at a cutoff, recompute event/volume/recency facts and compare to the stored feature version. Show excluded fee/future/invalid evidence reasons, with masked references.
- Generate immutable passport/case identifiers and record cutoff, data/feature/policy/method versions, gate inputs/results and current snapshot freshness separately.
- Make queue rows selectable and attributable. Provide SUPPORTED review and separate CAUTION/ABSTAIN investigation paths without turning investigation into a sales permission.
- Persist a deliberate staff decision with local reviewer identifier, internal case key, timestamp, reason and passport snapshot/hash. Use transactional SQLite writes, show write errors, and do not report successful recording before commit. A typed demo reviewer name is attribution, not authenticated authorization; label that limitation until real identity controls exist.
- Add an Audit and Validation Evidence view for current fresh validation results, source/build versions and review history.

**Data dependencies:** original ZIP, validated cutoff manifest, stable case identity, approved evidence retention scope and local writable storage. Source snapshots have no reliable effective-date history; replay must not imply historical KYC/holdings reconstruction.

**Acceptance:** replayed facts match the selected feature build; future rows never enter historical facts; current suitability is explicitly dated or marked unknown. Decisions survive a fresh Streamlit process/session, remain associated with the right internal customer despite masking, and include immutable passport evidence. Restricted customers cannot enter sales actions. Database errors never produce false audit-success messages. No communications or financial approvals are triggered.

**Tests:** replay cutoff and fee/type boundaries, exact feature reconciliation, missing source and stale manifest, alias-collision attribution, database restart persistence, transaction rollback/write failures, two-session writes, required reviewer/reason, immutable passport linkage and investigation-versus-sales behavior.

**Risks/safeguards:** local audit/evidence databases are sensitive and are not a production access-control solution. Keep them ignored, least-access on the presentation machine, exclude raw IDs from display/export, avoid unchecked free-text PII, document retention and include no database in the repository. Do not describe an append-only local table as tamper-proof.

## Phase 5 — historical evaluation and approved-method evidence (conditional)

**Purpose:** substantiate inactivity performance if experiment definitions can be established. This is not a prerequisite for demonstrating honest descriptive/rule-based intelligence.

**Files:** new `evaluate_history.py`, small `tests/test_evaluation.py`, `build_data.py` only for reusable point-in-time functions, `ui_views.py` for reported-versus-reproduced results, report documents. Keep artifacts ignored. Do not add scikit-learn merely to display prior figures; propose a dependency only if an actual logistic-regression experiment is required and justified.

**Features/data:** define inactivity outcome and qualifying event policy explicitly; freeze historical cohorts; create January 1 training and July 1 holdout observations, each with 180-day eligibility history and 90-day future labels. Specify whether dates are interval endpoints and how customer overlap is handled; report that overlap rather than calling it an unseen-customer split. Use only observation-time features and separate labels. Evaluate a transparent recency baseline first. Compare any fitted model with documented preprocessing, training-only fitting, exact cohort sizes, label prevalence and uncertainty. An ML model is not approved by its presence or by matching a reported number.

**Acceptance:** reproducible ROC-AUC, defined PR-AUC method and Precision@500 with explicit tie rules, cohort counts and date coverage. Differences from 0.9406/0.9686/100% (recency) or 0.5394/0.6129/68% (logistic) are investigated and reported, not edited away. Approval remains withheld until an explicit trusted method policy permits use. If definitions/time are insufficient, retain the original figures as reported only and keep current rule-based actions.

**Tests:** observation/label separation, cutoff-day exclusion, full future-window availability, preprocessing fit boundaries, snapshot and future-cohort invariance, metric edge cases/class imbalance, ranking ties and model-approval control.

**Risks/safeguards:** false reproduction from invented cohorts or ambiguous PR-AUC definitions is worse than an honest limitation. Do not infer salary, suitability, propensity or uplift from deposit frequency; do not retrofit results to the concept paper.

## Phase 6 — presentation acceptance and evidence freeze

**Files:** `scripts/verify_ui.py`, README and verification reports, lock file only if intentionally refreshed, optional `docs/PRESENTATION_RUNBOOK.md`. No infrastructure redesign.

**Features:** fix compatible Streamlit width deprecations with an explicit minimum-version decision, verify actual browser layout/keyboard use, rehearse the real customer → three intelligence views → passport → replay → review → persisted audit journey, then show clearly labeled synthetic restriction/model/human-control failures. Update stale Git/runtime statements and link fresh evidence with execution dates. Keep a small preflight/startup command and a local data configuration checklist.

**Data dependencies:** verified local artifacts from prior phases and a private presentation dataset location. No data or databases in Git or publicly distributed archives.

**Acceptance/tests:** rerun the complete pytest suite and content-based AppTests; test missing-file fallback and fresh startup; reconcile portfolio/queue counts; manually verify browser, masking, navigation and persistence on the actual machine. Capture aggregate/fully masked acceptance evidence. Record exact test totals, warnings, versions and remaining limitations. Freeze code/data/policy hashes and provide an honest demo script.

**Risks/safeguards:** do not spend the remaining presentation window on unvalidated ML or cosmetic expansion while safety/queue failures persist. Keep the existing rule-based walkthrough available. Never mark absent replay/persistence/evaluation as complete.

## Recommended sequencing before November 20

Complete **Phase 2 first**, then a minimal Phase 3 navigation journey, then Phase 4 traceability and replay. Perform Phase 6 rehearsal regardless of whether conditional Phase 5 finishes. If time becomes constrained, retain clearly labeled reported model metrics and descriptive intelligence; explicitly mark unfinished capabilities. Release readiness depends on measured acceptance criteria, not the number of pages created.
