# Phase 7 visual and functional validation

Date: 2026-11-18, Africa/Harare. Existing local Python 3.9.6, Streamlit 1.50.0, Chrome and Node. No new dependency, font download or public data deployment.

## Exact tests

Baseline command:

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase7/baseline_tests.xml
```

**291 passed in 65.41s** before visual changes.

Final full regression:

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase7/tests.xml
```

**308 collected; 308 passed in 72.17s; 0 failures, errors, skips or pytest warnings.** Full log: `outputs/phase7/test_execution_final.log`; XML: `outputs/phase7/tests.xml`. All 291 baseline case identifiers are retained. An earlier integration run passed 307 tests before the final style-scope regression was added; the final count is 308. No prior test was removed, skipped or weakened in Phase 7.

New tests: ten token contrast pairs, semantic non-color statuses, offline/responsive/focus CSS, theme-token agreement, escaped gate markup/status preservation, non-mutating privacy-safe replay markup, independent-student identity and sidebar-caption scope isolation. A small final correction targeting the visible native select focus container passed all **17 design tests in 0.25s** (`focus_final_tests.log`). This was a presentation selector change only; banking/review logic remained untouched.

## Browser/layout checks

Local-only preview command used:

```sh
env DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL BANCINC_AUDIT_DB=outputs/phase7/visual_demo.sqlite3 .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8507 --server.headless true --browser.gatherUsageStats false
```

Existing isolated Chrome listens on localhost CDP 9225. Verification:

```sh
node scripts/verify_phase7_visual.mjs
```

The script expects the local preview above and existing Chrome; BANCINC_PREVIEW_URL/BANCINC_CDP_URL can override them. It captures all nine routes at 1440, 1280, 768 and 390px, with 1080px viewport height. This is CSS viewport emulation in desktop Chrome, not testing on physical mobile hardware. Gate cards are two-column on desktop and stacked on smaller content widths; native tables retain internal scrolling.

Final evidence is in `outputs/phase7/responsive/visual_validation.json`, `responsive_final_execution.log` and 36 viewport PNGs. Acceptance requires no application exception, primary-document horizontal overflow, clipped metric value or clipped button; visible student identity and header clearance; six gate cards on Passport/Queue; and completed-render markers. Main-caption color was inspected as rgb(82,102,118), matching the reading token. Eight native Tab focus samples record focus outlines; this is keyboard sampling, not exhaustive keyboard/screen-reader certification.

The first screenshot pass exposed the fixed-header overlap and a caption-scope inconsistency; both were corrected with regression evidence. A subsequent rerun during concurrent cold validation exceeded the initial 45-second browser wait; inspection showed the page ultimately rendered without exceptions. The bounded harness allowance was increased. Some early captures included Streamlit stale/loading overlays; final capture explicitly waits for spinner, stale and running markers to clear. These earlier captures are diagnostic evidence, not the final presentation set. No business condition or render error was bypassed.

## Workflow and persistence

```sh
.venv/bin/python scripts/accept_phase5.py --out outputs/phase7/acceptance-new --port 8508 --cdp-port 9226
```

Choose an unused output directory. The already-executed run is `outputs/phase7/acceptance/`. The existing helper initializes an isolated managed DB, starts a separate server/browser, checks nine pages and KYC replay/reset, records a real-supported local demo review with explicit reviewer/reason/acknowledgement, stops/restarts that server, and verifies persisted history. It cleans up only its own processes.

Actual result: APPROVED_LOCAL survived restart, with one case, OPEN/APPROVE events, two snapshots and sixteen FEATURE_LEVEL references. Demo actor is DEMO_UNVERIFIED; bank_authorization and automatic_outreach remain false. Actual screenshots include `review_approved.png`, `review_after_restart.png` and `audit_after_restart.png`. Dataset hash and previous Phase 4 database summaries were unchanged. Evidence: `acceptance.json`, `browser_create.json`, `browser_reopen.json`, `browser_verification.json` and logs under that directory.

Replay: real baseline SUPPORTED → explicitly SIMULATED Pending KYC ABSTAIN → reset SUPPORTED. The visual transition/evidence comparison reads existing engine outputs; it does not change source features or create actionable simulation records. No communication or banking API was added.

## Screenshots

Final private presentation selection is indexed under `outputs/phase7/presentation_evidence/README.md`. Full responsive captures remain under `outputs/phase7/responsive/`; workflow captures under `outputs/phase7/acceptance/screenshots/`.

Required scenes: Executive Overview, Customer 360, six-gate Passport, replay baseline/Pending/reset, Manager Work Queue, committed manager review and audit after actual restart. Representative desktop/tablet/mobile images were visually inspected in addition to automated layout checks. Screenshots are viewport captures, not full-page exports; they contain aliases and derived competition information and must remain private unless release permission covers them.

## Limits and readiness

Ten token contrast combinations meet at least 4.5:1, but that does not certify all browser/native-component states. Native table canvases, full assistive-technology behavior, arbitrary zoom, touch ergonomics, all browser engines and physical devices were not comprehensively tested. Long axis text can shorten; full text is available through tooltips/data tables. Wide tables scroll internally. Inter is not bundled; system fallback is intentional. Style selectors should be revalidated after Streamlit upgrades.

Ready for the scoped local hackathon presentation, with the functional and visual evidence recorded here. No official branding, production authentication, regulatory compliance, tamper-proof audit, transaction-level replay or public real-data readiness is claimed. The existing confidentiality and cloud-ephemeral-storage warnings remain in force.
