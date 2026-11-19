# Final acceptance — mandatory regression and gate protection

Executed 2026-11-18 (Africa/Harare). **PASS for the current local presentation prototype.** Proposals 9 and 10 are satisfied within this scope: no unresolved regression failures, no unexpected operational decision changes and no experimental/unverified model outputs driving banking actions. This is technical acceptance, not bank authorization, production certification or permission to publish competition data.

## Exact final result

**443 collected; 443 passed in 58.32 seconds; 0 failures, 0 errors, 0 skips, 0 pytest warnings.** All **308** prior Phase 7 test identifiers remain; **135** new cases were added. The final result is generated only after the test run, source/JUnit verification, full-population reconciliation and experimental-provenance checks succeed.

Command executed:

```sh
.venv/bin/python scripts/run_final_regression.py --out-dir outputs/final_acceptance/verified_final
```

The runner executed the complete suite using `python -m pytest -v -ra --junitxml=...`, capturing full terminal output. It verified **72 application/test/config/asset source files** before and after the run, then compared the current content and exact JUnit SHA-256 before creating acceptance JSON. Documentation-only updates after the run do not alter that code snapshot.

Evidence:

- `outputs/final_acceptance/verified_final/tests.xml` — all collected test names/outcomes.
- `outputs/final_acceptance/verified_final/test_execution.log` — exact complete test output.
- `outputs/final_acceptance/verified_final/run_manifest.json` — before/after source hashes, command, UTC timestamps and JUnit fingerprint.
- `outputs/final_acceptance/verified_final/acceptance.json` — final PASS, reconciliation, provenance and scope.
- `outputs/final_acceptance/verified_final_execution.log` — acceptance-runner output.

For future changes, choose a new unused run directory; historical acceptance artifacts are not overwritten. A code/test/config/asset edit after testing invalidates the source-bound certificate. Failed/error/skipped/empty/inconsistent JUnit, missing run evidence or changed JUnit bytes cannot earn acceptance. These local hashes are reproducibility evidence, not owner-resistant attestation.

## Dataset integrity and decision reconciliation

| Measure | Verified result |
| --- | ---: |
| Validated customers | 50,000 |
| SUPPORTED | 2,052 |
| CAUTION | 20 |
| ABSTAIN | 47,928 |
| Invalid/quarantined records | 0 / 0 |
| Unexpected customer-level outcome/priority/reason changes | 0 |

Feature SHA-256: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. Manifest SHA-256: `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c`. Policy SHA-256: `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`.

The frozen technical reference in `tests/fixtures/reference_local_baseline.json` was captured before adding these tests, after comparing the current population/counts/policy to the retained Phase 7 evidence. Expected values exist only in test/reference metadata, never as hardcoded application results. A whole-population digest covers every customer key, rating, exact priority, reason-code list and invalid flag. Its final value is `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3`. This detects per-customer changes even when aggregate totals cancel out. Identifiers are used only in memory for hashing and are not exported. Presentation aliases do not determine this digest.

No canonical CSV/manifest, engine, evidence validator, decision index, analytics, builder, replay, review service, audit schema, deployment loader or historical evaluation code/artifact changed. The protected before/after hashes all match.

## Requirement-to-evidence matrix

| Requirement | Automated evidence and outcome |
| --- | --- |
| Preserve existing tests | All 308 prior identifiers retained; complete integrated run passes |
| Six gates individually and in combination | 96 status-grid cases: G2 PASS/CAUTION/ABSTAIN crossed with PASS/BLOCK at each other gate; explanations and reason codes remain consistent |
| Product suggestions cannot bypass G4/G5 | 18 restriction/suitability dashboard-index cases; no supported queue rows when G4 blocks; G5 held/no-rationale blocks remain |
| Experimental models remain separate | Prediction/segment/recommendation/priority side-channel columns cannot change index results; requesting fitted-model action fails G3 even with caller model_approved=True |
| No forged SUPPORTED action | Seven forged ratings across G1–G6 and G2 caution are rejected before creating a case/event |
| History/eligibility/type validation | Preserved boundary, malformed/unknown/missing/numerical, lineage and cohort tests pass |
| Human review | Preserved required actor/reason/acknowledgement, revision, current snapshot and SUPPORTED-only local approval tests pass |
| Stale/inconsistent evidence | Existing dataset/manifest/policy/decision/revision and pre-commit change checks reject saves, require refresh and preserve history |
| Replay/reset isolation | Real supported baseline suppresses under simulated Pending/Frozen/already-held inputs; reset restores baseline; simulated SUPPORTED is still non-actionable; canonical hash and isolated audit event count unchanged |
| Audit persistence | Existing fresh-session/fresh-Python-process persistence, append-only history, snapshot integrity, SQL/rollback/concurrency/idempotency tests pass |
| Dashboard interactions/segmentation | Existing all-nine-view navigation, selection, pagination, segmentation boundaries, product suppression, privacy and review UI tests pass |
| Decision/policy provenance | Frozen artifact/policy hashes, reason codes and existing dataset/policy/snapshot event linkage verified |
| Acceptance cannot reuse stale test results | Failure/error/skip/empty/inconsistent XML, changed source, altered XML bytes, missing run manifest and complete report generation have explicit tests |

The 96 combinations are exhaustive over that chosen representative status grid, not every possible raw input. No line/branch coverage percentage or universal proof against all future bypasses is claimed. Any new feature still needs its own meaningful behavioral tests before this acceptance workflow can approve an integration.

## Experimental output verification

No new AI inference, segmentation feature, product or dashboard interaction was implemented in this task. No fitted prediction was deployed. The currently operational method remains the same deterministic six-gate rules.

The two previously executed real-source historical evaluation artifacts were rechecked against current evaluation code and canonical feature hashes. Their cohorts/configuration and all three models' metrics/prediction fingerprints match between runs. They remain marked experimental. This acceptance run did not retrain models or produce new scores. Previously reported concept-paper values remain historical reported findings where not reproduced; they are not approved operational outputs. Single-extract historical results do not establish production calibration, fairness, external validity or intervention benefit.

## Failures found and resolved

An earlier full suite passed 441 tests in 56.62s, but the newly added report generator then hit a missing `run_evidence` assignment. No acceptance JSON/certificate was issued for that attempt. The assignment was corrected, and two integration tests were added to verify that the complete report path requires and records source-run evidence and rejects a missing manifest. Focused report checks passed 11 tests in 0.04s; the subsequent fresh full run passed all 443 tests and the acceptance generator completed successfully. The earlier diagnostic log remains in `outputs/final_acceptance/verified_execution.log`. There are **no unresolved failures**.

Negative test fixtures intentionally contain synthetic failure/error/skip XML to prove rejection. Those are passing checker tests, not suppressed regressions.

## Files added/updated

Added `acceptance_checks.py`, `scripts/run_final_regression.py`, `scripts/verify_final_acceptance.py`, `tests/test_gate_protection.py`, `tests/test_acceptance_gate.py`, `tests/fixtures/reference_local_baseline.json`, this report and `docs/DECISION_INTEGRITY_PROTECTION.md`. README links the mandatory workflow. Runtime application/business logic was not modified for these proposals. Existing Phase 6/7 workspace changes were preserved.

## Final decision and remaining limits

**Accepted for the scoped local presentation with the current verified inputs.** The six-gate engine remains authoritative; no unsupported banking action or automatic communication was introduced. SUPPORTED and APPROVED_LOCAL remain staff-review/local prototype outcomes, never authenticated bank authorization.

Public real-data deployment remains permission-gated and unverified. No restricted data was published. Cloud SQLite remains ephemeral; local SQLite is unencrypted and owner-trusted. Snapshot effective dates remain unknown and application event provenance remains feature-level. The source-bound regression gate cannot replace bank policy review, production identity/access controls or independent model validation. Any future integrated change must rerun the complete acceptance workflow and add behavior-specific tests; do not automatically rewrite the frozen reference to eliminate failures.
