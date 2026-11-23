# Phase 10B local demonstration guide

No bank-approved upgrade is available in the real feature data. This demonstration explicitly separates the existing operational Savings cross-sell, independent hypothetical upsell fixtures, source-derived activity proxy and existing offline AI evidence.

## Launch two separate local interfaces

From the repository, in the first terminal (choose an unused port and fresh audit filename):

```bash
cd /Users/user/Documents/BancInc360_Final
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
BANCINC_AUDIT_DB=outputs/phase10b/original-demo-new.sqlite3 \
.venv/bin/python -m streamlit run app.py \
  --server.address 127.0.0.1 --server.port 8514 \
  --server.headless true --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8514`. Do not reuse an accepted audit database for rehearsal writes.

Second terminal:

```bash
cd /Users/user/Documents/BancInc360_Final
BANCINC_RUNTIME=LOCAL .venv/bin/python -m streamlit run phase10b_app.py \
  --server.address 127.0.0.1 --server.port 8515 \
  --server.headless true --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8515`. It has no upload, storage, review-save or banking-action endpoint; no new secret/database configuration is required. It uses the existing local canonical dataset and existing key read-only. Missing/mismatched evidence produces an error, never synthetic substitution for real analytics. Stop each server with Ctrl-C in its own terminal.

## Reproducible walkthrough

1. In the original app, show Executive counts 50,000 / 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN.
2. Product Opportunity → supported review case → show known other products, recorded Savings gap, deposit rationale and G4/G5. This is the existing cross-sell, not an upsell.
3. Open Business Capability Companion → Overview. Explain the distinct original versus synthetic populations/statuses. Synthetic counts are not added to original totals.
4. Upselling Intelligence → **Eligible hypothetical upgrade**. Show independent DEMO-UP-001, known synthetic **Hypothetical Standard Account Package** and **Hypothetical Premium Account Package**.
5. Explain same-family tier 1 → tier 2 relationship; synthetic evidence: eight qualifying events and three expanded-service requests in the preceding 180 days; illustrative Active/Verified checks; human review required.
6. Show all PASS checks and **DEMO_ELIGIBLE_FOR_REVIEW**. State that this is not an existing Savings G5 decision, bank-approved offer, validated real-customer opportunity or authority to contact anyone.
7. Select **Restricted synthetic customer**: DEMO_NOT_ELIGIBLE and the restriction check. Then **Missing activity evidence**, **Unverified source ownership** or **Insufficient historical activity**: no positive result; missing evidence is explained and ownership is not invented.
8. Optionally show **Already holds hypothetical target** and **Invalid same-tier product relationship**: both excluded.
9. High-Value Customer Intelligence → global source population 50,000 and **10,003 High Relationship Activity**. The original band/percentile is reused, not recalculated.
10. Inspect a source-derived alias: original Higher activity band, global percentile >=0.8, absolute qualifying 180-day USD activity, current breadth/account context, window [2026-01-02, 2026-07-01), source/policy hashes.
11. Filter SME/Corporate/another source segment and explain that percentile/global denominator stay fixed; there is no segment-relative profitability score. Unknown segment can honestly be empty.
12. Read the exact limitation: higher historical activity does not establish profitability, LTV or future revenue. No actual customer row belongs in public reports/screenshots without data-use permission.
13. Evidence and Methodology → hypothetical product/provenance, separate namespace, exact proxy rule and non-production limits. Existing historical AI remains offline; no new model was trained or deployed.
14. Return to the original app and confirm unchanged population/permissions. Existing queue, Passport and Replay remain available; no companion action modifies them.

The real source has no approved upgrade contract. All hypothetical product ownership/need/status records are independently invented code fixtures and are never matched to real aliases. This closes the demonstrable **illustrative** upsell/proxy gap; it does not make real BancABC upselling operational or prove commercial value.

## Verification commands

Read-only baseline check through the companion's strict loader:

```bash
.venv/bin/python -c 'from phase10b_value import load_accepted_index; i=load_accepted_index(); print(len(i.records), i.counts)'
```

Fresh complete regression (choose a new output directory and isolated audit filename):

```bash
BANCINC_AUDIT_DB=/private/tmp/bancinc-phase10b-rerun-new.sqlite3 \
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python phase10b_acceptance.py \
  --out-dir outputs/final_acceptance/phase-10b-rerun-new
```

Full local browser rehearsal is in `scripts/accept_phase10b.py`; use an unused output folder and ports. It launches/stops its own main/companion servers and temporary Chrome profile. Private artifacts remain under outputs. Follow 05/08 for actual completed results, not an assumed pass. No public deployment, customer contact, product purchase or remote push is part of the demonstration.
