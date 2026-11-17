# Phase 3 — presentation walkthrough and local runbook

Prepared November 16, 2026 (Africa/Harare) for the November 20 presentation. Demonstrate the current verified prototype and its limitations, not production banking authority.

## Start and preflight

Use the existing environment and entry point:

```sh
.venv/bin/python -m pip check --disable-pip-version-check
.venv/bin/python -m pytest -v -ra
.venv/bin/python scripts/report_phase3_metrics.py
.venv/bin/python scripts/verify_ui.py
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

Default URL is http://127.0.0.1:8501. A separately verified Phase 3 preview is running at **http://127.0.0.1:8502**; the prior port-8501 session was not reset. To choose a different free port, add `--server.port 8502` (or another free port). Stop only the instance you started with Ctrl-C.

Real-data mode requires the authorized `outputs/customer_features.csv` and adjacent `.manifest.json`. An alternate input uses exported `BANCINC_FEATURES_PATH`; `.env` is not automatically loaded. Preserve private `outputs/.presentation_alias_key` for stable aliases. Never copy datasets, the key or review-note contents into public Git or a public presentation archive.

The theme/branding load from `.streamlit/config.toml` and `assets/brand.svg`. No frontend build, new package or internet service is needed. If the source is missing, the app explicitly offers synthetic mode; do not present that mode as real-data analysis. A malformed feature schema shows the validation code and withholds the real workspace.

## Suggested demonstration journey

1. **Executive Overview.** Confirm the source indicator and July 1 cutoff. Read the actual counts: 50,000 evaluated; 2,052 SUPPORTED; 20 CAUTION; 47,928 ABSTAIN. Explain that SUPPORTED permits staff review, not a banking approval. Point out typed-data quality, historical engagement, observed activity segments and overlapping non-pass reasons.
2. **Customer 360.** Use the privacy-safe alias selector/search. The same selection follows navigation. Show historical activity separately from current status/KYC/holdings. Identify the unknown snapshot effective date and explain the savings rationale without calling deposits salary.
3. **Inactivity Intelligence.** Explain whole-day recency and the exact cutoff/lookbacks. Show 26,734 customers with observed recency over 90 days and the event-coverage distribution. State clearly that these are observations, not trained future inactivity predictions.
4. **Relationship Value Intelligence.** Show the documented absolute-volume percentile proxy and product breadth. Use a segment filter and customer drilldown. Explain why this is not revenue, profitability or lifetime value; current breadth is not historical evidence.
5. **Product Opportunity Intelligence.** Show 40,000 recorded savings gaps, 12,517 gaps with rationale and only 2,052 engine-supported review cases. Switch to already-held suppression to show that ownership does not become a new opportunity. A gap is not verified suitability.
6. **Decision Passport.** Open the selected case and inspect the actual G1–G6 outcomes, reason codes, method/policy and fingerprints. Explain required staff checks and why no model is approved. A deliberate reason can be recorded as a session note; do not call that authenticated bank approval.
7. **Evidence Replay.** Start with a real supported case. Confirm baseline and simulated outcome both SUPPORTED with no overrides. Select **SIMULATED KYC status → Pending**: G4 changes and the simulated result becomes ABSTAIN. Reset returns the original SUPPORTED baseline. Optionally simulate Frozen status or an already-held Savings Account. The page is a labeled counterfactual, not source-transaction reconstruction, and has no action/note submission path.
8. **Manager Work Queue.** Show a nonempty SUPPORTED page and move to page two. The complete index includes every evaluated customer before paging. Open a queue case's passport; demonstrate separate CAUTION/ABSTAIN investigation lanes and an empty alias filter. Review notes remain session-only and cannot trigger outreach.
9. **Audit & Validation Evidence.** Show source/build reconciliation and parsed test artifact counts. The final recorded suite is 182 passing tests, with all 124 Phase 2 cases retained. Read the artifact/timestamp rather than assuming future runs pass. State the remaining snapshot, authentication, persistence and model-evaluation limits.

The analytics outcome filter has a declared scope: charts/tables, not executive population KPIs or implicit permission changes. Alias search is a workspace selector, not a banking identifier entry field. Clear filters before the next demonstration step if the context would otherwise be confusing.

## Verified simulation and reset

The actual browser run established: **real baseline SUPPORTED → SIMULATED Pending KYC ABSTAIN → Reset SUPPORTED**. The canonical file, complete decision index and real session notes remain unchanged. Even a simulated SUPPORTED output is explicitly non-actionable. Unsupported override fields such as identity, lineage, model approval and outreach controls are rejected.

Simulated event totals do not fabricate underlying transactions or silently rewrite subordinate counts. If the new total conflicts with unchanged 90-day/deposit evidence, validation may also withhold through G1. This is an evidence-quality explanation, not a reason to loosen the gates.

## Browser checks and screenshots

Local headless Chrome plus Node's built-in CDP support produced actual desktop screenshots for all nine views and a 768-pixel overview. The narrow layout has no clipped KPI values or document-wide horizontal overflow after native card wrapping. These checks do not certify every phone size, keyboard path or assistive technology.

To reproduce browser checks, start the app on port 8502 and use a fresh isolated Chrome profile:

```sh
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' --headless=new --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir=/private/tmp/bancinc-phase3-chrome --no-first-run --no-default-browser-check --disable-background-networking --disable-component-update --disable-sync about:blank
```

In another terminal:

```sh
node scripts/verify_browser.mjs
```

Keep debugging bound to localhost. Close the test Chrome process afterward; do not expose its port externally. Screenshots are viewport-only and live under ignored `outputs/phase3/screenshots/`. See [UI validation](PHASE_3_UI_VALIDATION.md) for links. Share only reviewed masked evidence; do not distribute local customer files or notes.

## Known limits to say aloud

- The extract is competition evidence, not a live banking connection. Current snapshot effective dates are unknown.
- Activity proxies and cash-deposit rationale do not establish profitability, salary, future behavior or suitability.
- No trained operational model or reproduced historical evaluation exists. Do not quote concept-paper figures as fresh measurements.
- Replay is controlled simulation, not immutable transaction-level evidence replay.
- Notes are session-only and reviewer identity is not authenticated. No real offer, communication, lending or insurance approval is executed.

## Recommended Phase 4

Prioritize durable SQLite-backed case/passport/review records, unique case IDs, reviewer attribution and explicit authorization boundaries, with persistence/write-failure/concurrency tests. Then add transaction-level evidence references and temporal replay tied to a source/build version. Treat snapshot freshness, access/retention policy and authenticated identity as explicit design work before operational use. Keep the current rules authoritative until any future method earns documented approval; do not add ML simply for presentation effect.
