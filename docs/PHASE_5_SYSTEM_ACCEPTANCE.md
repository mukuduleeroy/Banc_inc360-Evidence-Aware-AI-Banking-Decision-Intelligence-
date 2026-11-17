# Phase 5 system acceptance

Executed 2026-11-16 on the existing local repository. Baseline verification before implementation: **229 passed in 48.23s**, population 50,000 with 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN. The eight protected engine/data artifacts matched the Phase 4 baseline. Prior Phase 1–4 implementation, validation, presentation and roadmap documents were inspected.

## Final regression

```sh
.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase5/tests.xml
```

**261 collected, 261 passed in 84.33s; 0 failed, errors, skipped or pytest warnings.** All 229 Phase 4 case identifiers are retained. Thirty-two new tests cover temporal boundaries, qualifying activity/targets, future and snapshot leakage prevention, cohort grouping, deterministic fitted evaluation, metric ties, provenance, paired bootstrap, invalid-source rejection, managed reset/history retention, safe paths, private environment configuration, fresh-process persistence, full native navigation/replay/review and stale rejection. Initial focused tests ran before the real-source artifact existed and reported one explicit skip; the final full run has none. An initial physical-core discovery warning was resolved with an explicit single-worker discovery setting in the evaluation CLI and model test, without suppressing warnings globally.

## Complete workflow evidence

| Acceptance step | Verified result |
| --- | --- |
| Launch and validated real data | Fresh Streamlit server, healthy local endpoint, expected population counts |
| Executive Overview and safe customer selection | Actual Chrome render and stable selected C- alias |
| Customer 360, inactivity and relationship value | Native pages rendered with real historical indicators and separate snapshots |
| Real SUPPORTED Passport | All six existing engine gates displayed; actual supported example |
| KYC replay | Baseline SUPPORTED → explicitly SIMULATED Pending KYC ABSTAIN |
| Replay reset/isolation | Reset SUPPORTED; no action controls or canonical/audit mutation |
| Manager review | Explicit DEMO-RM-01; required reason and acknowledgement; APPROVED_LOCAL |
| Actual server restart | Server process terminated/relaunched with same isolated DB; approval remained |
| Persisted audit | One case, two events, two snapshots, sixteen feature references after restart |
| Stale data | Separate real January build rejected old context; explicit refresh/defer appended history |
| No banking action | Authorization/outreach false; no banking API or communications integration |
| Prior records/data | Phase 4 audit summaries, alias key and protected artifact hashes unchanged |

Browser command: `.venv/bin/python scripts/accept_phase5.py --out outputs/phase5/acceptance-new`. Existing Chrome and Node are required for this optional verification helper; no browser package was installed. It starts its own server on 8506 and isolated CDP on 9223, creates a new managed database, and stops only its own processes. Reuse requires a fresh output directory. The normal presentation database is never opened for mutation by acceptance.

Successful evidence: `outputs/phase5/acceptance_verified/acceptance.json`, browser verification/create/reopen JSON and logs, and viewport screenshots. The initial attempt in `outputs/phase5/acceptance/` failed in browser-driver checkbox timing after a scroll. Its OPEN event is retained in that disposable DB. The driver was corrected to wait for scrolling and selection before clicking; a fresh independent acceptance run then passed. No application gate or acknowledgement requirement was weakened.

Stale replay command executed:

```sh
.venv/bin/python scripts/verify_phase4_persistence.py --alternate outputs/phase4/alternate_jan/customer_features.csv --db outputs/phase5/stale_acceptance.sqlite3 --backup outputs/phase5/stale_acceptance_backup.sqlite3 --out outputs/phase5/stale_acceptance.json
```

The alternate January artifact was built from actual source in Phase 4, not fabricated data. A fresh process read approval; switching dataset rejected stale review without a write; refresh/defer preserved the original snapshot and yielded four complete events. Backup verified. Canonical data unchanged.

## Delivery and readiness

Created `historical_evaluation.py`, `presentation.py`, optional evaluation requirements/lock, evaluation/presentation/acceptance/performance CLI helpers, two new test modules and five Phase 5 reports. Updated only UI explanatory/test-artifact text, configurable browser helper output/CDP settings, README and environment guidance. The approved engine, builder, feature/index layer, analytics and replay remain byte-identical. Existing audit schema/history is preserved.

Evidence package: `outputs/phase5/presentation_evidence/`. It contains screenshots, final JUnit/text results, aggregate evaluation/uncertainty/provenance, performance, acceptance and preservation evidence. It excludes raw data, databases, private alias key and individual predictions. Screenshots are actual viewport captures; review derived information before sharing.

**Ready for the scoped local hackathon demonstration**, with the stated model/data/authentication/lineage limitations. Critical acceptance checks passed. This is not production authorization, security/accessibility certification, transaction-level replay or evidence of real retention impact. Use the presentation runbook and retain a recorded-evidence fallback.
