# Phase 2 — implementation report

Completed November 16, 2026 (Africa/Harare). Scope: trustworthy evidence and a complete real-data manager queue. The existing Streamlit/engine/builder architecture remains. No new dependencies, ML models, dashboard pages, live banking calls, communications or financial approvals were added.

## Delivered changes

| Files | Change |
|---|---|
| `evidence.py` (new) | Shared validation for identifiers, statuses, finite/nonnegative numeric domains, integral counts, booleans and explicit portfolio evidence; safe original-value payload |
| `engine.py` | Central validation on every `Case`; six gate rows retained; machine-readable codes plus explanations for every non-pass gate; strict controls and safe arithmetic |
| `data_access.py` (new) | Required 17-column schema; row adapter; duplicate/missing-ID quarantine; complete immutable decision index; keyed aliases; content/policy/manifest-aware cache; pagination after eligibility |
| `app.py` | Full-population counters, supported queue and separate investigation lanes, stable sorting, alias filtering, pagination, matching passport selection, identity-consistent session notes and provenance explanations |
| `build_data.py` | Observation-time cohort, historical ownership conflict exclusion, future-independent deduplication, finite/type validation, explicit unknown snapshots, sidecar manifests and refusal to overwrite existing feature outputs |
| `scripts/reconcile_phase2.py` (new) | Rebuild into a new directory, compare against canonical features, attest identical canonical content with a new sidecar, never replace the canonical CSV |
| `scripts/compare_phase2.py` (new) | Aggregate comparison with audited Git baseline `01b2729`, population reconciliation, outcome differences and cold/warm timing |
| `scripts/verify_ui.py` | Content-based checks for actual counts, nonempty supported queue, pages, investigation lanes, aliases/passports/notes and controlled synthetic failure cases |
| `tests/conftest.py`, `test_evidence.py`, `test_queue.py`, `test_cohort.py`, `test_real_data.py`, `test_ui_validation.py` (new) | 100 additional regression cases; original 24 tests preserved unchanged |
| `README.md`, `.env.example`, `requirements.txt`, four Phase 2 reports | Current setup, provenance, alias, queue and verification instructions |

Local ignored artifacts include `outputs/customer_features.manifest.json`, `outputs/.presentation_alias_key`, new candidate/reconciliation evidence and test/runtime logs under `outputs/phase2/`. The secret key and datasets are excluded from Git.

## Evidence semantics and policy

The history thresholds remain **0–1 ABSTAIN, 2–3 CAUTION, 4+ pass**. Savings Account remains the only supported discussion product, and behavioural rationale plus verified portfolio evidence are still required. All actions remain staff review proposals.

Account allowed labels: Active, Frozen, Dormant, Closed, Restricted. Customer labels: Active, Dormant, Restricted, Closed, Frozen. KYC labels: Verified, Pending, Review Due, Unverified, Expired, Rejected. Only **Active customer + Active account + Verified KYC** can pass G4. Unknown/missing states cannot become eligible defaults. Normalization permits case changes and redundant whitespace for exact known labels only; no synonym such as “approved” becomes Verified.

Portfolio parsing accepts an explicit list/tuple or its literal serialization, including explicit `[]`/`()`. Missing, blank, malformed, scalar/dictionary, duplicate/case-ambiguous, sentinel or unrecognized labels fail closed. The recognized current-portfolio catalog comprises the ten labels observed in the competition extract: Call Deposit, Credit Card, Current Account, Digital Banking, Fixed Deposit, Foreign Currency Account, Mortgage, Personal Loan, SME Working Capital, Savings Account. Recognizing a held product does not authorize recommending it. Catalog changes require a deliberate policy/code change and invalidate cached decisions.

Counts must be finite nonnegative integers; recency must be a finite nonnegative integer; percentile must lie in [0,1]. Booleans cannot masquerade as numeric counts. The CSV adapter recognizes unambiguous numeric tokens and True/False serialization without imputing missing values. Missing/invalid counts remain unavailable, not zero. Subwindow/deposit counts cannot exceed total history; stored product gap must agree with holdings. Unknown evidence is assigned coded ABSTAIN or, for missing schema/ambiguous identity, a coded import/quarantine failure.

Every gate has `reason_code`, `reason_codes` and a human-readable explanation. Passports also include aggregate non-pass codes and validation issues. Safe original numeric/status/recognized-portfolio/control values are retained; raw identifiers, arbitrary malformed strings and free-text rationale are not copied into the original-value audit section. Private source-row values remain available internally for the selected case; presentation uses its alias.

G3 no longer treats a caller's `model_approved=True` as authority: there is no registered operational model, so any model-driven action abstains. G6 blocks automatic outreach or missing/invalid review requirements. Session notes are not authenticated authorization or durable audit; those remain later work.

## Complete queue and identity

Every row is validated before display limits. Valid unique identities receive one decision; all occurrences of duplicate/conflicting IDs and missing/malformed IDs are quarantined, never deduplicated by choosing a favorable row. Input rows reconcile to evaluated + quarantined rows. Invalid non-identity evidence is retained as an ABSTAIN case with reasons.

The complete index is sorted by exact composite priority descending, then presentation alias ascending. There is no 1,500-candidate cap. Filtering by decision lane and alias precedes pagination, but follows full evaluation. SUPPORTED is the sales-review lane; CAUTION/ABSTAIN are visibly labeled investigation lanes. Empty filters show an explanation; any fallback passport is explicitly labeled an unfiltered inspection case.

Aliases use HMAC-SHA256 with a persistent local 32-byte random key; the displayed `C-` token uses 24 hex digits. Every accepted dataset is checked for alias collisions; a collision aborts safely instead of assigning ambiguous identities. All 50,000 real identities have distinct aliases. Queue, selector, passport and session notes use the same mapping. Stability requires preserving the local key; a rotated/lost key intentionally changes aliases. This is presentation pseudonymization, not anonymization or user authentication.

The bounded two-entry in-process cache is keyed by CSV bytes, manifest bytes, local alias key and a fingerprint of the policy version plus engine/validation/adapter source. Dataset, manifest or policy changes invalidate the index even if the filename or filesystem timestamp is unchanged. Cached records/index are frozen, tables are fresh values, and provenance issue dictionaries are recreated from immutable JSON. There is no disk cache of raw decision records.

## Data preservation and cohort fix

Historical cohort membership now requires a valid source transaction strictly before cutoff. Future-only customers cannot change historical activity ranks. Historical duplicate detection and ownership checks are isolated from future rows. Snapshot status/holdings/service evidence remains separate and may affect current screening, not historical aggregates. Missing snapshot states are preserved as unknown; a later unknown account state cannot leave an earlier Active default in place.

The existing 17-column CSV contract is retained. Known non-fee transaction types, valid ownership/date and finite amounts are required before counting history; invalid events are excluded and counted. Output directories containing a feature CSV are never overwritten automatically.

The corrected full-source build matched canonical customer keys and all 16 non-key columns. Canonical SHA-256 remains `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. No canonical CSV or reported model metric was replaced. A new manifest attests the identical existing CSV after comparison. No approval was needed because no replacement occurred. On a future comparison difference, the reconciliation script writes a difference report and does not attest or replace canonical features; explicit approval is required before a separate replacement operation.

## Verification and scope limits

**124 tests passed, 0 failed, 0 errors, 0 skipped, 0 pytest warnings**, in **10.76 seconds**. All six content-based UI verification groups passed. Fresh Streamlit startup on port 8502 and HTTP 200 health were verified without resetting the existing port-8501 session. The temporary verification server was subsequently stopped. Dependency consistency passed. No package or lock versions changed; the direct Streamlit minimum is now 1.50 to match the tested table-width API.

The full population is **50,000 evaluated; 2,052 SUPPORTED; 20 CAUTION; 47,928 ABSTAIN; zero malformed feature cases or quarantined identities**. All before/after per-customer permission outcomes agree. The actionable queue contains all 2,052 supported cases, with 25 shown by default. See the validation, queue reconciliation and data-quality reports for measured evidence and exact commands.

Remaining limits: trusted local manifest rather than cryptographic attestation of the source's banking truth; unknown snapshot effective dates; session-only notes and no staff authentication; no model training/evaluation or real Evidence Replay; no browser visual/accessibility acceptance in this phase. Phase 3 should add navigation and explanatory intelligence views on this shared validated layer, not introduce new prediction claims.
