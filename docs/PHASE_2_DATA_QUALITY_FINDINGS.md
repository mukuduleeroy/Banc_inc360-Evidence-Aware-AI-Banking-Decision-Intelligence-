# Phase 2 — data quality and historical cohort findings

Date: **November 16, 2026 (Africa/Harare)**. Distinguish malformed evidence, recognized ineligibility and excluded identities. The real-data counts below are measurements, not expectations encoded in tests.

## Findings and resolution

| Phase 1 finding | Phase 2 handling |
|---|---|
| Malformed/missing holdings became empty portfolio | Explicit empty lists remain valid; all missing/malformed/ambiguous/unrecognized portfolio evidence abstains with `INVALID_HOLDINGS` |
| Unknown/missing account or KYC could be eligible | Exact allowed-state catalogs; only Active customer/account plus Verified KYC can pass; coded unknown-state failures |
| NaN/infinite/negative/nonnumeric counts and out-of-domain scores | Central validation, no implicit zero; safe priority arithmetic; coded ABSTAIN |
| Missing or duplicate/conflicting identities | All ambiguous identity rows quarantined with row-position/reason codes; no arbitrary winner and no raw ID logs |
| Stored gap inconsistent with holdings | `INCONSISTENT_PRODUCT_GAP`, ABSTAIN |
| Future-only customer changed historical percentile | Historical cohort requires a valid transaction before cutoff; future-only customers excluded from historical ranking |
| Future duplicate could suppress historical event | Separate historical/future deduplication sets |
| Invalid-first duplicate suppressed later valid event | Validate before adding to accepted duplicate sets |
| Ownership conflicts not checked across historical rows | Customers affected by conflicting historical account owners excluded and counted |
| Unknown type/invalid amount still counted as an event | Six known competition transaction types; SERVICE FEE excluded from history; non-finite/invalid amounts and unknown types excluded/counted |
| Later malformed snapshot could leave earlier Active state | Snapshot normalization preserves unknown/restrictive evidence; cannot silently retain Active |
| Unversioned CSV/cached decision lineage | Companion manifest checks schema, content hash, cutoff, source fingerprint, builder/event definition, verification status and row count; cache keys include all content and policy inputs |
| Caller could assert model approval | No operational model registry entries exist; model-driven action abstains even with a caller approval flag |

Status and portfolio normalization is limited to known exact labels with case/whitespace variants. No unknown KYC becomes Verified, no unknown account becomes Active and no missing count is imputed to zero. Safe original nonidentifying fields are retained; malformed strings potentially containing personal data are redacted from audit payloads. Display output contains no raw customer/account ID.

## Fresh source and feature results

The corrected builder processed **1,048,575 source records** into **50,000 customer features**. On this source:

| Rejected/excluded source category | Count |
|---|---:|
| Invalid source identifiers | 0 |
| Invalid ownership links | 0 |
| Invalid transaction dates | 0 |
| Duplicate transaction IDs | 0 |
| Invalid/non-finite amounts | 0 |
| Unknown transaction types | 0 |
| Historical ownership-conflict customers | 0 |
| Future-only customers excluded from historical cohort | 0 |

The imported canonical feature index has **zero malformed-evidence cases and zero quarantined identity rows**. Missing deposit rationale is not fabricated or treated as a malformed portfolio; a valid empty rationale continues to withhold offers through G5. Current non-Verified KYC or restricted status is recognized ineligibility, not a malformed record.

Real permission distribution remains **2,052 SUPPORTED; 20 CAUTION; 47,928 ABSTAIN**. Per-customer comparison with Phase 1 found **zero changed outcomes**. All 50,000 identities received checked-unique aliases. These facts do not imply every customer is eligible or that every source snapshot is current.

## Historical correction and comparison

The builder's cutoff is exclusive. At July 1, 2026, historical lookbacks begin January 2 (180 days) and April 2 (90 days), inclusively. Recency can refer to older pre-cutoff non-fee history. Parsing is mixed-format, day-first, timezone-naive; an invalid, timezone-aware or non-midnight cutoff is rejected rather than silently shifted.

Historical membership now requires a valid source transaction and identifiers before the observation cutoff. Missing cutoffs cannot default to the present time; imported manifests require an explicit ISO date. A customer first appearing afterward cannot alter earlier percentile denominators. Historical account ownership conflicts and accepted duplicate IDs are computed without using future rows. Current KYC, current account/customer status, holdings, service issues, segment and total account breadth remain separate snapshot fields. They must not be used as historical predictors. The current triage score deliberately includes a snapshot service flag and is labeled accordingly.

Tests prove future-only customer invariance, future transaction/dedup independence, current-snapshot changes without historical changes, and separate January 1 training-observation versus July 1 holdout-observation cohort membership. This is feature-construction testing: no training, fitted model, future-label evaluation or reported performance reproduction is claimed.

All 50,000 customers in the supplied source already had valid pre-cutoff history. Consequently the safe correction produces **identical customer keys and identical values in all 16 non-key feature columns**. The canonical CSV remains byte-for-byte unchanged. The compared candidate is at `outputs/phase2/input_integrity_verification/candidate/customer_features.csv`; the comparison is `outputs/phase2/input_integrity_verification/reconciliation.json`. No canonical output or concept-paper metric was silently updated.

The code refuses to overwrite an existing feature CSV. On other datasets, new cohort/validation rules may change rows or values; the reconciliation helper emits the difference and withholds canonical attestation/replacement. Explicit approval is needed before replacing canonical data; this phase required no such replacement.

## Identity, security and remaining limitations

Presentation aliases are deterministic HMAC tokens backed by a private 32-byte key stored at ignored `outputs/.presentation_alias_key` with mode 0600 on this platform. Collisions are checked across each accepted dataset. Preserve this key securely with authorized local configuration if aliases must remain stable; losing/rotating it changes the mapping. Never commit it. The mapping is pseudonymization, not anonymization.

The companion manifest was created from an actual source rebuild and comparison. A local operator who can alter the manifest/code can falsify local metadata; hashes are integrity fingerprints, not signatures or external banking provenance. The app verifies content/metadata consistency but does not re-read the 633 MB source CSV on every interaction. Snapshot effective dates are unavailable and explicitly marked unknown. Staff must verify present suitability before any action.

Staff review notes remain session-only, without authenticated reviewer authorization, durable storage, tamper evidence or retention controls. Free-text notes can contain personal data typed by staff; the UI asks users to avoid it. No communications or financial approval path exists. The only review operations are Review/Investigate/No action, and an empty reason is rejected.

The recognized holdings catalog may need reviewed expansion for future datasets; unknown products intentionally abstain rather than implying absence. The historical cohort definition is based on observed valid transactions, not verified account-opening dates. No new ML model, nine-page UI, full Evidence Replay or browser visual/accessibility acceptance was added. These are explicitly deferred capabilities.
