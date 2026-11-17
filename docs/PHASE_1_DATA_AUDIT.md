# Phase 1 — data correctness and security audit

Audit date: **November 16, 2026 (Africa/Harare)**. All findings derive from existing local files or explicitly synthetic controlled probes. Original datasets and the default generated feature CSV were preserved.

## Source and fresh measurements

Source: `/Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip`, containing one CSV with **64 fields**. Existing extracted copies also exist in Downloads; this audit read the ZIP. The builder reads 14 selected fields from its denormalized rows; it does not perform a multi-table merge.

| Check | Fresh result |
|---|---:|
| Transaction rows | 1,048,575 |
| Unique transaction IDs | 1,048,575 |
| Customers | 50,000 |
| Accounts | 98,475 |
| Missing customer/account/transaction IDs | 0 / 0 / 0 |
| Invalid dates | 0 |
| Customer-to-account ownership-column mismatches | 0 |
| Accounts associated with multiple customer IDs | 0 |
| Duplicate transaction IDs | 0 |
| Missing/invalid/non-finite transaction amounts | 0 |
| Zero/negative source amounts | 0 / 0 |
| Source time coverage | 2022-10-01 00:19 to 2026-10-30 23:52 |
| Events on/after July 1, 2026 | 57,724 |
| Historical non-fee events before cutoff | 825,720 |

Six type labels occur: SERVICE FEE, FOREX_PURCHASE, CASH_DEPOSIT, POS_PURCHASE, ATM_WITHDRAWAL, BILL_PAYMENT. Each occurs 174,762 or 174,763 times. These measurements characterize the supplied competition extract, not independently authenticated production banking records.

Current snapshots are constant within each customer's rows in this file: zero customer-level conflicts in customer status, account status, KYC or product-holdings strings. This does not establish their effective dates or freshness.

## Feature contract and reproduction

`outputs/customer_features.csv` has **50,000 unique customer rows, 17 columns**. It contains five historical numeric measures (`qualifying_events_180d`, `events_90d`, `recency_days`, `transaction_volume_180d_usd`, `deposit_events_180d`), historical-derived deposit rationale/activity percentile, current holdings/status/KYC/service/segment/account breadth, and an identifier. `product_gap` is a current holdings-derived field. Product holdings are serialized Python-list strings, parsed with `ast.literal_eval` by the app.

An independent chunked aggregation matched all five historical numeric measures for every customer: **zero mismatches**. A fresh call to the existing feature builder wrote into **`outputs/phase1_audit/rebuild/`**, not the default output. Its 50,000 customer keys and all 16 non-key columns match the supplied feature file exactly. Preservation hashes verify that the original feature file was not altered.

All numeric and status fields in the supplied feature table are populated. `behavioural_reason` is blank/missing for **34,363** customers; this is an absence of qualifying deposit rationale, not a value to impute with invented evidence. Existing product serializations are all parseable. There are no duplicate customer rows.

Status distributions:

| Field | Counts |
|---|---|
| Customer status | Active 30,039; Dormant 10,000; Restricted 9,961 |
| Account status | Active 30,039; Dormant 10,000; Frozen 9,961 |
| KYC | Verified 16,667; Review Due 16,667; Pending 16,666 |

## Temporal validity

The implemented event boundary is **event time < cutoff**. At July 1, 2026, the inclusive 180-day lower boundary is **January 2, 2026**, and the 90-day lower boundary is **April 2, 2026**. Recency uses the most recent qualifying event before cutoff, including older history; `.days` floors sub-day differences. Times are parsed as day-first, timezone-naive; the source timezone is not established.

Current KYC, customer/account status and holdings are not inputs to these five historical aggregates. They do affect **current** suitability gates, as intended. Snapshot `service_issue` contributes to the current illustrative triage score; that score must not be presented as a purely historical inactivity prediction. `account_count`, product breadth, segment and service fields are assembled across all observed source rows and must not be used as historical predictors without point-in-time reconstruction.

A subtle cohort issue remains: `build_data.py` creates customer state for valid rows before applying the historical cutoff, then ranks volumes across every state. In a controlled synthetic fixture, adding a customer first seen after cutoff changes another customer's percentile from **0.5 to 0.6667**, despite unchanged prior transactions. Thus the implementation is **not generally point-in-time safe at the population level**. In the actual supplied extract, all 50,000 customers have a pre-cutoff non-fee event, so this specific post-cutoff-only population effect was **not observed**. A source-registration/opening-time policy is still needed before claiming general historical reliability.

No training pipeline, future inactivity labels, saved model or evaluation script exists. The January 1 training / July 1 holdout / future 90-day evaluation design is **not implemented or independently verified**. Supplied model performance figures remain reported findings. Source coverage through October 30 is sufficient in duration for a July 1 outcome window but does not establish correct labels, cohort or performance.

The feature CSV does not carry its cutoff, transaction definition, source hash, build version or snapshot date. Its companion JSON is not consumed/validated by the UI. A file built at another cutoff can therefore be imported while the UI still announces July 1. This is a provenance risk, not evidence that the currently verified file uses the wrong cutoff.

## Qualifying events, joins and invalid-input handling

Current rule: every valid transaction before cutoff except the exact case-normalized type **SERVICE FEE** counts as an event. CASH_DEPOSIT counts separately; two or more deposits generate a savings-discussion rationale. Product ownership and demographics are not historical predictors. No approved bank policy validating this qualifying-event definition is included in the repository.

The source has no bad joins or duplicate IDs. The builder excludes missing IDs, bad ownership links, invalid dates and repeated transaction IDs. It does not validate that one account always belongs to the same customer across rows; this audit independently checked that invariant. Its ID is marked “seen” before row validation, so an invalid first occurrence could suppress a later valid duplicate. No such case was found in the source.

Malformed amount text is converted to zero while the event still counts; unknown/missing type labels can also count as qualifying events. A synthetic probe with `UNRECOGNIZED_TYPE` and amount `bad` produced one qualifying event with zero volume. NaN/infinite floats can propagate because coercion only catches conversion exceptions. None of these amount anomalies were observed in the supplied source.

Snapshots are selected/aggregated conservatively for restrictions, but not by effective timestamp. Unknown or missing account statuses are not generally rejected by G4. Missing KYC/customer status blocks because they differ from required values. Whitespace/casing and enumerated-domain normalization are not defined. Missing feature columns cause a helpful error, but numeric domains, duplicate keys, malformed row types and cutoff metadata are not validated at load time.

Malformed product holdings are particularly unsafe: both detail and queue parsing catch errors and substitute empty holdings. A controlled corrupted-feature AppTest produced **SUPPORTED**. Missing ownership evidence must instead produce an unknown/invalid suitability result; it must not be interpreted as proof of no existing product.

## Decision and queue measurements

All source-derived features evaluated under current rules yield **2,052 SUPPORTED, 20 CAUTION, 47,928 ABSTAIN**. G4 blocks 39,928 customers; G5 blocks 37,483. These counts overlap and must not be summed as disjoint cohorts. G1/G3/G6 pass all source-derived cases because the app supplies trusted defaults and uses rules; this is not independent proof of identity/temporal validity, model approval or logged authorization.

The top 1,500 unfiltered priority candidates are **all ABSTAIN**. Consequently the default real-data queue is empty despite supported customers elsewhere. Queue capacity 25–50 is applied only after the 1,500 cap. Filtering by ID can change the scanned population, but this is not a complete manager discovery workflow.

## Privacy, identifiers and Git

IDs are masked in the selection label, passport and queue using the last three digits. There are only **1,000 distinct displayed suffixes for 50,000 customers**; every customer shares a suffix with another. The same alias is recorded in session audit entries, making case attribution ambiguous. Preserve a separate internal unique case/customer key and show a stable collision-resistant display alias in a later phase. The search field echoes typed raw IDs, so there is no enforced screen-sharing/presentation mode. Free-text staff reasons can also expose identifiers entered by the user.

Git now exists with two reachable commits (`01b2729`, `6f07047`); the README's “no Git repository” statement is stale. Current tracked paths and all reachable Git object paths contain **no CSV, ZIP, outputs, environment, database or `.aws` paths**. Ignore rules cover these local artifacts. The limited tracked-text secret-pattern scan found no embedded access-key/private-key/password patterns. These checks do not certify absence of every possible secret or sensitive string.

The submission DOCX and PDF are tracked. DOCX XML text had no exact customer-ID token matches. Best-effort PDF text-stream inspection likewise found no exact matches; an initial raw-stream match was in binary font data and was excluded as a coincidence. PDF encoded/rendered content was not exhaustively reviewed. Review both documents before external distribution; no history rewrite or document alteration was performed in this audit.

There is no authentication, staff authorization, encrypted local storage, durable audit, retention control or access audit. Local filesystem artifacts remain sensitive even when ignored by Git. The fresh audit reports publish aggregate counts only and do not include customer identifiers. No banking API, outreach, underwriting approval or fabricated competition record was introduced.

## Evidence and next safeguards

Local evidence is under `outputs/phase1_audit/`: `data_checks.json`, `rebuild/data_audit.json`, `rebuild_comparison.json`, `preservation.json`, `edge_probes.json`, `queue_checks.json`, `repository_checks.json`. The scripts there are audit-only helpers; they are not new production modules or added pytest tests.

Prioritize fail-closed feature validation and holdings parsing, verified cutoff/provenance, typed gate inputs and a complete supported-case queue. Then add durable internal identity, reviewer attribution, evidence replay and historical evaluation as specified in [the roadmap](IMPLEMENTATION_ROADMAP.md). Preserve the 17-column CSV contract unless a versioned, justified migration is approved.
