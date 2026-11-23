# Phase 9 test results

## Complete acceptance

**574 collected, 574 passed; 0 failures, 0 errors, 0 skips.** Pytest duration: **94.37 seconds**. No pytest warnings summary was emitted. All **504** Phase 8B cases remain, plus **70** new tests. All **96** original gate-combination cases passed.

Exact command:

```bash
BANCINC_AUDIT_DB=/private/tmp/bancinc-phase9-full-regression.sqlite3 \
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python phase9_acceptance.py \
  --out-dir outputs/final_acceptance/phase-9-final
```

This additive runner invokes the unchanged `scripts/run_final_regression.py`, which runs the entire suite with `-v -ra --junitxml=...`, verifies freshness and the original decision baseline, then creates a fresh acceptance receipt. Phase 9 additionally verifies the prior hash-pinned 504-case JUnit inventory, all 79 accepted source bytes, 24 protected artifact hashes and 55 pre-existing database/sidecar hashes. No previous receipt was overwritten.

Evidence:

- `outputs/final_acceptance/phase-9-final/test_execution.log`
- `outputs/final_acceptance/phase-9-final/tests.xml`
- `outputs/final_acceptance/phase-9-final/run_manifest.json`
- `outputs/final_acceptance/phase-9-final/acceptance.json`
- `outputs/final_acceptance/phase-9-final/phase9_acceptance.json`
- `outputs/phase9/full_acceptance.log`

Current run JUnit SHA-256: `9cf3d25aa2705b651864b1cb34511e5d8fd73e3260cb0e9651e512ed8212cff8`.
Prior accepted JUnit SHA-256: `921045f96df828a3cd223350ef4f657bfe0623570b5b43b4e0ffd4429c663c52`.
All **87** current Python/test/config/asset files in the unchanged acceptance snapshot mechanism stayed unchanged during/after the run. All **79** accepted source files match their original bytes.

## New targeted coverage

| Test module | Cases | Coverage |
|---|---:|---|
| `tests/test_phase9_ingestion.py` | 59 | Valid source/all outcomes; schema/type/date/numeric/currency/identifier/ownership failures; duplicate semantics; unknown eligibility; chronology; file/row/field limits; traversal/malformed CSV; staging lineage; exact gate/priority/reason reuse; unique snapshots; tampering; activation/rollback; atomic failure/recovery; managed storage isolation |
| `tests/test_phase9_ui.py` | 6 | Full native companion sequence; invalid upload; cleanup/date change; nonlocal refusal; actual installed uploader API; mandatory transport cap |
| `tests/test_phase9_protection.py` | 5 | Original source/artifact/history hashes; original inventory; all-customer decision invariance across activation/rollback; reconciliation failure; no inference/network/existing-audit dependency in runtime modules |

Commands and development receipts:

- `.venv/bin/python -m pytest tests/test_phase9_ingestion.py -q -ra`: **59 passed in 0.71s**, `outputs/phase9/targeted.log`.
- Initial four mocked-uploader UI tests: **4 passed in 11.82s**, `outputs/phase9/ui_tests.log`.
- Combined first focused run: **68 passed in 11.53s**, `outputs/phase9/focused_tests.log`.
- Corrected real-uploader/configuration UI run: **6 passed in 9.29s**, `outputs/phase9/ui_recheck.log`.
- Final full acceptance includes all 70 new cases and all original cases.

The pre-existing isolated synthetic estimator-fitting test was retained and ran only in its original fixture. No real-data retraining, historical experiment rewrite or operational fitted inference was performed.

## Live synthetic demonstration

```bash
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python scripts/accept_phase9.py \
  --out outputs/phase9/browser_verified --port 8511 --cdp-port 9230
```

**PASS**: actual browser file upload → successful validation → unchanged feature processing → 4 evaluated customers, 1 SUPPORTED / 1 CAUTION / 2 ABSTAIN → six visible gates → explicit activation → explicit return to 50,000-customer baseline → invalid-date upload rejected with processing/activation disabled. Registry events reconcile exactly to CREATE, ACTIVATE, ROLLBACK_BASELINE. No application exceptions or outreach controls. Three responsive viewport checks (1440/768/390) found no document overflow or application exceptions. This samples layout, not formal accessibility compliance; screenshots are viewport-only.

Evidence: `outputs/phase9/browser_verified/acceptance.json`, `browser_result.json`, screenshots and logs. All uploads used generated independent synthetic examples; storage and alias key were isolated. Browser/server processes stopped after the check.

## Original application browser regression

```bash
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python scripts/accept_phase5.py \
  --out outputs/phase9/original_app_browser --port 8512 --cdp-port 9231
```

**PASS**: all nine original native views, real KYC replay/reset and persistent local review across an actual Streamlit restart. The new isolated demonstration database retained one case, two events, two snapshots and 16 evidence references. Accepted canonical data and old Phase 4 histories remained unchanged. Existing Phase 7 styling remains byte-identical; previous desktop/tablet/mobile acceptance receipts were preserved. Evidence: `outputs/phase9/original_app_browser/acceptance.json`, browser JSON receipts/logs/screenshots.

## Failure discovered and resolved

The first actual browser attempt failed because this installed Streamlit version does not accept `file_uploader(max_upload_size=...)`. Mocked upload tests had hidden that API mismatch. Removed that unsupported argument without dependency changes; require the supported server transport setting `--server.maxUploadSize 5`, enforce it before rendering upload controls, and add an unmocked uploader/API test plus a missing-cap rejection test. The repeated real-browser workflow and final full suite passed. The original failed run remains in `outputs/phase9/browser/` and `browser_run.log`; it is not acceptance evidence. No unresolved regression remains.
