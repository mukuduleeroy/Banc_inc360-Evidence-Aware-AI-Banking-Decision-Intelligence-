# Phase 4 validation report

Executed locally on 2026-11-16, Python 3.9.6, pytest 8.4.2, Streamlit 1.50.0. These results describe the local workspace, not certification.

## Automated tests

Baseline command: `.venv/bin/python -m pytest -v -ra` → **182 passed in 34.12s**. Captured in `outputs/phase4/baseline_tests.log`.

Final command:

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase4/tests.xml
```

Exact terminal summary: **229 passed in 53.87s**. Collected 229, passed 229, failed 0, errors 0, skipped 0, pytest warnings 0. Full output: `outputs/phase4/test_execution.log`; machine evidence: `outputs/phase4/tests.xml`. All 182 original Phase 3 case identifiers were retained (verified by JUnit comparison). New cases: audit store 9, review service 32, durable UI 6 = 47.

Coverage includes initialization/version rejection, release schema hash, FK/rollback, file permissions/backup, real-supported approval, required reason and acknowledgement, explicit attribution, CAUTION/ABSTAIN rejection, simulated-context rejection, source/policy/manifest/decision staleness, physical policy reload guard, real disk reread, revision conflicts, concurrent submissions, duplicate tokens, append-only history, snapshot corruption, parameterized SQL, privacy-safe snapshots, feature-level references and UI error reporting. Controlled test fixtures are not presented as competition evidence.

## Actual-source persistence and stale evidence rehearsal

Commands executed (stdout/stderr captured under `outputs/phase4/`):

```sh
.venv/bin/python build_data.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --out outputs/phase4/alternate_jan --cutoff 2026-01-01
.venv/bin/python scripts/verify_phase4_persistence.py --alternate outputs/phase4/alternate_jan/customer_features.csv --db outputs/phase4/process_rehearsal.sqlite3 --backup outputs/phase4/process_rehearsal_backup.sqlite3
```

Use fresh unused rehearsal database and backup paths when repeating. This was an alternate real-source build, not synthetic data and not a canonical replacement. July canonical counts: 2,052/20/47,928. January alternate counts: 1,976/289/47,735. An actual supported case was opened and approved locally; a fresh Python process read APPROVED_LOCAL with OPEN/APPROVE. Switching to the valid alternate dataset rejected an old-context review with STALE_EVIDENCE and no extra event. Explicit refresh then defer produced OPEN/APPROVE/REFRESH/DEFER; a fresh process read DEFERRED, four events, four snapshots and 32 references. Original snapshot unchanged, backup verified, canonical CSV unchanged. Exact machine evidence: `outputs/phase4/persistence_demo.json`.

## Native UI and browser evidence

```sh
.venv/bin/python scripts/verify_phase4_ui.py
.venv/bin/python scripts/verify_ui.py
env BANCINC_PREVIEW_URL=http://127.0.0.1:8503 BANCINC_BROWSER_OUT=outputs/phase4/views node scripts/verify_browser.mjs
node scripts/verify_phase4_browser.mjs create
# Stop and restart the Streamlit process using the same presentation.sqlite3 path.
node scripts/verify_phase4_browser.mjs reopen
```

The Phase 4 AppTest helper uses an isolated temporary database: all nine native pages loaded; explicit actor, persisted supported review and a fresh-session audit read passed (`ui_verification.json`). Streamlit bare-mode helpers emit missing ScriptRunContext warnings outside pytest; these are recorded separately and are not pytest warning counts.

Actual Chrome/CDP checks rendered all nine pages and verified SUPPORTED → simulated Pending-KYC ABSTAIN → reset SUPPORTED. The Phase 4 browser helper created one real-source local case with Demo reviewer 1, recorded APPROVE with reason/acknowledgement, then read APPROVED_LOCAL after an actual server process restart. The audit still showed exactly two events, DEMO_UNVERIFIED, FEATURE_LEVEL and bank_authorization false, with zero app exceptions. Evidence: `browser_create.json`, `browser_reopen.json`, `views/browser_verification.json` and corresponding logs under `outputs/phase4/`. Driver waits for the reviewer-dependent enabled button; no application guard was weakened.

Screenshots: `outputs/phase4/screenshots/review_approved.png`, `audit_timeline.png`, `review_after_restart.png`, `audit_after_restart.png`; all nine pages under `outputs/phase4/views/screenshots/`. The restarted audit screenshot was visually inspected. This is functional browser evidence, not formal accessibility or security certification.

## Preservation and privacy

Eight protected artifact hashes match the pre-edit baseline (`baseline.json`, `preservation.json`). Canonical CSV SHA-256: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. Policy fingerprint: `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`. Feature-level lineage explicitly reports no verified source-event mapping. Local databases, WAL/SHM, screenshots, source data and alias keys remain ignored; review reasons and aliases remain private operational data.

## Remaining limits

No production authentication, owner-resistant audit integrity, database encryption, retention enforcement, transaction-level replay or independent source attestation. Current KYC/status/holdings effective dates are unavailable. No trained future prediction or model-performance claim. Approval remains a local prototype outcome with no banking API or outreach.
