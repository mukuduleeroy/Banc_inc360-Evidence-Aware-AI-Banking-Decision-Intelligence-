# Reproducible live-demo runbook

**Planning only.** No launch, preparation write, review, upload, activation or reset in this runbook was executed during Phase 11. Clear the manual gates in 10 first. Future rehearsals must use fresh disposable state; never reuse accepted databases or registries. Commands below were checked against current code, installed Streamlit 1.50.0 and previously successful browser launch recipes; current port availability/startup was not tested here.

## Prerequisites and read-only preflight

Repository actually exists at `/Users/user/Documents/BancInc360_Final`; the old Downloads repository path does not. Existing `.venv`: Python **3.9.6**, Streamlit **1.50.0**, pandas **2.3.3**, NumPy **2.0.2**, PyArrow **21.0.0**, pytest **8.4.2** verified from metadata. Application pins are in `requirements-lock.txt`. Offline evaluation dependencies are in `requirements-evaluation-lock.txt`; no fitting/dependency install is needed to show the JSON-driven historical panel.

Required private local inputs: canonical `outputs/customer_features.csv`, adjacent manifest, existing `outputs/.presentation_alias_key`, trusted historical `outputs/phase5/evaluation/evaluation.json`, frozen reference and accepted receipts. Required wholly synthetic upload examples already exist in `outputs/phase9/examples/`. No credential/key value belongs on the command line or projector.

Before an authorized rehearsal, read-only checks:

```bash
cd /Users/user/Documents/BancInc360_Final
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -c 'from phase10b_value import load_accepted_index,value_reconciliation; i=load_accepted_index(); print(len(i.records), i.counts); print(value_reconciliation(i)["existing_higher_activity_band"])'
lsof -nP -iTCP:8514 -sTCP:LISTEN
lsof -nP -iTCP:8511 -sTCP:LISTEN
lsof -nP -iTCP:8515 -sTCP:LISTEN
```

Expected counts: 50,000; 2,052/20/47,928; 10,003. This data check does **not** clear the `docs/.DS_Store` checkpoint exception or constitute a fresh test pass. Empty lsof output normally means no listener; permission/other errors are not proof of an unused port. If a port is occupied, select an unused explicit alternative and update the matching launch/URL; do not kill another process.

No installation is performed in Phase 11. If the existing environment is missing, defer to authorized setup in a new environment/copy using pinned requirements; do not upgrade the frozen `.venv`, retrain models or install dependencies live during the pitch. README contains older counts/startup guidance; this runbook uses the current verified entrypoints.

## Exact future startup — one terminal, three owned processes

This block deliberately creates **new temporary rehearsal state/logs**, outside the protected tree. It is for a separately authorized rehearsal/presentation only, not Phase 11 execution. Keep the terminal open so its PID variables remain available. Choose free ports first.

```bash
cd /Users/user/Documents/BancInc360_Final
BANCINC_DEMO_ROOT="$(mktemp -d /private/tmp/bancinc-phase11-demo.XXXXXX)"
export BANCINC_DEMO_ROOT
printf '%s\n' "$BANCINC_DEMO_ROOT"

PYTHONDONTWRITEBYTECODE=1 DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
BANCINC_FEATURES_PATH=outputs/customer_features.csv \
BANCINC_AUDIT_DB="$BANCINC_DEMO_ROOT/original-review.sqlite3" \
.venv/bin/python -m streamlit run app.py \
  --server.address 127.0.0.1 --server.port 8514 \
  --server.headless true --browser.gatherUsageStats false \
  > "$BANCINC_DEMO_ROOT/main.log" 2>&1 &
BANCINC_MAIN_PID=$!

PYTHONDONTWRITEBYTECODE=1 DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
BANCINC_PHASE9_STORAGE="$BANCINC_DEMO_ROOT/ingestion" \
.venv/bin/python -m streamlit run phase9_app.py \
  --server.address 127.0.0.1 --server.port 8511 \
  --server.maxUploadSize 5 \
  --server.headless true --browser.gatherUsageStats false \
  > "$BANCINC_DEMO_ROOT/ingestion.log" 2>&1 &
BANCINC_INGESTION_PID=$!

PYTHONDONTWRITEBYTECODE=1 BANCINC_RUNTIME=LOCAL \
.venv/bin/python -m streamlit run phase10b_app.py \
  --server.address 127.0.0.1 --server.port 8515 \
  --server.headless true --browser.gatherUsageStats false \
  > "$BANCINC_DEMO_ROOT/business.log" 2>&1 &
BANCINC_BUSINESS_PID=$!
```

Expected URLs **if those selected ports are free and startup succeeds**:

- Original: `http://127.0.0.1:8514`
- Ingestion: `http://127.0.0.1:8511`
- Business companion: `http://127.0.0.1:8515`

Bind loopback only. The Phase 9 server cap **5 MiB** is mandatory; the app refuses uploads without it. Do not omit its storage override: default storage is inside existing outputs and must not be used for this rehearsal. Phase 10B has no write store. Three tabs are separate applications, not a single switching workspace. Environment variables override Streamlit secrets by `deployment_data.setting`; explicit LOCAL/canonical path prevent unintended inherited data selection.

Verify each page is fully rendered and counts reconcile before starting the clock. Health alone is not proof of completed UI render. There is no startup-duration guarantee. Do not proceed on source/hash errors, missing evidence or unresolved authorization.

## Safe, already-existing case anchors

Read from existing `outputs/phase9/original_app_browser/demo/demo.json` and independently checked through the current index, not invented:

| Purpose | Presentation alias / existing synthetic reference | Expected result |
|---|---|---|
| Original supported case | `C-4620B382895C1E428483A2FF` | SUPPORTED, six gates; Savings discussion only |
| Optional borderline case | `C-999D124405DED97E57819E62` | CAUTION; no local Approve |
| Optional withheld case | `C-546C667C281C61AC638FD044` | ABSTAIN; no sales permission |
| Phase 10B eligible upgrade | DEMO-UP-001 / “Eligible hypothetical upgrade” | DEMO_ELIGIBLE_FOR_REVIEW |
| Phase 10B restriction | DEMO-UP-004 / “Restricted synthetic customer” | DEMO_NOT_ELIGIBLE |
| Phase 9 CSV | `outputs/phase9/examples/synthetic-valid.csv` | Four synthetic customers; 1 SUPPORTED / 1 CAUTION / 2 ABSTAIN |

Aliases are pseudonyms, not proof of anonymization or public data-release permission. Only show customer evidence to an authorized audience; do not copy financial values/raw customer IDs/emails/student numbers into public artifacts. Keep only alias/rating anchors in this local runbook. Do not generate a new key to force an alias match.

## Preparation outside the 15-minute clock

Planned writes below are allowed **only in the new disposable stores during an authorized rehearsal**, not protected histories and not during this documentation phase.

1. Original → data source **BancABC historical extract**, analytics outcome **ALL**, cases/page **25**. Sidebar Find customer alias → paste supported anchor → explicitly select it. Product context **Supported staff review**, banking segment **All**. Verify known other holdings, Savings gap, rationale and actual G4/G5.
2. Manager Work Queue → lane SUPPORTED, local status ALL, empty queue alias filter, selected Passport supported anchor. Select **DEMO-RM-01** (unverified demo label), click **Open case and inspect Passport** once. Leave case OPEN for the timed local review. Do not use the separate session-only Record decision button.
3. Phase 9 → date **2026-07-01**, upload existing synthetic-valid.csv, **Validate upload** → **Process validated dataset** → **Preview candidate snapshot**. Expect 14 source/accepted rows, four customers/accounts, zero exclusions, 1/1/2, coverage 100%. Leave candidate preview selected but **active selection baseline**, ready to demonstrate explicit activation/rollback. This creates only a disposable candidate outside the accepted tree.
4. Phase 10B → Upselling Intelligence → Eligible hypothetical upgrade; preload High-Value page once to warm reads, then return to eligible scenario.
5. Original → Executive Overview, supported global anchor retained. Open separate local receipt/report tab for latest 647 tests; the embedded Audit list still reads older phase files and displays latest listed 308.

If preparation cannot be completed safely, use the recorded-evidence/storyboard fallback and disclose the limitation; do not fake prevalidated state.

## Timed navigation and speaking cues

| Pitch interval / action | Exact settings/navigation | Expected verified output | Speaking cue | Planned action time | Fallback |
|---|---|---|---|---:|---|
| 0–2 opening | Original Executive tab | 50,000 / 2,052 / 20 / 47,928 | Permissions, not sales/churn | 10–15s gesture | Static aggregate/method text; label recorded |
| 2:00 customer | Customer 360; supported global anchor | Same alias; historical/current sections, source segment, Passport link | Snapshot dates unknown | 20–25s | Skip numeric row details, explain sections |
| 2:40 inactivity | Inactivity; segment All; >90 days; 4+ events; outcome ALL | Honest filtered subset; original global selection need not belong to it | Observed recency, not probability | 20–25s | Existing chart/aggregate count 26,734, no invented case |
| 3:45 relationship | Relationship; Higher activity (80th+); optional SME | Existing global percentile, no rerank | Activity not profit | 20–25s | Show Phase 10B method/threshold text |
| 5:00 cross-sell | Reset global supported alias; Product; All; Supported staff review | Known other holdings + Savings absent + rationale/G4-G5 | Prototype additional-product discussion | 20–25s | Read existing product explanation/recorded evidence |
| 5:50 Passport | Decision Passport for supported anchor | Six actual gate cards/reasons, staff review only | G1–G6 authority | 20–30s | Architecture gate table; do not invent a pass |
| 8:00 replay | Evidence Replay; KYC Pending; **Reset simulation** | Baseline SUPPORTED → SIMULATED ABSTAIN → SUPPORTED | Copy only, no real action | 25–30s | Existing replay receipt; say recorded |
| 8:40 review | Queue, same supported case; select DEMO-RM-01; action Approve; reason + acknowledgment; **Save durable review** once | APPROVED_LOCAL, not bank approval | Human evidence review, local only | 35–40s | Existing persisted timeline receipt; no new-save claim |
| 9:35 audit | Audit → durable case/timeline | OPEN and APPROVE for fresh prepared case, snapshots/provenance | Append-only local application history | 15–20s | Prior restart receipt, no new restart claim |
| 10:00 ingestion | Candidate already previewed; Activate validated preview snapshot; Return to accepted baseline | Companion active candidate then baseline; main app unchanged | Isolated reversible selection | 20–25s | Existing synthetic acceptance receipt; no activation claim today |
| 10:30 upsell | Business tab; eligible then Restricted synthetic customer | DEMO eligible then not eligible | Hypothetical tier upgrade only | 20–25s | Existing wholly synthetic screenshots |
| 11:20 value | High-Value page; All/high-only; inspect first visible alias | 10,003, >=.8, window/segment/explanation | Potential value review, no profit | 15–20s | Existing method/aggregate only; no private screenshot publication |
| 12:00 AI | Original Inactivity/Audit historical panel | Recency/LR/HGB verified metrics, cohorts and unavailable inference | Historical experiment, not live prediction | 20–25s | Exact verified historical table in 06, marked recorded |
| 13:15 technical | Separate latest receipt and 01 freeze report | Historical 647; metadata exception disclosed | Verified source, not fresh pytest pass | 15–20s | Local text reports, no internet needed |
| 14:00 closing | Stop navigation | Summary, no financial-return figure | Evidence → permission → accountable human decision | 0s extra | Spoken closing |

These are rehearsal targets, not measured timings. Do not click a filtered table's customer selector accidentally and pretend it is the original case. Explicitly restore the supported anchor before Product/Passport/Replay/Review. Never read an arbitrary confidential amount aloud. Use a stage manager's absolute time checkpoints in 03.

## Exact disposable review form

Action **Approve** is available only on currently SUPPORTED. Required reason:

“Controlled local demonstration review; current Passport inspected; no bank authorization or outreach.”

Tick the actual acknowledgment that the current six-gate Passport was inspected and this is not authenticated bank approval. Save once. Expected fresh prepared case has two events OPEN→APPROVE and APPROVED_LOCAL; another state/history means preparation differs—inspect it, do not erase it or claim a new result. Non-supported cases expose Defer/Reject only.

## Extended demo after the clock (optional, authorized)

Phase 9 fresh upload sequence takes additional time: validate synthetic CSV → process → reconcile → preview → activate → rollback → invalid-date CSV validation failure, with processing/activation disabled for invalid upload. Do not promise arbitrary schemas, FX conversion or all-nine-view refresh. UI cap is 5 MiB/25,000 rows, preview 50 aliases; date 2026-07-01. Use **Discard staged upload** for the disposable staging token only.

## Reset, recovery and shutdown

- Replay: **Reset simulation** only, preserving source and real history.
- Phase 9: **Return to accepted baseline** resets selection, not deletion of candidates/history. Preserve the disposable directory.
- Phase 10B: select the eligible synthetic scenario and All/high-only source filters; no persistent store to reset.
- Original selection: explicitly reselect supported anchor. Do not reset/migrate a protected DB or use scripts/presentation.py reset against an accepted generation.
- Fresh-run requirement: stop owned processes, create a new mktemp root on the next authorized rehearsal; do not delete previous evidence to “clean” the demo.

In the same shell that launched the three apps, while its recorded PIDs still refer to these live processes:

```bash
kill -TERM "$BANCINC_BUSINESS_PID"
kill -TERM "$BANCINC_INGESTION_PID"
kill -TERM "$BANCINC_MAIN_PID"
```

If launched in separate terminals, Ctrl-C in each respective terminal. Never use broad pkill/killall or terminate unknown listeners. Preserve logs and new state privately, verify original data digest if needed, and do not publish that directory. Phase 11 did not create these processes or state directories.
