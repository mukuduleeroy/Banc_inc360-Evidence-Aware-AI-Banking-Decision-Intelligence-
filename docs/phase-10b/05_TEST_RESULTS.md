# Phase 10B actual test and demonstration results

## Full acceptance — PASS

**647 collected / 647 passed / 0 failures / 0 errors / 0 skipped.** Pytest duration **104.31 seconds**. No pytest warnings summary was emitted. All **574** accepted Phase 9 test IDs were retained, plus **73** new cases; the original **96 gate-combination cases** passed. Original nine-view navigation, Passport/replay/reset, review persistence, ingestion and historical evaluation tests all remain in the executed full suite.

Exact full command:

```bash
BANCINC_AUDIT_DB=/private/tmp/bancinc-phase10b-full-regression.sqlite3 \
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python phase10b_acceptance.py \
  --out-dir outputs/final_acceptance/phase-10b-final
```

The new additive runner calls the unchanged Phase 9 acceptance runner, which calls the unchanged original full regression workflow. It then additionally verifies the hash-pinned 574-case inventory, all 87 accepted source bytes, every checkpoint-protected artifact/state file, original canonical decisions and both separate population reconciliations. No test or frozen result was edited to secure a pass.

Fresh receipts under `outputs/final_acceptance/phase-10b-final/`: `test_execution.log`, `tests.xml`, `run_manifest.json`, `acceptance.json`, `phase9_acceptance.json`, `phase10b_acceptance.json`. Full stdout: `outputs/phase10b/full_acceptance.log`.

JUnit SHA-256: `ee2297d3b34355eff70c8694190d3a49ce5a2b4ba09a6cca3cb2c33359a332bb`.
Prior accepted JUnit SHA-256: `9cf3d25aa2705b651864b1cb34511e5d8fd73e3260cb0e9651e512ed8212cff8`.
Run started `2026-11-20T08:41:50.945109+00:00`, finished `2026-11-20T08:43:36.756491+00:00`. The before/after/current source snapshots match across **96** covered Python/test/config/asset files; the exact JUnit matches the completed run manifest. The JavaScript browser helper is separately bound in the final new-file preservation receipt.

## New tests and targeted results

| New module | Cases | Required coverage |
|---|---:|---|
| `tests/test_phase10b_upsell.py` | 43 | Valid same-family higher tier; same-product/downgrade/family/spec/assumption rejection; target already held; unknown/absent ownership; missing/insufficient history/need/status; restrictions; human/no-outreach controls; synthetic scope; failed-over-missing precedence; no call to operational G5/engine |
| `tests/test_phase10b_value.py` | 17 | Existing >=.8 boundary; missing/invalid evidence/cutoff; original columns/rank/band/order/digest invariance; window/segment/breadth/denominator explanations; source reconciliation; alias safety; canonical 16-column contract |
| `tests/test_phase10b_ui.py` | 9 | Four views; synthetic eligible/withheld outcomes; separate denominators; source segment filters/global metrics/pagination reset/empty state; source-integrity failure without fallback; local-only guard; no action controls |
| `tests/test_phase10b_isolation.py` | 4 | All 87 source hashes/protected state; exact decisions/priorities/reasons/aliases; full prior 574 inventory; no registry/review/storage/network/live-model runtime dependency |

Targeted commands used `.venv/bin/python -m pytest` with isolated review storage:

- `tests/test_phase10b_upsell.py tests/test_phase10b_value.py -q -ra`: **60 passed in 10.26s** (`outputs/phase10b/targeted_tests.log`).
- All four `tests/test_phase10b_*.py` modules with `-q -ra`: **73 passed in 28.84s** (`outputs/phase10b/focused_tests.log`).

No failing test run or unresolved regression was recorded. Before final tests, ownership explanation was explicitly made unavailable when not established, and the installed Streamlit/native controls were used without new dependencies. The original full suite's isolated synthetic estimator reproducibility fixture ran as before; no real-data model fitting or historical artifact change occurred.

## Actual local browser demonstration — PASS

```bash
DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL \
.venv/bin/python scripts/accept_phase10b.py \
  --out outputs/phase10b/browser --main-port 8514 \
  --port 8515 --cdp-port 9232
```

Verified sequence: accepted original Savings cross-sell with known holdings/gap/disclaimer → separate companion → eligible hypothetical Standard→Premium upgrade → restriction/missing/unknown-ownership withholding → real source-derived high-activity classification and segment context → original Executive baseline 50,000 / 2,052 / 20 / 47,928. Source digest before and after matched.

All four companion views passed at **1440, 768 and 390** widths: **12 view/viewport checks**, no application exceptions/document overflow/clipped metric values and no approval/save/outreach controls. Browser/server traffic was loopback only. Screenshot artifacts are private viewport samples, not formal accessibility certification or public customer-data artifacts.

Receipts: `outputs/phase10b/browser/{acceptance.json,browser_result.json,browser.log,servers.log}` plus screenshots. The runner used a new isolated original-review path and temporary Chrome profile; both servers/browser stopped after the check. Original all-nine native view behavior was also re-exercised in the full automated suite; the browser demonstration visited the two original views relevant to this walkthrough rather than claiming a new all-nine browser pass.
