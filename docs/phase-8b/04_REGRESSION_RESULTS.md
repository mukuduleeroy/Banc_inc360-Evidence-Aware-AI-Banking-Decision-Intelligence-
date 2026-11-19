# Phase 8B regression results

## Final complete run

**PASS: 504 collected, 504 passed, 0 failures, 0 errors, 0 skipped; 47.40 seconds.** Pytest reported no warnings summary. Streamlit AppTest's captured bare-thread ScriptRunContext log messages are not pytest warnings or application exceptions.

All **443** prior test IDs are retained, plus **61** new cases. The gate suite includes **96** gate-combination cases; existing individual gates, anti-bypass, stale evidence, replay/reset, audit persistence and deployment-mode tests all passed. The isolated synthetic estimator reproducibility test ran in its original fixture; no real-data model training occurred.

Exact full command from the repository root:

```bash
BANCINC_AUDIT_DB=/private/tmp/bancinc-phase8b-full-regression.sqlite3 \
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python scripts/run_final_regression.py \
  --out-dir outputs/final_acceptance/phase-8b-final
```

The runner executes `.venv/bin/python -m pytest -v -ra --junitxml=<absolute fresh output directory>/tests.xml`, snapshots sources before/after, then calls the corrected final verifier. Its exact executable/JUnit paths and timestamps are in `run_manifest.json`. Repository location for this session: `/Users/user/Documents/BancInc360_Final`.

Evidence:

- `outputs/final_acceptance/phase-8b-final/test_execution.log`
- `outputs/final_acceptance/phase-8b-final/tests.xml`
- `outputs/final_acceptance/phase-8b-final/run_manifest.json`
- `outputs/final_acceptance/phase-8b-final/acceptance.json`
- `outputs/phase8b/preservation_verification.json`

Current JUnit SHA-256: `921045f96df828a3cd223350ef4f657bfe0623570b5b43b4e0ffd4429c663c52`.
Prior 443-case JUnit SHA-256: `8fd29c0dbc43354b94c5210fc479a8ad62fc5d7c6c408c2181949115fb343920`.
Source-bound run: 79 source/test/config/asset files unchanged during and after tests. Required inventory is checked against the hash-pinned prior JUnit; a current-run reference, missing prior gate case, failure, error or skip is rejected. Frozen customer reference was not regenerated.

## New tests

| Module | New cases | Scope |
|---|---:|---|
| `tests/test_acceptance_gate.py` | 6 (17 total) | 443-case retention, missing gate/combination cases, self-reference, prior receipt and inventory tampering |
| `tests/test_segment_context.py` | 15 | Labels, malicious input, alias joins, duplicates, missing rows, exact frame/decision invariance |
| `tests/test_product_context.py` | 8 | Actual passport G4/G5, ownership/rationale/status restrictions, segment/model-score isolation |
| `tests/test_experimental_evidence.py` | 24 | Trusted receipt, metrics/config/cohort validity, source/code hashes, stale/missing/malformed states, no runtime inference |
| `tests/test_intelligence_views.py` | 8 | Default All, combined filters, selection, pagination reset, empty states, KPI invariance, verified/unavailable panels |

Targeted commands (all via `.venv/bin/python -m pytest`):

- `tests/test_acceptance_gate.py -v -ra`: 17 passed, 0.04s; B0 completed before integration.
- `tests/test_segment_context.py -v -ra`: 15 passed, 0.05s.
- `tests/test_experimental_evidence.py tests/test_product_context.py tests/test_segment_context.py -v -ra`: 47 passed, 0.38s.
- `tests/test_intelligence_views.py tests/test_navigation.py tests/test_durable_ui.py -q -ra`: initial development run 31 passed / 1 failed, 28.09s (explained below).
- `tests/test_intelligence_views.py -q -ra`: corrected/extended interaction suite 8 passed, 14.35s.

## Development failure and resolution

One new test initially assumed Trust customers included already-held Savings. Actual source data yields an empty Trust/already-held intersection. The UI was correct. The assertion was corrected to compare the exact filtered source frame (including the empty case); no dataset, policy, gate or working application logic was changed to satisfy it. The corrected test and the entire full suite passed. No unresolved failure remains. Development logs are retained under `outputs/phase8b/`.

## Actual server/browser acceptance

```bash
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python scripts/accept_phase5.py \
  --out outputs/phase8b/browser_acceptance --port 8508 --cdp-port 9226
```

PASS: nine actual native views, no browser exceptions/overflow; Evidence Replay SUPPORTED → Pending KYC ABSTAIN → reset SUPPORTED; no replay action controls. A fresh managed database retained its case, two immutable events, two snapshots and 16 evidence references after a real Streamlit process restart. Prior Phase 4 histories and canonical data remained unchanged. Evidence: `outputs/phase8b/browser_acceptance/acceptance.json`, `browser_verification.json`, `browser_create.json`, `browser_reopen.json` and screenshots/logs.

The existing Phase 7 responsive browser checker also passed all nine views at widths **1440, 768 and 390** (27 view/viewport checks), plus keyboard focus sampling. A temporary copy changed only its output folder to `outputs/phase8b/responsive`; the original checker and Phase 7 receipts were preserved. Invocation: `.venv/bin/python /private/tmp/bancinc_phase8b_visual.py` with fresh local server 8509, CDP 9227 and isolated database. This runner used `BANCINC_VIEWPORTS=1440,768,390`, a temporary Chrome profile, and stopped its server/browser afterward. Report: `outputs/phase8b/responsive/visual_validation.json`. No page overflow, clipped metric/button labels, stale rendering or application exceptions were found; independent-student identity and six passport gate cards remained. This is sampled usability/layout verification, not formal accessibility certification.
