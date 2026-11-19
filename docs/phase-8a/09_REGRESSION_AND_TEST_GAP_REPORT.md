# Phase 8A — regression evidence and test gaps

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Recorded full baseline verification

**VERIFIED:** `outputs/final_acceptance/verified_final/tests.xml` contains 443 passing cases, zero failures/errors/skips; the terminal log records 58.32s and no pytest warnings. The associated acceptance JSON is PASS and its source/JUnit manifest still matches all 72 current application/test/config/asset files. All 308 Phase 7 cases were retained in that run, with 135 additions. The gate-combination subset has 96 cases. Verification: `evidence/model_and_baseline_audit.json`, `integrity_verification.json`.

This verifies recorded evidence and source freshness; it is not a claim that all 443 cases were re-executed during 8A.

## Side-effect assessment and safe fresh run

Inspected runner, tests/fixtures, data builder, evaluation, review and storage before execution. The ordinary full runner would execute `test_model_reproducibility_and_feature_allowlist`, which calls `historical_evaluation.evaluate()` twice and fits temporary logistic/boosting estimators. Phase 8A prohibits training. It also initializes SQLite via UI tests unless storage is isolated. Accordingly **the full final workflow was not run or modified**, and no fresh final acceptance certificate was created.

A reviewed subset ran with temporary BANCINC_AUDIT_DB and pytest base directory, bytecode disabled/redirected, pytest cache disabled, LOCAL mode, and only new report outputs under docs/phase-8a/evidence. Relevant command shape:

```sh
# task_tmp is a new private /private/tmp/bancinc-phase8a.* directory.
env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="$task_tmp/pycache"  BANCINC_AUDIT_DB="$task_tmp/audit.sqlite3" DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL  .venv/bin/python -B -m pytest -p no:cacheprovider --basetemp "$task_tmp/pytest"  -k 'not test_model_reproducibility_and_feature_allowlist' -v -ra  --junitxml=docs/phase-8a/evidence/safe_tests.xml
```

**Fresh result: 442 passed, 1 deliberately deselected in 35.09s; 0 failed, errors, skips or pytest warnings.** This includes all nine-view AppTest interactions, gate combinations, current source reconciliation, replay, stale evidence and isolated persistence tests. Temporary synthetic fixture files/databases are not production records; no persistent application database was opened by the audit itself. Source/selected existing output hashes were checked before and after: no changes across 190 selected preexisting data/model/database/acceptance files, sources unchanged and alias key unchanged. No shared acceptance evidence or canonical output was overwritten.

Evidence: `evidence/safe_tests.log`, `safe_tests.xml`, `before_integrity.json`, `integrity_verification.json`. No tests or dependencies were edited; deselection is an audit-only no-training safeguard, not a disabled test in the repository.

## Verified acceptance gap to fix first in 8B

`scripts/run_final_regression.py` passes **outputs/phase7/tests.xml** to the verifier. `verify_final_acceptance.verify()` defaults to that same baseline and checks subset retention. It therefore enforces retention of 308 Phase 7 IDs, **not all 443 current IDs** for a future change. It additionally requires at least one test from test_gate_protection but does not independently require all 96 combination IDs. The current 443 suite is present/passing; this is a forward-looking retention gap, not evidence of current test removal.

Before accepting 8B, freeze/verify the current 443-ID inventory or explicitly select the current verified JUnit as the prior baseline, pin its hash and add deletion-negative tests. New acceptance must retain all 443 plus new meaningful cases. Do not update the data/policy/decision reference just to accommodate a failed test. This hardening is specified, not implemented, in 8A.

## Additional test specification

| Feature/risk | Current evidence | Required new tests |
| --- | --- | --- |
| Source banking segment display | Source field retained; no display; raw analytics frame deliberately excludes it | All five allowlisted labels, missing/unknown/malicious free text, safe aliases, source/current-snapshot explanation, no historical-inference claim |
| Banking segment filtering | Behavioral/outcome filters exist | ALL/each label/Unknown; zero-result state; correct aggregate partitions; stable row order, pagination reset and shared selected alias; global versus filtered KPI scopes |
| Segment/product mapping | No approved mapping | Existing Savings-only context shared across labels; other ownership labels never become offers; missing policy remains Unavailable; no invented terms |
| Product explanations | Current rationale/gate table | Explanation matches actual G4/G5/status/reason/policy/hash for held/missing/restricted/borderline/supported cases; no new review action |
| Historical AI comparison | JSON artifacts present; no UI panel | Exact numeric values/AP labeling/cohort/cutoff; missing/malformed/nonfinite/stale/wrong-version/hash mismatch; no hardcoded fallback metrics; no probability/approval claim |
| Live experimental inference | No saved models/API | Deferred; if later authorized, require fitted preprocessor/model identity, feature order/types, version/hash/dependency checks, valid cohort, deterministic bounded output and safe missing handling |
| Artifact integrity | Existing JSON/code/score hashes | New panel validates artifact/data/source/code association; never loads arbitrary binary/user uploads or refits; corrupted artifact produces Unavailable |
| G3 isolation | Declared model-use blocks even caller-approved; extra columns ignored | No panel score can enter Case/gates/priority/queue/review payloads; no model-approved toggle; no import/fitting in runtime display helper |
| G4/G5 bypass | 18 restrictions/suitability cases, 96 combinations | Repeat new segment/product display integration across restrictions, held/unknown/no rationale, unsupported categories; final state remains engine-equal |
| Decision invariance | Full population digest, frozen CSV/manifest/policy | Recheck 50,000 decisions, exact priorities/reasons, 2,052/20/47,928; no segmentation/filter/panel mutation before/after interactions |
| Stale evidence | Review service/hash/revision/TOCTOU tests | Stale/missing segment/model metadata must not authorize writes or erase original lineage; old review/policy tests retained |
| Currency display | Builder uses provided USD; fresh aggregate rate consistency | Mixed currencies, positive/missing/zero rates, rounding tolerance, rate dates and no mixed raw-sum fallback; calculations unchanged |
| All nine views/design | Existing routes, 36 recorded viewports and native tests | New interactions in Customer 360/Inactivity/Value/Product; all nine routes and selection preserved; no design reset/overflow; explicit demo/missing artifact behavior |
| Existing test retention | Runner retains only older 308 by default | Fail when any current 443 ID is removed, including new gate matrix/report guards; preserve source-freshness and JUnit tamper checks |

No new test code or CI/dependency change was introduced in this audit. Full integrated acceptance after 8B may fit the existing synthetic reproducibility fixture only when the implementation phase authorizes that validation; no real model retraining/deployment is implied.
