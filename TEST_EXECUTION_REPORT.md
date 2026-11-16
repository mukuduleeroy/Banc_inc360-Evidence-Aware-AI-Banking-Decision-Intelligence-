# Test execution report — November 16, 2026

Executed in `.venv` with Python 3.9.6 and pytest 8.4.2.

**Full suite: 24 passed in 8.09 seconds.** All nine original Decision Integrity tests remain present and passed. No failures were disabled or skipped. The synthetic feature test verifies the observation cutoff, 180-day window, invalid dates/links and duplicate-event exclusion.

Command: `.venv/bin/python -m pytest -v --junitxml=outputs/tests.xml`

Raw output: `outputs/test_execution_current.txt`; JUnit results: `outputs/tests.xml`.

| Test | Result |
|---|---|
| `test_historical_cutoff_and_invalid_evidence` | PASS |
| `test_supported_savings_review` | PASS |
| `test_insufficient_history_abstains` | PASS |
| `test_borderline_history_caution` | PASS |
| `test_broken_link_abstains` | PASS |
| `test_future_snapshot_abstains` | PASS |
| `test_unapproved_model_blocked` | PASS |
| `test_unverified_kyc_blocks` | PASS |
| `test_already_held_product_suppressed` | PASS |
| `test_automatic_outreach_blocked` | PASS |
| `test_invalid_customer_identifier[]` | PASS |
| `test_invalid_customer_identifier[ ]` | PASS |
| `test_invalid_customer_identifier[None]` | PASS |
| `test_invalid_customer_identifier[nan]` | PASS |
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

Streamlit AppTest also passed all prepared workflows: real Customer 360 indicators/passport/queue, synthetic staff decision logging, KYC/duplicate-product/restricted-customer suppression, supported-only queue and missing-file fallback. Command: `.venv/bin/python scripts/verify_ui.py`. Evidence: `outputs/ui_verification.json` and `outputs/ui_verification.log`.

The verification helper initially failed because the project root was absent from its import path, then because AppTest's index selector passed a display string to a dataclass formatter. The helper now inserts the project root and selects the actual scenario object; the final run exited successfully. Application policy was unchanged.

Streamlit launched on localhost and `/_stcore/health` returned `ok`. The sandbox initially blocked socket binding/requests; approved execution resolved this. No manual browser/visual/accessibility testing was performed. Non-fatal warnings request a future migration from `use_container_width` to `width`.

Earlier full-suite attempts failed collection while pandas was missing. Dependency installation resolved that environment issue; the results above supersede those earlier attempts.
