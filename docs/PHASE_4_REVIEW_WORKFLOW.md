# Phase 4 review workflow

1. Start the existing app with a durable database path. Open Manager Work Queue in real-source mode. Its 2,052 SUPPORTED cases still come from the complete 50,000-row engine evaluation. Optional local-case filtering does not change eligibility.
2. Open a selected customer's Decision Passport and inspect all six gates. Select a demonstration reviewer explicitly; no default identity is assigned. DEMO-RM-01, DEMO-RM-02 and DEMO-AUDIT-01 are unverified labels, not authentication or separate production roles.
3. Open the local case. This appends OPEN with the selected reviewer, an immutable passport snapshot and eight feature references. Reopening an existing case does not duplicate OPEN.
4. Choose Approve, Defer or Reject, enter a required nonblank reason (maximum 2,000 characters), and acknowledge inspecting the current passport. No raw customer secrets in reasons. Save records the actor, reason, UTC time, hashes and snapshot atomically.
5. Inspect the updated case and timeline. APPROVE means APPROVED_LOCAL only. It grants no bank authorization and initiates no communication. CAUTION and ABSTAIN offer Defer/Reject for investigation; backend and database also block their approval.
6. Audit & Validation Evidence reads durable cases, complete event sequences, snapshots and feature references. A new browser session and restarted process read the same history.

## Changed evidence and conflict handling

The service independently reloads and validates the current feature/manifest data and engine passport; caller UI outcome text cannot authorize a review. It compares alias, feature and manifest hashes, policy hash/version, current decision hash, inspected snapshot and expected revision. It checks evidence again before commit. Policy code changes in an already running process require reload; they cannot silently reuse the imported old policy.

Any stale/mismatched context blocks saving, including Defer/Reject, until the reviewer explicitly refreshes the case with a reason. REFRESH adds a new immutable snapshot and event; it never changes the old snapshot or approval. The case becomes OPEN for current SUPPORTED evidence or INVESTIGATION_REQUIRED otherwise. Inspect the refreshed passport and acknowledge again before a new review. Changes to actor/context/revision clear the draft acknowledgement. A changed revision from another reviewer requires reinspection. Identical submission tokens are idempotent; conflicting duplicates fail visibly. Storage errors do not produce a success message or partial audit records.

The queue shows effective stale status separately from previously recorded local status. No durable reviewer assignment or task-routing engine is claimed: it shows the last demo reviewer, while the passport shows the currently selected actor. Legacy session notes remain visibly labeled as non-durable notes, separate from this workflow.

## Simulation boundary

Evidence Replay remains a copied, explicitly SIMULATED workbench, with no durable review controls. Simulated SUPPORTED and ABSTAIN contexts are both rejected by the real review service. Reset restores the original customer decision. Replay writes neither canonical features nor real audit events. Synthetic demonstrations do not supply portfolio metrics or source evidence.
