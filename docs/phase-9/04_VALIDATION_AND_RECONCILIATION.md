# Validation, reconciliation and snapshot behavior

## Admission and privacy

The interface shows filename/size, received SHA-256, detected/required/missing fields, validation errors by category and row number, date/type/numeric/currency/identifier/ownership/duplicate counters and missing-evidence warnings. Errors contain fixed guidance, not submitted values or customer IDs. Source rows stay in a private generated staging location; user filenames never become paths.

Schema errors, invalid dates/types/numbers/identifiers, conflicting transaction IDs, inconsistent account ownership, unsupported currencies, malformed CSV, size/row limits and missing historical cohorts fail closed. Unknown status/KYC/blank ownership is warned and follows the existing engine's abstention semantics. Exact duplicates are explicitly reported, not silently discarded. No synthetic evidence is substituted for an uploaded missing field.

Validation is rerun against the same staged-content fingerprint when processing starts. Byte changes or receipt mismatches block processing. The staged CSV is copied into the private candidate; its hash must still match the upload receipt. It is packaged internally as a single-CSV ZIP only to reuse the existing builder; both CSV and ZIP fingerprints are recorded, with the latter bound to the generated source manifest.

## Synthetic reconciliation reference

`outputs/phase9/examples/synthetic-valid.csv` contains **14** independently invented transactions, **4** distinct customers/accounts. At observation date **2026-07-01**, unchanged rules produce:

| Measure | Result |
|---|---:|
| Uploaded rows | 14 |
| Accepted unique source rows | 14 |
| Exact duplicate rows | 0 |
| Invalid/quarantined rows | 0 |
| Evaluated customers | 4 |
| SUPPORTED | 1 |
| CAUTION | 1 |
| ABSTAIN | 2 |
| Decision coverage | 100% |

Scenarios: sufficient qualifying deposits; borderline three-event history; insufficient one-event history; Pending KYC. These outcomes arise from existing rules and have no bank approval. No restricted customer row was copied or modified to create them.

An added exact duplicate test reconciles 15 uploaded rows = 14 accepted unique rows + 1 duplicate. Invalid inputs are rejected as datasets and never receive an activatable snapshot; they are not partially accepted with silent row loss.

## Candidate acceptance

Builder audit must show no unexpected invalid identifiers/links/dates/amounts/types, ownership-conflict customers or post-cutoff-only exclusions. Its duplicate count must match admission. Feature header must match the existing 16-column order. Index lineage must verify; no duplicate/invalid customer exclusions are allowed; evaluated customers must equal distinct source customers. SUPPORTED + CAUTION + ABSTAIN must equal evaluated customers exactly. Invalid evidence can still correctly produce ABSTAIN; those decisions are disclosed and are not fabricated supported actions.

Snapshot metadata records schema, unique ID, observation date/time, validation status, source/ZIP/feature/policy hashes, missing-evidence counters, counts/coverage, decision digest and processing code hashes. Materialized alias-only decisions are checked against fresh existing-engine output. Priority calculation remains the original `.45 × min(recency/90,1) + .35 × activity_percentile + .20 × service_issue`; no historical model scores enter it.

Required disclosure: **These outcomes are generated using the existing prototype decision policy. They are not bank-approved outreach, credit or product decisions.**

## Immutability, activation and recovery

Completed snapshots are published under random IDs by directory rename and registered by receipt hash. No snapshot file is overwritten by activation, rollback or cleanup. A candidate is not automatically active. The registry stores activation status separately from immutable snapshot metadata; CREATE/ACTIVATE/ROLLBACK_BASELINE events contain no source identifiers.

Activation is explicit and rechecks registered receipt, all fixed artifact hashes, source/manifest association, policy/code versions, regenerated decisions and reconciliation. On failure, prior active selection remains. Logical immutability is enforced by hash verification and never rewriting snapshots; this is not hardware write-once storage and cannot prevent the machine owner editing files.

Locked state updates use checksummed JSON, temporary files, fsync and atomic replacement. The previous committed registry is retained. An unreadable current file recovers the last committed backup; both unreadable files fail closed rather than erase snapshots. Recovery may restore the previous selection, so the operator must inspect the displayed active state and explicitly re-activate if needed. Orphans/interrupted temporary files do not become active automatically.

Explicit rollback sets the companion selection to baseline without touching canonical artifacts or histories. The original app is unaffected throughout. Explicit upload discard, changed-upload/date cleanup and successful-processing cleanup remove only generated staging-token files. A disconnected browser may leave a private staged upload; operators can retain or remove that managed Phase 9 staging data locally after stopping the companion. Snapshot cleanup/deletion is deliberately not provided.

## Prototype limitations

5 MiB/25,000-row compatible USD-normalized CSV only; full competition-sized source ingestion is outside this controlled demo limit. Preview is capped at 50 engine-ranked aliases. No supplier authentication, production authorization, encryption-at-rest, production audit database, live fitted inference or customer communication is claimed. Local HTTP for the demo browser is loopback only; no banking data is sent to outside APIs.
