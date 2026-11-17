# Phase 3 — UI, test and browser validation

Executed November 16, 2026 (Africa/Harare), on the existing Python 3.9.6 / Streamlit 1.50.0 environment. No new testing or visualization package was installed.

## Exact automated results

**182 tests collected; 182 passed; 0 failed; 0 errors; 0 skipped; 0 pytest warnings.** Terminal and JUnit duration: **34.38 seconds**. The case-inventory comparison confirms every one of the **124 Phase 2 cases** remains; 58 new cases cover the interface, analytics and simulation. Four pre-existing UI cases now explicitly navigate to the native queue; their fail-closed assertions remain.

| Test module | Cases |
|---|---:|
| `test_analytics.py` | 21 |
| `test_navigation.py` | 19 |
| `test_replay.py` | 16 |
| `test_report_evidence.py` | 2 |
| Existing `test_cohort.py` | 16 |
| Existing `test_data.py` | 1 |
| Existing `test_engine.py` | 23 |
| Existing `test_evidence.py` | 52 |
| Existing `test_queue.py` | 27 |
| Existing `test_real_data.py` | 1 |
| Existing `test_ui_validation.py` | 4 |

Coverage includes all nine native routes; shared alias selection/search; real KPI reconciliation; detached privacy-safe analytics; segment boundaries; product/held-product suppression; passport/engine equality; complete queue pages and drilldown; session-note continuity/draft reset; permitted and forbidden replay inputs; simulated failure/reset/customer-change behavior; unchanged canonical data; graceful missing/invalid features; internally reconciled report counts; stale source reports; and no repeated full portfolio decision sweep while navigating.

No line-coverage percentage or new model-performance result is claimed. Earlier development runs passed 178, 180 and 181 cases while coverage was expanded. Initial integration defects in an Altair width keyword and the standalone AppTest navigation helper were corrected; no failing test was disabled. AppTest's explicit page selection is needed after a button triggers `st.switch_page`, because its subsequent run does not automatically retain the browser's URL hash.

## Commands

From `/Users/user/Downloads/BancInc360_Final`:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase3/tests.xml > outputs/phase3/test_execution.log 2>&1
.venv/bin/python scripts/verify_ui.py > outputs/phase3/ui_verification.log 2>&1
.venv/bin/python scripts/report_phase3_metrics.py > outputs/phase3/metrics.log 2>&1
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false > outputs/phase3/startup.log 2>&1
node scripts/verify_browser.mjs > outputs/phase3/browser_verification.log 2>&1
git diff --check
```

The untouched initial baseline was 124 passed in 12.59 seconds. Local server, Chrome and CDP connections required sandbox escalation. Browser automation used the already-installed Chrome executable plus Node's built-in WebSocket/CDP support, not Playwright/Selenium or a new dependency. The script expects a fresh Chrome instance listening only on localhost port 9222; see the walkthrough for browser launch instructions.

Standalone AppTest groups all pass: nine routes, actual KPI reconciliation, nonempty complete queue and page two, alias/passport/note consistency and blank-reason rejection, replay/reset/no-action/canonical preservation, separately labeled synthetic failures, and missing-file fallback. Bare-mode ScriptRunContext messages are harness log advisories, not pytest warnings or application exceptions.

## Browser results

All nine native sidebar links were clicked in Chrome at **1440×1080**. The driver waited for each page's final content marker and expected tables before capturing it. No application exception or document-wide horizontal overflow was detected. The Audit page parses both the available Phase 3 and historical Phase 2 test artifacts rather than assuming a passing count.

The browser selected **SIMULATED Pending KYC** on Evidence Replay: baseline SUPPORTED → simulated ABSTAIN → Reset SUPPORTED. No review-note action control was present on that view. AppTest separately verifies no changed source file or session note from simulation.

At **768×1024**, the overview had **zero clipped metric values**, zero document-wide horizontal overflow and no application exception after the native wrapping-card correction. Phone widths below this, arbitrary zoom settings, assistive technologies and formal accessibility conformance were not comprehensively tested.

The Chrome verification profile is isolated under `/private/tmp/bancinc-phase3-chrome`. Its screenshots/report contain aliases, aggregate metrics and permitted evidence only. No raw customer/account ID is intentionally rendered. Customer identity columns are tested to contain only `C-` aliases. Numerical activity values are not claimed to be anonymized banking records.

## Local screenshots

Screenshots are actual viewport captures, **not full-page images**. They remain under ignored `outputs/phase3/screenshots/`; review before sharing externally.

- [Executive Overview](../outputs/phase3/screenshots/executive_overview.png)
- [Customer 360](../outputs/phase3/screenshots/customer_360.png)
- [Inactivity Intelligence](../outputs/phase3/screenshots/inactivity_intelligence.png)
- [Relationship Value Intelligence](../outputs/phase3/screenshots/relationship_value.png)
- [Product Opportunity Intelligence](../outputs/phase3/screenshots/product_opportunities.png)
- [Decision Passport](../outputs/phase3/screenshots/decision_passport.png)
- [Evidence Replay baseline](../outputs/phase3/screenshots/evidence_replay.png)
- [Replay with Pending KYC](../outputs/phase3/screenshots/evidence_replay_pending.png)
- [Replay after Reset](../outputs/phase3/screenshots/evidence_replay_reset.png)
- [Manager Work Queue](../outputs/phase3/screenshots/manager_work_queue.png)
- [Audit & Validation Evidence](../outputs/phase3/screenshots/audit_validation.png)
- [768-pixel overview](../outputs/phase3/screenshots/overview_narrow.png)

## Evidence and limits

Raw artifacts: `outputs/phase3/tests.xml`, `test_execution.log`, `ui_verification.log`, `browser_verification.json`, `browser_verification.log`, `metrics.json` and `preservation.json`. Protected engine, validation/index, builder, feature CSV and manifest hashes are unchanged. All 124 old case IDs are present in the final suite.

A healthy server and screenshots do not establish production authorization, durable audit or model reliability. Current snapshots still lack effective dates. Session notes disappear when the session/process resets. Test artifacts are local recorded evidence, not signed certification; the UI labels historical runs accordingly. No production banking action was tested or connected.
