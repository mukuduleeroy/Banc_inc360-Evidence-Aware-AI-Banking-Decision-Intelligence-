# Mandatory regression and Decision Integrity protection

Proposals 9 and 10 are mandatory acceptance conditions for this local prototype. This document describes implemented technical checks, not production bank approval or regulatory certification.

## Operational authority

`engine.evaluate()` and the shared `data_access` case/index path remain the single source of operational recommendation status. No fitted model is registered or approved for action. Historical recency/logistic/boosting experiments remain offline and experimental. A caller-supplied `model_approved=True` cannot grant model approval: requesting model-driven action still fails G3. Additional experimental prediction, segment or recommendation columns do not override the operational index.

SUPPORTED means eligible for staff review only. It is not authenticated bank authorization, completed suitability verification or permission for automatic communication.

| Gate | Protected requirement |
| --- | --- |
| G1 | Valid identity/ownership, typed consistent data, verified lineage and temporal evidence |
| G2 | Existing historical sufficiency: 0–1 events ABSTAIN; 2–3 CAUTION; 4+ passes this gate |
| G3 | Current versioned deterministic rules; experimental/unregistered models cannot drive action |
| G4 | Current customer/account/KYC eligibility; restrictions cannot be outweighed by score or product interest |
| G5 | Existing Savings-only policy, usable ownership/rationale and already-held suppression |
| G6 | Human review and verification remain required; automatic or unreviewed actions are blocked |

A block at any gate dominates a passing score elsewhere. CAUTION does not become actionable approval. Explanations and reason codes remain attached to every gate. G6 PASS denotes the human-control requirement, not a completed bank authorization.

The review service independently revalidates current disk evidence, policy, case revision and inspected snapshot before committing. Stale data/manifest/policy or changed decision blocks review until explicit refresh/reinspection. Events and snapshots remain append-only through the application. Replay copies permitted fields, is always SIMULATED/non-actionable, and cannot create a real review case or alter canonical data.

## Required acceptance workflow for future changes

1. Identify changed behavior and add tests for new inference, segmentation, recommendation or dashboard interactions. Preserve all existing test cases. Do not substitute visual smoke tests for decision/eligibility tests.
2. Keep experimental outputs out of operational paths unless an actual approved-method process and its tests have been established. Do not use a caller flag, high score or displayed product suggestion to bypass G4/G5/G6.
3. Run the entire integrated suite and the source-bound acceptance checker:

   ```sh
   .venv/bin/python scripts/run_final_regression.py --out-dir outputs/final_acceptance/run-new
   ```

   Choose an unused directory. The runner records source/test/config hashes before and after pytest, the exact JUnit fingerprint, UTC times, complete test output and acceptance JSON. It refuses to overwrite historical evidence.
4. Acceptance requires zero test failures, errors and skips, all prior Phase 7 test identifiers retained, unchanged reviewed dataset/manifest/policy, whole-population decision reconciliation and verified experimental provenance. Missing authorized data or historical artifacts cannot be called a successful full-data acceptance.
5. Inspect `acceptance.json` and the final report. An old XML alone is insufficient. Source changes during/after testing, altered JUnit bytes or an unsuccessful run are rejected. Re-run after integration changes. Documentation-only edits do not invalidate the application/test snapshot.
6. Do not auto-update the frozen reference to make failures disappear. Any intentional dataset/policy/priority/reason change requires documented justification, reviewed provenance and a separately reviewed new reference before acceptance. Do not weaken gates to restore a preferred count.

## Frozen baseline and new coverage

`tests/fixtures/reference_local_baseline.json` contains aggregate counts and fingerprints only. It is a verified local technical reference, not bank approval or release permission. `acceptance_checks.decision_fingerprint()` hashes all 50,000 customer-key/outcome/exact-priority/reason/invalid-flag tuples in memory, sorted by internal customer key. Raw identifiers and individual decisions are never exported. Thus a redistribution of outcomes that leaves aggregate counts unchanged is still detected. Alias rotation does not change this decision fingerprint, because the presentation alias is not its key.

`tests/test_gate_protection.py` adds 96 representative status combinations: G2 PASS/CAUTION/ABSTAIN crossed with PASS/BLOCK for G1/G3/G4/G5/G6. This is exhaustive over that chosen status grid, not every possible raw input. It also tests 18 G4/G5 product/dashboard combinations, forged SUPPORTED rejection, model-column noninterference, frozen real-population reconciliation and real replay/reset isolation.

`tests/test_acceptance_gate.py` verifies that failed/error/skipped/empty/inconsistent evidence, post-test source edits and changed JUnit bytes cannot earn acceptance. Secret files and datasets are excluded from the source snapshot; canonical data/manifest are separately pinned and verified. The source/JUnit manifest is local reproducibility evidence, not a tamper-proof external attestation.

Existing tests additionally cover numerical/schema invalidity, eligibility boundaries, all nine native routes, shared selection, analytics segmentation, product suppression, stale evidence, concurrent reviews, idempotency, rollback, immutable snapshots/events, UTC actor attribution, fresh-process persistence and simulation isolation. No application, engine or review business logic was changed for these proposals.

## Scope and remaining boundaries

No new inference, segmentation feature, product or dashboard interaction was introduced by this testing work. New behavior still requires explicit tests and review; a passing generic suite cannot prove the correctness of every future feature automatically. The final acceptance report is scoped to current local code and authorized artifacts.

No communications, real banking API or dataset publication occurs. Public real-data deployment remains permission-gated and unverified. Cloud SQLite remains ephemeral; local SQLite is unencrypted and owner-trusted. Current snapshot effective dates remain unknown, and application provenance is feature-level. Reproduced historical model results do not establish production validity, calibrated probabilities, intervention benefit or fairness. Historical concept figures must remain labeled as reported where they were not reproduced; none becomes an operational prediction.
