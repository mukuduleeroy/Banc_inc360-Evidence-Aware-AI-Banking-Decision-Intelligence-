# Phase 2 — validation report

Execution date: **November 16, 2026 (Africa/Harare)**. Python 3.9.6, pytest 8.4.2, Streamlit 1.50.0, pandas 2.3.3. No dependencies added.

## Automated results

**124 collected; 124 passed; 0 failed; 0 errors; 0 skipped; 0 pytest warnings.** Terminal duration **10.76 seconds** (JUnit suite: 10.757). All original 24 tests remain unchanged and pass; 100 regression cases were added.

| File | Passing cases | Coverage |
|---|---:|---|
| `tests/test_engine.py` | 23 | Original gate policy and existing boundary cases, unchanged |
| `tests/test_data.py` | 1 | Original synthetic chronology/invalid-evidence fixture, unchanged |
| `tests/test_evidence.py` | 52 | Unknown/missing status/KYC, NaN/infinite/negative/nonnumeric/huge counts, malformed/ambiguous holdings, safe originals, recognized normalization, three valid outcomes and human/model/lineage controls |
| `tests/test_queue.py` | 27 | Complete deep-candidate evaluation, pagination, stable ordering, duplicates/conflicts, invalid IDs/fields, domain consistency, alias collision detection, private stable key and dataset/manifest/policy cache invalidation |
| `tests/test_cohort.py` | 16 | Future-only cohort invariance, current snapshot independence, separate January/July observations, exact windows, future-independent deduplication, ownership conflicts, malformed events, unknown snapshots, invalid cutoff and no overwrite |
| `tests/test_real_data.py` | 1 | Actual supplied competition file, verified manifest, full count reconciliation, nonempty genuine supported queue, aliases, passports and unchanged file hash |
| `tests/test_ui_validation.py` | 4 | Explicit synthetic corrupted CSV imports: holdings, account status, KYC and NaN history all produce zero sales cases and ABSTAIN passports |

Controlled unit fixtures are explicitly synthetic, never substitutes for the supplied dataset. The real-data test does not hardcode 2,052: it reconciles the validated index and asserts genuine support from the available local data. If authorized data is absent in a different checkout, that single test explicitly skips; it **did not skip here**. A present but unattested dataset fails rather than inventing provenance.

## Commands executed

From the project root:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python scripts/reconcile_phase2.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --out outputs/phase2/verification > outputs/phase2/reconciliation.log 2>&1
.venv/bin/python scripts/reconcile_phase2.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --out outputs/phase2/final_verification > outputs/phase2/final_reconciliation.log 2>&1
.venv/bin/python scripts/reconcile_phase2.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --out outputs/phase2/input_integrity_verification > outputs/phase2/input_integrity_reconciliation.log 2>&1
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase2/tests.xml > outputs/phase2/test_execution.log 2>&1
.venv/bin/python scripts/verify_ui.py > outputs/phase2/ui_verification.log 2>&1
.venv/bin/python scripts/compare_phase2.py > outputs/phase2/queue_comparison.log 2>&1
.venv/bin/python -m pip check --disable-pip-version-check
git diff --check
```

The initial untouched baseline passed 24 tests in 0.55 seconds. Intermediate suites passed 95, 112, 116, 118, 119 and 123 cases as safeguards were added. One early synthetic date probe emitted pandas' format-inference warning; explicit mixed-format/day-first parsing resolved it. The final 124-case run has no warnings. No failed case was disabled or deleted.

Final raw evidence: `outputs/phase2/test_execution.log`, `outputs/phase2/tests.xml`, `outputs/phase2/ui_verification.log`, `outputs/ui_verification.json`, `outputs/phase2/queue_comparison.json` and `outputs/phase2/input_integrity_verification/reconciliation.json`.

## Streamlit content/runtime checks

All six groups passed:

1. Real totals equal the complete index; default supported queue is nonempty and matches the expected page; passport has six gates and matches the selected alias.
2. Page 2 matches full-index pagination, with no duplicate cases from page 1.
3. Empty alias filter state is explained; CAUTION and ABSTAIN investigation lanes show only their respective outcomes.
4. Blank review reason is rejected; a deliberate real-case review note records the selected alias and SUPPORTED passport consistently.
5. Separately labeled synthetic Pending-KYC, duplicate-product and restricted-customer cases abstain; the synthetic sales table contains only SUPPORTED cases.
6. Missing real feature file falls back to clearly labeled synthetic demonstrations with a warning.

The helper emits two expected bare-mode ScriptRunContext log messages; these are not pytest warnings or application failures. Previous `use_container_width` deprecation messages were removed by using the installed Streamlit `width` API in targeted tables. Manual rendered-browser, responsive-layout and accessibility verification were not performed.

A fresh process was started separately from the existing session:

```sh
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false > outputs/phase2/startup.log 2>&1
curl --fail --silent --show-error -o outputs/phase2/health.txt -w 'HTTP %{http_code}\n' http://127.0.0.1:8502/_stcore/health
```

Startup succeeded and health returned **HTTP 200 / `ok`**. Local socket operations used approved sandbox escalation. The verification process was stopped after checking; the existing session was not reset. `pip check` returned **No broken requirements found**; its cache-directory advisory does not indicate a missing requirement.

## Rebuild, lineage and canonical preservation

The full ZIP rebuild processed **1,048,575 source rows**, producing **50,000 customers**. Invalid identifiers/dates, ownership links, duplicate transaction IDs, invalid amounts, unknown transaction types, historical ownership-conflict customers and future-only excluded customers all counted **zero** on this source.

The corrected candidate and canonical file have equal customer keys and zero differences across all 16 non-key columns. The canonical CSV's SHA-256 agrees with the Phase 1 preservation record, before and after Phase 2. A new source-linked companion manifest was created only after equality verification. The CSV and previously reported model metrics were never replaced.

Local manifest verification is evidence of a reproducible local build, not signed external attestation or a guarantee of current KYC freshness. Temporal tests validate feature construction at distinct observation cutoffs, not a trained model or future inactivity label experiment.
