# Actionability, ingestion and technical interface audit

## Actionable business insights: MET at local decision-support scope

`engine.evaluate` (`engine.py:30`) supplies exact priority and gates; `data_access.build_index` (line 163) ranks cases by unrounded priority descending then alias. The .45 recency / .35 activity-percentile / .20 current-service-issue score is a review priority, not predicted churn/profit/expected response. `ui_views.manager_work_queue` (`ui_views.py:194`) evaluates eligibility before filters/pagination; SUPPORTED is the default lane, with CAUTION/ABSTAIN available separately.

- **SUPPORTED (2,052):** all six gates pass; eligible for staff review only. Local review options Approve, Defer, Reject. APPROVED_LOCAL is not bank authorization or contact permission.
- **CAUTION (20):** borderline historical evidence without another blocking gate; investigate manually, defer or reject; no local approval.
- **ABSTAIN (47,928):** at least one blocking gate; withhold sales. A selectable manual lane and the same limited Defer/Reject review interface exist, but no automated remediation, assigned investigation pipeline, KYC resolution/inactivity treatment plan or task SLA is implemented for all 47,928.

`review_service.open_case` (`review_service.py:146`) creates OPEN or INVESTIGATION_REQUIRED state; `record_review` (line 173) requires explicit demonstration reviewer, reason, inspected current snapshot and acknowledgment. `ui_review.render_workflow` (`ui_review.py:48`; options at line 81) reflects these restrictions. Current fingerprints/policy/decision hash, expected revision and idempotency checks prevent stale or conflicting review reuse; append-only application events/snapshots/references preserve local history. Fingerprint freshness means changed content/version detection, not a verified wall-clock KYC expiry policy. Current snapshot dates remain unknown, so staff must still verify real eligibility.

Existing end-to-end evidence is `outputs/phase9/original_app_browser/acceptance.json` and browser create/reopen receipts: one case, two events, two snapshots, 16 feature references survived an actual process restart. Native/service tests include `tests/test_review_service.py::test_supported_review_persistence_snapshot_and_feature_refs`, `test_non_supported_cannot_approve_but_can_defer`, `test_stale_fingerprints_block_until_explicit_refresh`; `tests/test_durable_ui.py::test_real_supported_review_survives_new_app_session_and_auditor_view`. These workflows were **not run** during this audit.

No actual customer communications, account action, product purchase, lending approval or financial transaction executes. Reviewer labels are unverified demo attribution; local SQLite is owner-trusted/unencrypted, cloud local storage ephemeral. Evidence traceability is feature-level, not source-event-level reconstruction. No measured retention, revenue, product-uptake improvement or controlled business pilot was found. The platform produces reviewable insights; business outcomes remain unproven.

### Why 95.856% ABSTAIN?

47,928 / 50,000 = **95.856%** is the final sales-permission withholding share, not churn rate or model uncertainty. Actual reason counts among ABSTAIN cases:

| Reason code | Customers (overlapping) | Meaning |
|---|---:|---|
| CURRENT_RESTRICTION | 39,928 | Current account/customer state or KYC prevents sales |
| NO_BEHAVIOURAL_EVIDENCE | 27,483 | Existing Savings rationale missing |
| HISTORY_INSUFFICIENT | 17,391 | 0–1 qualifying events in window |
| PRODUCT_ALREADY_HELD | 10,000 | Savings already owned |
| HISTORY_BORDERLINE | 1,134 | Caution on history accompanies some other blocking gate |

These counts overlap and must not be summed as unique customers. All canonical evidence is typed/valid; invalid/quarantined canonical records are zero. Therefore withholding is largely policy/eligibility/product evidence, not widespread data corruption. A HISTORY_BORDERLINE code by itself yields CAUTION, not ABSTAIN. Executive Overview's reason chart (`analytics.reason_distribution`, line 57; `ui_views.py:51`) correctly includes caution reason codes that coexist with a blocker.

Only **23** supported customers are in Higher activity, and **546** supported customers have historical recency >90 days. SUPPORTED is neither high commercial value nor an estimated conversion/uplift population. It means evidence-compatible staff review under a narrow prototype policy.

## Phase 9 ingestion/reusability: MET for its documented compatible local scope

Exact code: `phase9_ingestion.py:15` SOURCE_FIELDS, `:46` validate_csv, `:120` SnapshotStore, `:210` process, `:246` _verify, `:269` inspect, `:271` activate, `:275` rollback; `phase9_app.py:84` decision preview and `:106` management. A separate companion, **not a tenth page in the original app**.

| Item | Verified implementation / limitation |
|---|---|
| Formats | UTF-8 optional-BOM CSV only; uploaded ZIP/Excel/arbitrary schemas unsupported |
| Schema | 14 required transaction fields, optional Currency; exact list in `phase9_ingestion.SOURCE_FIELDS` and `docs/phase-9/03_DATASET_CONTRACT.md`; names/meaning verified against original builder |
| Validation | Missing/duplicate/unknown columns, IDs/ownership, invalid dates/types/amounts, conflicting transactions, unsupported currencies, size/row/field limits fail closed; repeated customers/accounts are valid; exact duplicate transactions explicitly audited/deduplicated |
| Units | Amount (USD) must already be normalized; optional Currency must equal USD; no FX conversion or assurance of upstream rates |
| Limits | 5 MiB, 25,000 rows, 2,048 chars/field; absolute numeric amount <=1e12 as demo admission bound; server `--server.maxUploadSize 5` required, otherwise uploader disabled |
| Unknown eligibility | Blank/unknown KYC/status and blank holdings remain unknown; existing engine abstains; no fabricated defaults |
| Processing | Internally package staged compatible CSV as a single-CSV ZIP; call unchanged `build_data.run` in a new private directory; call unchanged `load_index` with separate Phase 9 alias key; output 16-column contract unchanged |
| Reconciliation | Source/accepted/duplicate/excluded counts, customers/accounts, evaluated count, exact SUPPORTED+CAUTION+ABSTAIN and coverage recorded; unexpected exclusions or lineage failures block candidate registration |
| Snapshot | New ID, content hashes, source/ZIP/feature association, policy/code provenance and decision digest; hash-checked logical immutability |
| Activation | Explicit action updates only companion registry; inspection verifies content/policy/reconciliation; failed activation retains prior active state |
| Rollback | Explicit companion return to accepted baseline; no regeneration/canonical writes |
| Original dashboards | **Do not automatically switch.** `app.py:11`–24 retains original deployment loader; companion registry is not consumed by it |
| Companion preview | Alias table limited to first 50 engine-ranked customers, actual gates/lineage; not all nine dashboards on uploaded data |
| Demo evidence | Existing 14-row/four-customer independent synthetic CSV, one SUPPORTED/one CAUTION/two ABSTAIN; browser CREATE→ACTIVATE→ROLLBACK_BASELINE, rejected invalid date, no exceptions/outreach controls |

Existing outputs verified read-only: `outputs/phase9/browser_verified/acceptance.json`, `browser_result.json`, private registry and one stored candidate. Registry currently records baseline after CREATE/ACTIVATE/ROLLBACK. Candidate inspection used read-only artifact/index access, **not SnapshotStore construction**, because initialization/recovery can write state. No new upload, processing, registry mutation or temporary output was created.

Tests: `tests/test_phase9_ingestion.py` (59), `tests/test_phase9_ui.py` (6), `tests/test_phase9_protection.py` (5); existing accepted receipt records all 70 passing. Unknown supplier authenticity, real-world data-use permission and production security remain outside this local compatibility proof.

## Nine original views and technical quality

| View / renderer in `ui_views.py` | Actual capability | Limitation or demo note |
|---|---|---|
| Executive Overview / `executive_overview:23` | Full-population counts, activity/ownership/decision charts and overlapping reason codes | Not measured business uplift or a predictive performance dashboard |
| Customer 360 / `customer_360:58` | Selected alias, historical activity, known products/current status, source segment, Passport/replay links | Current effective dates unknown; activity not profitability |
| Inactivity / `inactivity_intelligence:86` | Recency/history/segment/outcome filters, pagination, historical ML panel | No live per-customer churn probability |
| Relationship Value / `relationship_value:106` | Global activity percentile, volume/breadth/account context, source-segment/activity filters | No explicit economic high-value classifier |
| Product Opportunity / `product_opportunities:118` | Savings gap/held/unknown lanes and authoritative eligibility explanation | No upsell; selected customer outside filter remains selected explicitly |
| Decision Passport / `decision_passport:134` | Six gates, reasons, method/provenance, session notes and durable review | Local prototype permission, not bank authorization |
| Evidence Replay / `evidence_replay:144` | Counterfactual KYC/status/history/ownership, changed gates, reset | Simulation, not transaction replay; no real review writes |
| Manager Work Queue / `manager_work_queue:194` | Engine-first lane filtering/pagination, customer navigation, local review status and workflow | Not an automatic campaign or full investigation platform |
| Audit / `audit_validation:224` | Manifest/rebuild provenance, historical experiment, audit timeline and recorded test evidence | Test list is hardcoded to older phase files; latest displayed phase7 JUnit is **308**, not current **574** |

Navigation/selection: `ui_shell.PAGES` (line 10), `selection_controls` (line 44), `app.py:29`–48; native pages retain selected alias, existing per-page pagination resets and filters. Charts: `ui_components.bars:33`; global KPI/filter scope is explicit. Tests: all-nine navigation, alias search/selection continuity, privacy, paging, replay/reset, stale evidence and storage failure tests in the current hash-bound 574-case receipt.

Existing browser evidence: Phase 9 verifies all nine views and review restart; Phase 8B responsive report has 27 view/viewport checks at 1440/768/390; Phase 7 has 36 at 1440/1280/768/390. The accepted original view source/design bytes still match. Companion three-width browser samples also have no overflow/exceptions. These are prior recorded functional/layout checks, not a live audit run today or formal accessibility certification.

### Demo-critical cautions

Show the separate latest acceptance receipt for 574 tests; do not imply the Audit page already loads it. Launch the companion separately with required upload cap; do not search original navigation for it or promise dashboard-wide dataset switching. Use independent synthetic inputs for ingestion, clearly label replay and offline models, and disclose missing upselling/value limits. Current port availability, deployment permissions and live cloud real-data parity were not checked and remain UNVERIFIED. No discovered source-integrity drift prevents the local recorded demo; business completeness remains the main risk.
