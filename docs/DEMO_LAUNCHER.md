# Local three-app demo launcher

Verified 2026-11-23. From the repository root:

```bash
./scripts/start_demo.sh
```

Optional macOS browser opening: `./scripts/start_demo.sh --open-browser`.

- **MAIN:** http://127.0.0.1:8514
- Dataset Ingestion & Refresh: http://127.0.0.1:8511
- Business Capability Companion: http://127.0.0.1:8515

The main default follows the latest accepted Phase 11 runbook (8514), rather than the older README presentation-manager port 8505. All nine native pages, names/order and state management remain intact. The two external `st.page_link` links appear after the existing sidebar controls, separated under ADDITIONAL CAPABILITIES; installed Streamlit 1.50 opens them in separate tabs. Long labels wrap within only this new section. No iframe or application merge.

## Configuration and ownership

The executable shell script finds its own repository root and uses that repository's `.venv/bin/python`; it works when called from another directory. No installation or dependency change. Actual entrypoints are app.py, phase9_app.py and phase10b_app.py. Phase 9 retains its required `--server.maxUploadSize 5`. All servers bind 127.0.0.1.

Existing environment configuration is inherited. Optional main port override: BANCINC_DEMO_MAIN_PORT, then STREAMLIT_SERVER_PORT, otherwise 8514. Companion ports stay 8511 and 8515. Sidebar URL overrides are BANCINC_INGESTION_URL and BANCINC_BUSINESS_URL; defaults are the URLs above. Only HTTP(S) URLs without embedded credentials are accepted. Invalid overrides produce a sidebar configuration warning. Overrides change links, not application routing or data.

A fresh private temporary run directory holds logs and default disposable state. Its physical path is resolved because Phase 9 deliberately rejects symlinked storage roots (macOS /var resolves to /private/var). BANCINC_AUDIT_DB and BANCINC_PHASE9_STORAGE are preserved when explicitly supplied; otherwise they point to fresh original-review.sqlite3 and ingestion subpaths outside the repository. For protected-history rehearsals, leave these unset or point to new disposable storage. Explicit existing storage may be initialized by the existing apps; choose overrides deliberately. Main data-mode/path/secrets behavior is unchanged, with no silent demo fallback.

Launcher checks all ports before starting anything, never terminates an existing listener, waits up to 60 seconds total for the three health endpoints, prints URLs and monitors children. `--timeout SECONDS` changes the bounded health deadline. SO_REUSEADDR handles recently closed sockets consistently with Streamlit; it does not enable sharing a live listener. A bind race or subsequent child failure is reported with its private log path and tears down owned services.

Ctrl+C, TERM and HUP trigger cleanup of owned process groups, with bounded TERM wait and KILL escalation only for those groups. No broad termination commands. Logs and disposable state remain for inspection; the launcher never resets reviews, processes uploads or activates snapshots. Health success alone is not proof that an application has completed UI rendering.

## Focused verification

Final command, using external audit state and no caches/model-fitting tests:

```bash
PYTHONDONTWRITEBYTECODE=1 BANCINC_AUDIT_DB=/private/tmp/bancinc-launcher-acceptance-review.sqlite3 .venv/bin/python -B -m pytest -q -p no:cacheprovider   tests/test_demo_launcher.py   tests/test_navigation.py::test_all_nine_native_pages_load   tests/test_navigation.py::test_alias_search_and_selection_survive_navigation   --basetemp=/private/tmp/bancinc-launcher-acceptance-tests   --junitxml=/private/tmp/bancinc-launcher-acceptance-tests.xml
```

**20 passed, no failures/errors/skips.** Tests cover all nine native routes and selection retention, default/custom/invalid links, no accidental port-value output, finite timeout validation, live-listener preservation, shell syntax and physical default-storage resolution. Existing tests/expectations were not edited. Full suites that fit estimators were not run; the prior 647-test receipt remains historical and is not claimed to cover this change.

Fresh headless-Chrome checks rendered all nine original views, checked link destinations/new-tab targets on each, and exercised Replay Pending KYC/reset. Actual clicks opened both companions in separate tabs. Phase 9 rendered through Audit and Provenance in fresh disposable storage; no upload or activation was needed. Business companion retained SYNTHETIC UPSELL DEMONSTRATION ONLY / DEMO_ELIGIBLE_FOR_REVIEW and the non-operational disclaimer. Narrow main viewport at 768 had no outer overflow or Streamlit exception. New sidebar screenshots were visually inspected. This is technical automation, not a human presentation rehearsal or projector certification.

Lifecycle checks: Ctrl+C returned 130 with all three listeners removed; TERM returned 143, all three recorded owned PIDs gone; forced 0.001-second health deadline returned 1 with cleanup and no listeners. All verification services and isolated browser were stopped. Optional macOS opening was not exercised against the user's normal browser.

Private temporary browser/lifecycle evidence: /private/tmp/bancinc-launcher-check.t8OG6I (navigation/, links-accepted/, lifecycle.json, logs). Final JUnit/log: /private/tmp/bancinc-launcher-acceptance-tests.xml and corresponding .log. Temporary evidence is not a durable public release artifact. Screenshots may include pseudonymous financial evidence and remain private.

## Integrity and scope

Original index before/after: 50,000 customers; 2,052 SUPPORTED, 20 CAUTION, 47,928 ABSTAIN. Exact decision/unrounded-priority/reason digest remains 7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3.

No feature contract, gates, policy, canonical dataset, historical model experiment/artifact, Phase 9 snapshot/history, Phase 10B business rule or accepted review history changed. The sole existing accepted-source edit is the explicitly requested app.py sidebar addition. Old immutable source manifests therefore differ for app.py as expected; no manifest, guard or test expectation was rewritten to hide this. The pre-existing protected docs/.DS_Store mismatch was neither touched nor waived; task entry/exit hash bbddc5e958865503c9d4306cc148f8d53b5826a760330562ae228995f9ce193a remains unchanged. Other protected evidence hashes match.

Changed files: app.py; new scripts/start_demo.sh, tests/test_demo_launcher.py and this guide. Existing working-tree/staged changes from prior phases were preserved. No commit, push, publication, model fit or outreach. Phase 9 activation remains companion-only; hypothetical upselling remains a separate synthetic illustration. Organizer/data-display permissions and a human timed rehearsal remain release conditions.
