# Phase 10B feasibility and source evidence

Date: 2026-11-20 (Africa/Harare). Scope: strictly additive local companion; no accepted application source, report, data or persistent state changes.

The five required Phase 10A reports (01, 02, 03, 07, 08) and actual analytics/ownership/engine/ingestion interfaces were inspected before implementation. Phase 9 run manifest verified against current source: 87 files, prior 574-case JUnit bytes match; frozen 50,000 keyed decisions/priorities/reasons and policy match. All prior protection hashes match. Current source HEAD is recorded in `outputs/phase10b/checkpoint.json`; it differs from the old historical report HEAD but actual source bytes are accepted. Source-only rollback archive: `outputs/phase10b/rollback-source.zip`. The checkpoint additionally protects prior reports, all Phase 9 artifacts/registry/snapshots, current database/sidecars and original acceptance receipts.

## Product evidence finding

The 16-column feature contract exposes known product **types**, customer/account/KYC states, source segment, historical event/volume evidence, breadth/account context and global activity percentile. Ownership uses existing `evidence.holdings` and its fixed catalogue. No product tier, package level, upgrade relationship, package usage/upgrade demand, approved upgrade specification or bank upgrade eligibility exists. A holdings vocabulary is not an upgrade catalogue. Existing operational Savings logic remains unchanged.

Therefore **real source-backed BancABC upselling is not feasible with current approved evidence**. Attaching fictional tiers to accepted customer aliases would invent facts and is prohibited. The explicitly authorized safe alternative is a wholly synthetic, independent higher-tier package demonstration with a separate DEMO_* namespace, hypothetical products, synthetic evidence/checks and mandatory human review. It never evaluates the Savings G5 as upsell approval, never joins synthetic ownership onto real customers, and never writes operational review records.

Balances, fee income, margins, profitability and LTV are absent from the canonical 16-column contract. Additional raw snapshot fields mentioned by earlier historical source audits are not an approved economic-value calculation; this enhancement will not import or infer them. No profit/revenue estimate, product terms, pricing, rates or bank-policy claim is warranted.

## Safe independent analysis

Reuse unchanged `analytics.portfolio_frame`, `analytics.activity_band`, `analytics.numeric`, `segment_context.banking_segment_frame`/`filter_banking_segment`, and the accepted index loaded read-only with its existing key. The original Higher activity boundary is verified as **percentile >=0.8**. Original volume uses the absolute finite 180-day normalized USD sum; original percentile is the global average-tie rank rounded to four decimals. New proxy labels may explain those existing values but may not rerank/recompute them or change original band names.

Chosen source layout: new root `phase10b_upsell.py`, `phase10b_value.py`, `phase10b_app.py`, `phase10b_acceptance.py`, new tests/browser helpers and these reports. This keeps Python code within the existing acceptance source-snapshot coverage. No accepted navigation integration or implementation modification is needed. The companion has four views: overview, synthetic upselling, source-derived value proxy, evidence/methodology; the original nine views and Phase 9 companion remain unchanged.

**Feasibility: GO for isolated synthetic upselling and source-derived high-activity proxy only.** Real product-upgrade offers, bank-approved suitability, economic value and operational ML inference remain unavailable. This limitation is a deliberate evidence boundary, not a reason to weaken an existing gate.

## Original archive schema verification

The existing local original source ZIP was also inspected read-only: its SHA-256 matches the canonical manifest's source hash; it contains one CSV. Header inspection found `balance_after`, `account_current_balance`, `account_interest_rate_pct`, `estimated_monthly_income_usd` and card/account descriptors. Therefore it would be inaccurate to say the entire raw dataset lacks every balance/income field. They are **not** part of the accepted 16-column feature contract, are current snapshot evidence with unknown effective dates, and do not provide a validated profitability, bank fee-income/cost/margin/LTV calculation. This enhancement does not extract, infer or use them. No explicit approved tier/upgrade specification or eligibility relationship was found; names/descriptors alone cannot authorize a real upsell. Only source header labels and archive fingerprint were inspected; no identifying customer rows are included in this report.
