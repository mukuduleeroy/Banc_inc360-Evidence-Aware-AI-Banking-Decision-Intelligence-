# Controlled source dataset contract

Contract: `phase9-transactions-usd-v1`. This supports a bounded compatible transaction CSV, not arbitrary banking extracts, customer-feature uploads, ZIP uploads or spreadsheets.

## Transport and limits

- UTF-8 (optional UTF-8 BOM), comma-separated CSV with one unique header row; no duplicate/unknown columns.
- Plain `.csv` filename, at most 120 characters, no directory separators/control characters. It is display metadata only; storage names are generated tokens.
- Maximum **5 MiB**, **25,000 data rows**, **2,048 characters per field**, finite absolute USD amount at most **1,000,000,000,000**. Row/amount limits are explicit local ingestion safeguards, not bank policy thresholds.
- The companion must launch with `--server.maxUploadSize 5`; it refuses to render upload controls with a larger cap. Staging reads 64 KiB blocks and independently enforces byte limits. CSV processing stops at the row limit; malformed/oversized files cannot activate.
- Explicit valid timezone-naive observation date, exactly `YYYY-MM-DD`. No inferred/default historical date is used in processing; the UI proposes the documented synthetic scenario date for confirmation.

## Required source fields

| Field | Contract / existing semantics |
|---|---|
| `Customer ID` | Existing identifier syntax; valid repeated values across transactions |
| `Account ID` | Existing identifier syntax; one owner per source account |
| `account_customer_id` | Existing identifier syntax; must equal Customer ID |
| `Transaction ID` | Existing identifier syntax; exact repeated records reported/deduplicated, conflicting reuse rejected |
| `transaction_date` | Existing mixed/day-first date parsing; timezone-naive valid timestamp; prefer `DD/MM/YYYY` to avoid ambiguity |
| `Type` | Existing type labels, case-insensitive exactly as the builder handles them; see below |
| `Amount (USD)` | Already-normalized finite USD amount; no exchange-rate inference or conversion |
| `dr_cr_indicator` | `DR` or `CR`; preserved input, not a new signed-volume formula |
| `products_held` | Pipe-separated existing product catalogue labels; blank remains unknown, never imputed as empty holdings |
| `customer_status` | Existing customer-state vocabulary; unknown/blank permitted only as unknown evidence leading to abstention |
| `account_status` | Existing account-state vocabulary; same unknown handling |
| `kyc_status` | Existing KYC-state vocabulary; same unknown handling, never invented as Verified |
| `service_reasons` | Bounded source text; existing service-issue detection; not exposed in preview/logs |
| `customer_segment` | Existing Retail, SME, Corporate, NGO/NPO or Trust meaning; blank becomes presentation Unknown; never an inferred predictor or eligibility rule |

Optional **`Currency`**: every value must be exactly `USD`. Without this optional column, `Amount (USD)` explicitly declares the normalized input unit. This does not independently verify an upstream FX conversion. All other currencies are rejected; the pipeline is not an FX converter. No rates are fabricated.

Types: CASH_DEPOSIT, POS_PURCHASE, ATM_WITHDRAWAL, BILL_PAYMENT, FOREX_PURCHASE and SERVICE FEE. Known non-fee finite-amount events are qualifying. FOREX_PURCHASE still requires its already-normalized Amount (USD); its label does not authorize arbitrary currency input.

Customer states: Active, Dormant, Restricted, Closed, Frozen. Account states additionally include their existing vocabulary Active, Frozen, Dormant, Closed, Restricted. KYC: Verified, Pending, Review Due, Unverified, Expired, Rejected. Existing whitespace/case normalization is reused for states. Missing schema columns always fail even when a blank field value is an explicitly supported unknown.

Known product labels come from `evidence.PRODUCT_LABELS`; no new product terms or policies are introduced. A nonblank malformed/unknown product list fails admission. Blank ownership is explicitly warned and produces existing G5 abstention. Formula-like service/segment text is rejected; source text is never executed.

## Relationships, temporal scope and duplicates

Multiple rows per customer/account are normal. Exact duplicate transaction records are allowed, reported and handled by the unchanged builder. A transaction ID reused with differing evidence is rejected. Ownership mismatches or an account attributed to multiple customers are rejected, rather than silently quarantined on activation.

Every uploaded customer must have a transaction strictly before the observation date. Post-cutoff-only customers are rejected to avoid missing decisions. Later records for an existing historical customer may be accepted with a warning: they do not enter historical predictors, while current snapshot fields follow existing builder semantics. Current snapshot effective dates remain unknown; source KYC/holdings/segment do not reconstruct historical eligibility.

The adapter rejects invalid identifier/date/type/amount/linkage records before calling the builder. The builder's original quarantine/exclusion logic remains unchanged and is rechecked afterward: any unexpected invalid/excluded records or reconciliation discrepancy blocks candidate registration. Exact duplicates are accounted for separately, not described as invalid customers.

## Unchanged output feature contract

The user clarified that the actual accepted **16 columns** are authoritative. Preserve this exact header/order and the existing builder/index types and semantics:

```text
customer_id,qualifying_events_180d,events_90d,recency_days,transaction_volume_180d_usd,deposit_events_180d,product_gap,behavioural_reason,products_held,customer_status,account_status,kyc_status,service_issue,customer_segment,account_count,relationship_activity_percentile
```

No seventeenth column is added. Counts, recency, rounded USD volume, booleans, serialized ownership, source metadata and globally ranked percentile are generated by the original builder and loaded by the original index adapter. Observation windows remain 180/90 days with exclusive cutoff, and the existing event definition and policy remain unchanged. Earlier 17-column descriptions are historical documentation errors; original Phase 8B reports are preserved.

The source contract is compatibility, not certification of the supplier's data-use rights, real-world accuracy, current eligibility or currency-normalization provenance. The operator must supply authorized data; demonstration uses independently fabricated records only.
