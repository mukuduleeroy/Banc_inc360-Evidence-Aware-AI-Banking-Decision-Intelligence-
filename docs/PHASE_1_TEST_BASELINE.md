# Phase 1 — fresh test and runtime baseline

Execution date: **November 16, 2026 (Africa/Harare)**. Original tests and application files were not modified. Evidence is under ignored `outputs/phase1_audit/`.

## Results

| Check | Fresh outcome |
|---|---|
| pytest collection | **24 tests**: 23 engine cases, one feature-builder case |
| Passed / failed / errors / skipped | **24 / 0 / 0 / 0** |
| pytest warnings reported | **0** |
| pytest terminal duration | **0.62 seconds**; JUnit suite duration 0.625 seconds |
| Dependency consistency | `No broken requirements found` |
| Installed lock versions | All **42** pinned versions match installed metadata |
| Existing AppTest helper | Exit 0; all five reported workflow groups true |
| Existing server, port 8501 | Health HTTP 200, body `ok` |
| Fresh server, port 8502 | Started successfully; health HTTP 200, body `ok`; audit instance subsequently stopped |
| Source validation and separate rebuild | Completed; matching keys and all 16 non-key feature columns |
| Independent five-feature recomputation | Zero mismatches across all 50,000 customers |
| Source/default feature preservation | Before/after SHA-256 checks unchanged |

AppTest logs contain **24 width deprecation messages** and **two missing-ScriptRunContext messages** associated with the test harness. These are not pytest warnings and did not fail the helper. Startup suggests optional Watchdog installation; no new package is required or installed for this audit.

## Exact commands

Executed from `/Users/user/Downloads/BancInc360_Final`:

```sh
.venv/bin/python --version
.venv/bin/python -m pip check --disable-pip-version-check
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase1_audit/pytest.xml > outputs/phase1_audit/pytest.log 2>&1
.venv/bin/python scripts/verify_ui.py > outputs/phase1_audit/ui_workflows.log 2>&1
cp outputs/ui_verification.json outputs/phase1_audit/ui_verification.json
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false > outputs/phase1_audit/startup.log 2>&1
curl --fail --silent --show-error -o outputs/phase1_audit/health_8501.txt -w '8501 HTTP %{http_code}\n' http://127.0.0.1:8501/_stcore/health
curl --fail --silent --show-error -o outputs/phase1_audit/health_8502.txt -w '8502 HTTP %{http_code}\n' http://127.0.0.1:8502/_stcore/health
.venv/bin/python outputs/phase1_audit/inspect_data.py > outputs/phase1_audit/data_checks.log 2>&1
.venv/bin/python outputs/phase1_audit/edge_probes.py > outputs/phase1_audit/edge_probes.log 2>&1
```

The fresh server/localhost requests required approved sandbox escalation. The audit-only inspection helper independently reads the source, aggregates features and invokes this existing builder call:

```python
run(Path('/Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip'), ROOT / 'outputs/phase1_audit/rebuild', '2026-07-01')
```

It also compares rebuilt rows and hashes existing source/feature files. An initial slow version of the independent aggregation helper was interrupted, optimized to use vectorized group aggregates, and rerun successfully; this did not modify application code or disable tests. Other read-only checks used `git status --short`, `git ls-files`, `git log -3 --format='%h %s'`, `git rev-list --all --objects`, `git check-ignore`, and local Python package/document checks. Scripts and aggregate outputs remain available under the ignored audit directory.

## Every collected test

| Test | Result / purpose |
|---|---|
| `test_historical_cutoff_and_invalid_evidence` | PASS — synthetic duplicate, invalid ownership/date, cutoff-day event and older-than-180-day event; checks event/deposit count and recency |
| `test_supported_savings_review` | PASS — original supported rule path |
| `test_insufficient_history_abstains` | PASS — original one-event path |
| `test_borderline_history_caution` | PASS — original three-event path |
| `test_broken_link_abstains` | PASS — original bad-link flag |
| `test_future_snapshot_abstains` | PASS — original future-information flag |
| `test_unapproved_model_blocked` | PASS — original unapproved-model control |
| `test_unverified_kyc_blocks` | PASS — original KYC gate |
| `test_already_held_product_suppressed` | PASS — original duplicate-product control |
| `test_automatic_outreach_blocked` | PASS — original automatic-action block |
| `test_invalid_customer_identifier[]` | PASS — empty ID |
| `test_invalid_customer_identifier[ ]` | PASS — whitespace ID |
| `test_invalid_customer_identifier[None]` | PASS — null ID |
| `test_invalid_customer_identifier[nan]` | PASS — literal invalid ID |
| `test_restricted_account_blocks[Frozen]` | PASS |
| `test_restricted_account_blocks[Dormant]` | PASS |
| `test_restricted_customer_blocks` | PASS |
| `test_history_boundaries[0-ABSTAIN]` | PASS |
| `test_history_boundaries[2-CAUTION]` | PASS |
| `test_history_boundaries[4-SUPPORTED]` | PASS |
| `test_missing_behaviour_blocks` | PASS |
| `test_human_controls_required[staff_verification_required]` | PASS |
| `test_human_controls_required[human_review_required]` | PASS |
| `test_unsupported_product_blocks` | PASS |

Nine original engine tests exist and pass; the total is now 24, not nine. Coverage is described behaviorally; no coverage dependency was installed and no line/branch coverage percentage is claimed.

## What AppTest actually verifies

| Helper group | Actual assertions | Important limits |
|---|---|---|
| Real indicators/passport/queue | No exception, first metric has the expected label, rating is one of three strings, at least three dataframes exist | Does not assert numeric values, six gate contents, populated real queue, correct customer attribution or rationale |
| Human decision/session log | Synthetic supported case; enter reason; press record; session list length becomes one | No empty-reason assertion, actor identity, saved passport contents, restart persistence or write-failure handling |
| Suppression | Synthetic Pending KYC, already-held savings and restricted customer each produce ABSTAIN | Does not assert sales action text or inspect real restricted records; Frozen/Dormant checks are engine-only |
| Supported-only queue | Inspects synthetic queue after scenario checks; displayed ratings are a subset of SUPPORTED | Does not check eligibility of the real population or prove a nonempty queue; a subset assertion can pass for an empty table |
| Missing-file fallback | Override path to missing file; script does not throw and one warning appears | Does not validate corrupt schemas, numeric domains, serialized holdings or imported cutoff metadata |

The helper exercises useful real/synthetic paths, but is a smoke check rather than complete acceptance. No browser automation/rendered screenshot, responsive layout, keyboard navigation or accessibility audit was performed. Health HTTP 200 proves server liveness; it is not equivalent to executing every script branch. AppTest supplies the separate script-execution evidence.

## Audit probes outside the passing baseline

Controlled synthetic probes are observations, **not added pytest tests** and not production input substitutions. They establish missing safeguards despite the passing baseline:

| Probe | Observed behavior |
|---|---|
| Empty account status with otherwise valid case | SUPPORTED |
| NaN qualifying-event count | SUPPORTED |
| Percentile 2.0 / negative recency | SUPPORTED, with distorted priority |
| Caller sets `uses_model_for_action=True`, `model_approved=True` | SUPPORTED without registry evidence; trusted-call configuration limitation |
| Add a post-cutoff-only customer | Prior customer's historical percentile changes 0.5 → 0.6667 |
| Unknown type plus invalid amount | Counts one event with zero volume |
| Malformed holdings in a clearly synthetic corrupted feature fixture | UI has no exception and yields SUPPORTED |

Real-data population evaluation also found 2,052 supported cases, while every top-1,500 candidate in the current scan is ABSTAIN. The default queue is empty. This was not caught by existing assertions. See `edge_probes.json`, `queue_checks.json` and the other audit documents.

## Next regression priorities

Add tests for fail-closed product parsing, numeric/enum domains, source/cutoff validity, a qualifying case beyond candidate 1,500, preservation of internal identity despite display masking, snapshot non-leakage including cohort membership, service-fee/type definitions, exact lower-window boundaries, duplicate ownership/invalid-first-duplicate behavior, persistent review logging and replay consistency. Preserve all 24 existing passing cases and established history thresholds.
