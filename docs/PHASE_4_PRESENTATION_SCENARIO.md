# Phase 4 presentation scenario

## Preparation

Use the authorized local data and existing environment. Keep screenshots and SQLite files private. Choose an unused database for a new rehearsal; the verified preview currently uses `outputs/phase4/presentation.sqlite3` and already has one locally approved case with two events.

```sh
env BANCINC_AUDIT_DB=outputs/phase4/presentation.sqlite3 .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8503 --server.headless true --browser.gatherUsageStats false
```

Open http://127.0.0.1:8503. Keep the alias key and feature/manifest versions stable across the restart. Do not change the canonical data for the demonstration.

## Live review and restart

1. Executive Overview: 50,000 customers; 2,052 SUPPORTED, 20 CAUTION, 47,928 ABSTAIN. Describe deterministic evidence controls, not a trained prediction.
2. Manager Work Queue: complete eligible population with local case state, last demo reviewer, latest action and timestamp. Open a SUPPORTED passport.
3. Inspect the six gates. Select a demo reviewer explicitly. Explain that this is an unverified demonstration identity. Open the local case if new.
4. Choose Approve, supply a demonstration reason without personal data, tick the inspected-passport acknowledgement and save. Point to APPROVED_LOCAL and the no-bank-authorization/no-outreach message.
5. Stop only this preview process, restart the same command and reopen the case. Approval persists. Audit & Validation Evidence shows OPEN/APPROVE, reviewer, UTC times, immutable snapshots and hashes. The verified rehearsal case is `CASE-d56bbff520e94d0cb3caede0daa8a531`; do not resave it merely to show persistence.
6. Expand references: eight feature-level derivations; no transaction event mapping is claimed. Current KYC/status/holdings are explicitly separate from historical cutoff features.
7. Evidence Replay: select Pending KYC, observe simulated ABSTAIN without durable action controls, reset and recover SUPPORTED. Audit history is unchanged.

## Stale evidence proof without altering canonical data

Use the isolated real-source rehearsal described in the validation report. It opens/approves against July, switches to an independently rebuilt January-cutoff artifact, blocks stale review, explicitly refreshes and defers, and verifies unchanged historical snapshot plus backup in a new process. Show `outputs/phase4/persistence_demo.json` and the rehearsal DB through the local audit inspector if needed. The January build is real source data with a different observation cutoff; it is not current bank status or a fabricated customer scenario.

For a separate UI stale-context demo, start a separate preview with `BANCINC_AUDIT_DB=outputs/phase4/process_rehearsal.sqlite3` and `BANCINC_FEATURES_PATH=outputs/phase4/alternate_jan/customer_features.csv`. Preserve this rehearsal database or make a backup before further reviews. Never silently replace canonical features or rewrite audit history for presentation.

## Evidence and ending

Show the recorded 229-pass test result, all-nine-page browser evidence and actual restart screenshots from the validation report. Explain the limits precisely: unverified demo attribution, local unencrypted SQLite, trusted local provenance, unknown snapshot effective dates and feature-level traceability. Recommend timestamped source inputs and verified event lineage before production reviewer/access/audit hardening. No communications or real banking API calls occur.
