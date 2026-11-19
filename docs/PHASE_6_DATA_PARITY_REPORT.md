# Phase 6 data parity and validation report

Executed 2026-11-18 (Africa/Harare). **Local parity verified; live public real-data parity not verified or deployed.** Publication is blocked pending written BancABC approval. Test configuration references are explicitly local-only fixtures, not actual release authorizations.

## Evidence matrix

| Check | Existing public deployment | Local emulation of DEPLOYED/CLOUD mode |
| --- | --- | --- |
| Configured feature artifact | Missing/unresolvable per live warning | Authorized local-only copy loaded |
| Real customer rows | Not available; synthetic-only UI | 50,000 |
| SUPPORTED | Not a real-data count | 2,052 |
| CAUTION | Not a real-data count | 20 |
| ABSTAIN | Not a real-data count | 47,928 |
| Release fingerprint/version checks | Old loader lacks independent release pins | Checked SHA and local-only manifest version |
| Decision engine | Live demo identifies deterministic rules | Unchanged local engine, entire queue equal |
| All nine views | Synthetic page only | All nine AppTest and Chrome views passed |
| Alias selection/Passport | Demo identities only | Real supported alias, six gates, source provenance |
| Replay | Synthetic examples | Real SUPPORTED baseline → SIMULATED Pending KYC ABSTAIN → reset SUPPORTED |
| Manager queue | Not available for real population | Nonempty complete supported queue |
| Review storage | Private settings/files inaccessible | Explicitly ephemeral cloud SQLite initialized without preexisting DB |
| External data publication | None performed in this phase | None; emulation stays in ignored local outputs |

These are independently calculated results, not output constants. Local artifact SHA-256: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. Current policy fingerprint: `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`. The emulation copies only authorized local files into ignored `outputs/phase6/parity/`, adds `dataset_version=phase6-local-parity-only` to that copy's manifest and leaves canonical inputs untouched. The complete alias/rating/priority/action queue matches local evaluation, not only aggregate totals. Same alias key is used for this comparison; separate authorized environments may use different keys and consequently different aliases.

## Test results

Baseline before edits:

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase6/baseline_tests.xml
```

**261 passed in 57.08s.**

Complete Phase 6 regression:

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase6/tests.xml
```

**291 collected; 291 passed in 82.42s; 0 failed, errors, skips or pytest warnings.** All 261 original test identifiers remain. One legacy missing-file fallback assertion was deliberately updated to require the requested DATASET_UNAVAILABLE error/no synthetic content; the identifier and malformed-schema check remain. The standalone UI helper was updated consistently. No test was removed or disabled.

Thirty new cases cover missing deployed/local inputs, explicit demo, no silent fallback, exact deployed schema, hash/version/missing-manifest errors, approval/config prerequisites, stable alias secret conflicts, portable paths, env/secrets precedence, cloud-mode enforcement, fresh ephemeral audit initialization, content/policy cache invalidation, safe alias display, no-outreach/human control, all nine views under actual CLOUD configuration, real-artifact local parity, excluded secret/data tracking and manifest replacement during load. Unit fixtures are explicitly synthetic. Cloud-mode approval references in tests are local validation markers, not permission to host competition data.

The final targeted UI/report/deployment check after adding Phase 6 evidence to the Audit view passed **51 tests in 34.48s** (`outputs/phase6/final_ui_checks.log`). Standalone `scripts/verify_ui.py` passed all six workflow groups, including missing-file error rather than fallback. Bare AppTest helpers emit Streamlit ScriptRunContext advisories outside pytest; these are distinct from the zero warnings in the complete pytest run.

## Reproduction and actual browser checks

```sh
.venv/bin/python scripts/verify_deployment_parity.py --out outputs/phase6/parity-new
.venv/bin/python scripts/verify_ui.py
```

Choose a new parity output directory. The helper never transfers data externally, never overwrites canonical files and writes no review events. Its structured output is `outputs/phase6/parity/parity.json`.

A temporary localhost-only Streamlit server ran with DEPLOYED/CLOUD settings against that local artifact copy and a separate browser_cloud.sqlite3. Existing Chrome and Node checked all nine native views at 1440px, with zero application exceptions/whole-document horizontal overflow, then exercised the real-supported Pending-KYC replay/reset. The narrow 768px overview was also captured. The public app was not changed. Browser command against this temporary server:

```sh
env BANCINC_CDP_URL=http://127.0.0.1:9224 BANCINC_PREVIEW_URL=http://127.0.0.1:8506 BANCINC_BROWSER_OUT=outputs/phase6/browser node scripts/verify_browser.mjs
```

Evidence: `outputs/phase6/browser/browser_verification.json`, `browser_execution.log`, viewport PNGs under `browser/screenshots/`. Synthetic modified fields remain visibly labeled; baseline data is the competition feature extract. The original public screenshot and iframe text are separately retained as deployed-before evidence. Functional checks are not formal accessibility/security certification. No live banking action or communication was performed.

## Preservation and confidentiality

SHA-256 comparisons confirm no changes to engine.py, evidence.py, data_access.py, analytics.py, build_data.py, replay.py, audit_store.py, review_service.py, canonical CSV or canonical manifest. Existing Phase 4 presentation history still has OPEN/APPROVE (two events); stale-rehearsal history retains four events. Schema and review-write logic were untouched; emulated cloud databases were isolated. See `outputs/phase6/preservation.json`.

No source tables, key, real secrets, customer CSV, database or screenshot was added to tracked files. Actual Streamlit secrets are now explicitly ignored; the documented nonsecret template is intentionally exempt. Rendered customer tables use checked C- aliases rather than raw customer/account identifiers; deployed artifacts reject additional raw source columns. Data approval and audience access remain organizational requirements that masking and loader checks cannot satisfy automatically.

## Release status

Code/configuration changes are prepared locally and reviewable. They are not pushed or deployed. For the current public app, use explicit DEMO after code review until written approval exists. To obtain actual live 50,000-row parity, first verify hosting/audience permission, provision the exact private release artifact and secrets, confirm branch/entry point/commit in owner settings, deploy the reviewed code, then run live acceptance and record its evidence. Neither cloud persistence nor live data parity may be claimed before that verification.
