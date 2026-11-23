# Phase 9 implementation report

Date: 2026-11-19 (Africa/Harare). User authorization explicitly confirms the accepted **16-column** feature contract. Historical reports are not rewritten.

## Additive architecture

The accepted `app.py`, its nine native routes and every accepted source file remain untouched. The new local companion is `phase9_app.py`, titled Dataset Ingestion & Refresh. It uses the existing design-system functions without changing their tokens or definitions. No navigation integration was needed; the companion is opened at its own local URL.

Flow: bounded CSV upload → private staging receipt → source validation → unchanged `build_data.run` through an internally generated single-CSV ZIP → unchanged `data_access.load_index` and six-gate engine → exact reconciliation → immutable candidate directory → explicit companion-only activation → alias-safe inspection → explicit return to baseline.

Activation never changes existing dashboard loader paths, environment variables, alias key or canonical files. The companion preview clearly distinguishes a selected preview from the active registry selection. It may inspect a candidate before activation. Existing dashboards always retain the original dataset selection.

## New files

| File | Responsibility |
|---|---|
| `phase9_ingestion.py` | Bounded upload/storage, contract validation, feature/engine adapter, reconciliation, snapshot integrity, locked atomic registry, activation/rollback |
| `phase9_app.py` | Separate Streamlit companion; six labeled workflow sections; native widgets; no review or outreach endpoints |
| `phase9_demo.py` | Independently invented transaction generator and four synthetic CSV examples |
| `phase9_acceptance.py` | Run existing full acceptance and additionally require all 504 Phase 8B cases, unchanged 79 accepted source hashes and every checkpoint-protected artifact/history |
| `scripts/accept_phase9.py` | Actual local Chrome/Streamlit upload demonstration with fresh private storage; stops its own processes |
| `scripts/verify_phase9_browser.mjs` | Real CSV upload/validation/processing/preview/activation/rollback/invalid-input and responsive checks |
| `tests/test_phase9_ingestion.py` | 59 source/decision/snapshot/security tests |
| `tests/test_phase9_ui.py` | Six companion native UI/API/configuration tests |
| `tests/test_phase9_protection.py` | Five accepted-source/inventory/customer-invariance and isolation checks |
| `docs/phase-9/01`–`08` | Compatibility, implementation, contract, validation, testing, integrity, demo and final acceptance reports |

Private generated outputs: `outputs/phase9/checkpoint.json`, source-only `rollback-source.zip`, `examples/`, browser/test receipts and isolated snapshot stores. Existing Git ignore rules already exclude CSV/ZIP/SQLite and the entire outputs directory. No accepted ignore/config/dependency file was edited.

## Reused interfaces and safety

The original builder alone calculates historical windows, qualifying events, cash deposits, absolute USD volume, relationship percentile, source segment and current snapshot evidence. The original index adapter/engine alone supplies decisions, exact priorities, gate precedence and reason codes. No copy of those formulas is used for operational calculation in the new implementation. Tests independently compare the existing formula and full gate objects for fidelity.

Input validation is an additional admission boundary, not a replacement feature algorithm. Unsupported/ambiguous source evidence is rejected before processing. Missing status/KYC/holdings evidence remains unknown and follows existing abstention behavior. The stricter upload boundary is documented in 03.

Snapshots bind raw received CSV hash, internal ZIP hash, builder feature/manifest hashes, original policy/code hashes, Phase 9 adapter hash, decision fingerprint and reconciliation summary. A separate private alias key is used for Phase 9 customers. Snapshot data is never rewritten by activation or rollback; verification recomputes decisions via the unchanged engine and rejects tampering/stale policy/code.

Registry writes use same-directory temporary files, file fsync and atomic replacement under a local process lock. A checksummed last-committed backup permits recovery from an unreadable/missing current registry. Unregistered orphan snapshots and interrupted temporary files cannot automatically activate. Existing snapshots are never deleted by cleanup or rollback.

## Local constraints

The companion refuses a non-LOCAL runtime and refuses to enable uploads unless the server transport cap is at most 5 MiB. The installed Streamlit version does not have a per-widget upload-size argument; the supported server launch flag is required. There are no new dependencies, fitted inference, serialized model loaders, public deployment, banking approvals or automatic communications.

Limits and exact commands are in 03/07. Verified final outcomes and any development failures are recorded in 05/08, without implying production-grade security or external supplier authenticity.
