# Phase 8B demonstration readiness

**GO for a controlled local demonstration.** Full acceptance: 504 passing tests, all 443 baseline cases retained, all 50,000 decisions unchanged. Public release and operational banking/model use remain outside authorization.

## Run locally

Use the existing repository and virtual environment. Preserve old audit databases; choose a fresh managed demo folder so rehearsal events cannot alter prior histories:

```bash
cd /Users/user/Documents/BancInc360_Final
.venv/bin/python scripts/presentation.py --help
```

The existing launcher supports managed presentation generations; its precise create/start/status commands remain documented in the repository README. For a direct isolated local preview:

```bash
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
BANCINC_AUDIT_DB=outputs/phase8b/presenter-new.sqlite3 \
.venv/bin/python -m streamlit run app.py \
  --server.address 127.0.0.1 --server.port 8510 \
  --server.headless true --browser.gatherUsageStats false
```

Use an available port and a fresh database filename; open `http://127.0.0.1:8510`. Stop that server with Ctrl-C. Do not stop or reuse another presentation's database. The approved canonical local dataset, manifest, alias key and historical JSON must already exist; missing/stale data is shown explicitly rather than substituted with demo data. A missing historical artifact withholds its metric panel without changing the application's data mode.

## Suggested walkthrough

1. Executive Overview: explain the real validated population and 2,052 / 20 / 47,928 decision distribution. SUPPORTED means staff-review eligibility only.
2. Customer 360: inspect the source-provided segment card, unknown effective date and historical/current-snapshot distinction.
3. Inactivity Intelligence: change banking segment and recency/history filters. Explain descriptive inactivity and the separate verified historical experimental comparison. Live fitted inference is unavailable.
4. Relationship Value: combine banking segment with Observed activity band. Percentiles remain global; volume/activity is not profitability or lifetime value.
5. Product Opportunity: show unfiltered population KPIs, a filtered subset and actual Savings G4/G5 evidence. If selection is outside the subset, explicitly choose a matching customer. Read the prototype discussion/no-contact disclaimer.
6. Decision Passport: inspect all six gate reasons, source/policy provenance and required human review. No segment or experimental score bypasses them.
7. Evidence Replay: simulate Pending KYC, observe ABSTAIN, then reset. Overrides do not edit canonical customer data or save review events.
8. Manager Work Queue: ranking is unchanged. Any permitted local demo review requires the existing reviewer/reason/acknowledgement workflow; APPROVED_LOCAL is not bank authorization.
9. Audit & Validation Evidence: distinguish historical evaluation from live model availability; inspect the local immutable review timeline and validation receipts.

## Evidence and limits

Final acceptance and detailed limitations are in 05; exact test commands/results are in 04. Browser verification used isolated local storage and actual server restart. Responsive screenshots cover nine views at 1440/768/390 widths in `outputs/phase8b/responsive`; private local screenshots/receipts must not be publicly distributed without data-use permission.

No model probabilities, new product terms, bank affiliation, real customer communications, cloud persistence or public real-data parity should be claimed. Retain this local demonstration boundary. Stop after Phase 8B.
