# Three-app startup verification

**Freshly executed locally, 2026-11-20. All three apps started and rendered.** This is local verification, not cloud deployment, projector certification or publication authorization.

Used Phase 11 runbook 04's existing `.venv` and exact entrypoints/configuration, with permitted free-port substitution: original 18514, ingestion 18511, business 18515. `lsof` found existing listeners on 8511/8515; they were not used or terminated. New ports 18514/18511/18515/19222 had no listeners at preflight. Fresh state root: `/private/tmp/bancinc-phase12-demo.5KHKEx` (mktemp-generated). No default accepted store was used.

## Commands actually used

Working directory `/Users/user/Documents/BancInc360_Final`. Each app used `PYTHONDONTWRITEBYTECODE=1` and redirected logs to the temporary root. Bash launched owned background processes and retained PIDs.

```bash
BANCINC_DEMO_ROOT="$(mktemp -d /private/tmp/bancinc-phase12-demo.XXXXXX)"
export BANCINC_DEMO_ROOT
PYTHONDONTWRITEBYTECODE=1 DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL BANCINC_FEATURES_PATH=outputs/customer_features.csv BANCINC_AUDIT_DB="$BANCINC_DEMO_ROOT/original-review.sqlite3" .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1   --server.port 18514 --server.headless true --browser.gatherUsageStats false

PYTHONDONTWRITEBYTECODE=1 DATA_MODE=LOCAL BANCINC_RUNTIME=LOCAL BANCINC_PHASE9_STORAGE="$BANCINC_DEMO_ROOT/ingestion" .venv/bin/python -m streamlit run phase9_app.py --server.address 127.0.0.1   --server.port 18511 --server.maxUploadSize 5 --server.headless true   --browser.gatherUsageStats false

PYTHONDONTWRITEBYTECODE=1 BANCINC_RUNTIME=LOCAL .venv/bin/python -m streamlit run phase10b_app.py --server.address 127.0.0.1   --server.port 18515 --server.headless true --browser.gatherUsageStats false
```

For simultaneous startup, use the runbook's background/PID/log shell syntax; the commands above show actual argument/environment values without obscuring them with redirection. Loopback URLs were `http://127.0.0.1:18514`, `:18511`, `:18515`.

| App | Fresh evidence | Result |
|---|---|---|
| Original | `original/browser_verification.json`, nine viewport captures, `main.log` | Nine native views rendered, no Streamlit exceptions; source 50,000 / 2,052 / 20 / 47,928 |
| Phase 9 | `phase9/browser_result.json`, `ingestion.log` | Rendered; cap accepted; isolated synthetic processing/activation/rollback/rejection passed |
| Phase 10B | `phase10b/browser_result.json`, `business.log` | All four views; separately labelled DEMO upgrades; source value 10,003; twelve viewport/view checks passed |

Paths above are relative to the private temporary root. Late health requests independently returned HTTP 200 `ok`: main 11.25 ms, ingestion 4.29 ms, business 7.57 ms. These are **measured health request latencies, not cold startup times**. Initial original navigation/render/capture observation was 14.666 seconds; all apps were preloaded before interaction tests. No complete process-start-to-first-render duration was recorded.

Existing canonical data, manifest, alias key, policy, frozen reference and trusted historical JSON were accessible; no installation, rebuilding, key generation or inference was needed. Runtime logs had no traceback/application exception. Streamlit suggested optional Watchdog installation; no dependency was installed.

## Restart recovery and shutdown

Main process 66481 was terminated to test persistence. The immediate replacement reported `Port 18514 is already in use` at 13:11:54.899 local time: shutdown had not completed. After a listener check showed closure, the identical launch succeeded as PID 67109 (`main-restart-2.log`). Browser reopen verified the same APPROVED_LOCAL case and two events; 11.621 seconds measured including render/check/captures. This transient failed restart is disclosed, not counted as first-attempt success.

At completion, owned PIDs 67109 (replacement main), 66482 (ingestion), 66483 (business), 66484 (isolated Chrome) received TERM. Subsequent lsof found no listeners on the four rehearsal ports. Existing unrelated listeners were untouched. Private evidence/state retained outside the repo. No server is claimed to be still running.
