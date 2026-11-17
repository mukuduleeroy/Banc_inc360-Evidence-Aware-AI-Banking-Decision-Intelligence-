# Phase 5 presentation runbook

The demonstration runs locally and offline using the existing feature CSV, matching manifest, private alias key and disposable managed SQLite database. Model packages are optional for offline research; no model is approved or invoked by the app.

## Start

```sh
# One time for a new managed demonstration directory:
.venv/bin/python scripts/presentation.py init
# Normal startup (already initialized in this workspace):
.venv/bin/python scripts/presentation.py start
```

Open http://127.0.0.1:8505. Existing Phase 4 preview/database is independent. `.env` files are not auto-loaded. `--root` selects a separate managed folder; `--port` changes the local port. Startup verifies feature fingerprint, manifest provenance, policy and alias key against the managed configuration. If they change, inspect the change before explicit reset/reinitialization.

Current managed configuration: `outputs/phase5/demo/demo.json`. Stable examples with the existing private key:

| Outcome | Real-source alias | Demonstration |
| --- | --- | --- |
| SUPPORTED | `C-4620B382895C1E428483A2FF` | Six gates pass; staff-review candidate only |
| CAUTION | `C-999D124405DED97E57819E62` | Borderline history/investigation; approval unavailable |
| ABSTAIN | `C-546C667C281C61AC638FD044` | Explain the actual blocking gate codes; no sales approval |

Use the sidebar alias search and selector for exact examples. Preserve `outputs/.presentation_alias_key` privately to retain aliases. Never display/search raw identifiers. Aliases and derived profiles remain sensitive pseudonymous material, not anonymized public records. Reviewer reasons must contain no personal data or credentials.

## Five-minute journey

1. Executive Overview: real population 50,000; 2,052 SUPPORTED, 20 CAUTION, 47,928 ABSTAIN. Show actual data fingerprint/cutoff and explain rules, not deployed ML.
2. Supported Customer 360: historical recency/count/volume versus explicitly current snapshot status/KYC/holdings. Inactivity is descriptive; relationship volume is not profit.
3. Decision Passport: inspect G1–G6, reasons and provenance; no invented source-event drilldown. Snapshots have unknown effective date.
4. Evidence Replay: Verified baseline SUPPORTED → explicitly SIMULATED Pending KYC ABSTAIN → Reset SUPPORTED. No review action or actual customer state change occurs in replay.
5. Manager Work Queue: open a case, explicitly choose DEMO-RM-01, inspect passport, enter a local review reason and acknowledgement, approve locally. Show APPROVED_LOCAL; no bank authorization or communication.
6. Stop this preview and restart the same startup command. Audit & Validation Evidence retains OPEN/APPROVE, demo actor, UTC, fingerprints and snapshots.
7. Select the CAUTION/ABSTAIN alias to show investigation controls. Use the recorded isolated stale acceptance evidence rather than replacing canonical data live.
8. Show historical model comparison as a separate offline experiment. Recency reported figures reproduce; the newly specified logistic result differs from the original report. High held-out scores on this extract do not demonstrate production retention benefit.

## Backup and reset

```sh
.venv/bin/python scripts/presentation.py status
.venv/bin/python scripts/presentation.py backup --out outputs/phase5/demo-backup-new.sqlite3
# Stop the demo server before reset; then:
.venv/bin/python scripts/presentation.py reset
.venv/bin/python scripts/presentation.py start
```

Backup uses SQLite's consistent online API and refuses overwrite. Reset switches the managed pointer to a new empty database generation; previous databases remain and a backup is retained. It does not delete events, rewrite canonical data, rotate aliases or touch Phase 4 databases. A running process continues using its old generation until restarted, so stop/start explicitly. Reset refuses unmanaged nonempty folders. Preserve the source feature/manifest versions and private alias key alongside restricted backups. SQLite is unencrypted, owner-trusted storage.

## Evidence and fallback

Evidence package: `outputs/phase5/presentation_evidence/`, including verified screenshots, replay baseline/Pending/reset, passport, local review, audit after process restart, final tests and historical results. These captures show real competition features except the clearly marked replay modifications. The acceptance DB is separate at `outputs/phase5/acceptance_verified/demo/`; its history remains available independently of the fresh presentation DB.

If a prerequisite or hash fails, stop and investigate; do not bypass gates. If the live server is unavailable, use the labeled recorded evidence and explain that it is a capture. No external API, login, production approval or customer communication is needed or provided. The optional evaluation install is a preparation step, never an internet dependency during presentation.
