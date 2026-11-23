# Phase 9 final acceptance

Date: 2026-11-19 (Africa/Harare).

**PASS — controlled local demo ready.** The strictly additive Dataset Ingestion & Refresh companion is implemented, reconciled and verified. This is not production banking/security approval, permission to publish customer data, live-model approval or authorization for outreach.

## Acceptance evidence

| Requirement | Result |
|---|---|
| Authoritative feature contract | User-confirmed 16 columns; exact names/order/types/semantics preserved by unchanged builder/index |
| Original accepted source | All 79 source files unchanged; no original dashboard, navigation, logic, design or dependency edits |
| Complete regression | 574 passed; all 504 original test IDs retained; 70 new; zero failures/errors/skips |
| Gate combinations | All original 96 cases passed; engine/thresholds/precedence/reasons unchanged |
| Freshness | Exact JUnit/run-manifest match; all 87 covered current source files unchanged during/after tests |
| Protected files | All 24 checkpoint-protected artifacts unchanged |
| Persistent histories | All 55 files existing at Phase 9 checkpoint unchanged; original 49 Phase 8B database/sidecars also initially reverified |
| Original decisions | All 50,000 outcomes, unrounded priorities, reason lists and validity flags match original digest |
| Original distribution | 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN |
| Source ingestion | Compatible bounded CSV; invalid inputs fail closed; no arbitrary schema/FX assumptions |
| Feature refresh | Original builder receives new private internal ZIP; no existing source/canonical output overwritten |
| Synthetic reconciliation | 14 source rows, four customers/accounts; one SUPPORTED, one CAUTION, two ABSTAIN; 100% decision coverage |
| Isolation and activation | New private snapshot/alias key/registry only; explicit activation and return to baseline; no original loader changes |
| Snapshot safety | Hash-pinned immutable receipts/artifacts; re-evaluated engine output; failed activation retains prior state; interrupted registry recovery tested |
| Live demo | Actual file upload, validation, processing, preview, six gate inspection, activation, rollback and invalid-upload rejection passed |
| Original application | Nine actual views, Evidence Replay/reset and local review persistence across a real restart passed |
| Responsive companion | 1440/768/390 samples, no page overflow or application exceptions; not formal accessibility certification |
| AI and privacy | Historical evaluation unchanged; no operational fitted inference or real-data training; synthetic demonstration only; no publication or outreach |

Full run receipt: `outputs/final_acceptance/phase-9-final/phase9_acceptance.json`; original acceptance checks also passed in that directory's `acceptance.json`. Independent final preservation and exact new-source hashes: `outputs/phase9/final_preservation.json`.

Pytest duration: **94.37s**. JUnit SHA-256: `9cf3d25aa2705b651864b1cb34511e5d8fd73e3260cb0e9651e512ed8212cff8`. Source-bound run started `2026-11-19T09:03:48.288162+00:00`, finished `2026-11-19T09:05:24.516953+00:00` (runner wall time includes setup). Current Git HEAD at checkpoint: `6d06878a992980971f468535e8486b5eb577ade3`. No new commit/push was performed.

## Frozen fingerprints preserved

- Canonical CSV: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`.
- Manifest: `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c`.
- Policy: `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`.
- Full original decision/priority/reason digest: `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3`.

No original dataset, policy artifact, historical AI output, frozen reference or old acceptance receipt was regenerated to obtain these results. Historical reports retain their old column-count wording; the user's correction is recorded only in Phase 9 documentation.

## Exact implementation scope

New source: `phase9_ingestion.py`, `phase9_app.py`, `phase9_demo.py`, `phase9_acceptance.py`, `scripts/accept_phase9.py`, `scripts/verify_phase9_browser.mjs`; three new `tests/test_phase9_*.py` modules. Eight new reports are in `docs/phase-9/`. Private generated examples, staging/snapshots and test/browser receipts live under the ignored `outputs/phase9/` subtree; new final regression evidence uses a fresh directory. Accepted source modifications: **none**.

The companion is intentionally separate. It does not add a tenth navigation entry to the accepted app or switch its nine dashboards to uploaded data. The authorized alternative dedicated snapshot-preview interface handles activation and inspection; explicit rollback selects the accepted baseline in that preview without altering canonical files.

## Resolved issues and limits

The initial 17-versus-16 description discrepancy was resolved by explicit user authorization; no schema change occurred. One development browser attempt exposed an unsupported per-widget Streamlit upload-limit argument. It was corrected in new code only: require server cap `--server.maxUploadSize 5` before rendering upload controls, add real-uploader/configuration tests, and repeat the browser/full-suite checks. Failed-run evidence is retained; no unresolved regression remains.

Supported source is UTF-8 compatible USD-normalized CSV only, 5 MiB/25,000 rows with a 50-alias preview. No arbitrary mapping or FX conversion. Source supplier authenticity, upstream FX correctness and public data-use permission are not certified. Current snapshot effective dates remain unknown. Private local registry/key/files are owner-trusted and unencrypted; snapshots are logically immutable through hash checks, not write-once media. Recovery can restore the preceding committed selection, which operators must inspect. Disconnected sessions can leave private staging files for controlled local cleanup. Existing live cloud parity/persistence limitations remain unchanged.

All automated test servers/browsers stop after their checks. To launch the two local interfaces and repeat the synthetic scenario, follow `07_DEMO_GUIDE.md`. No public deployment or next implementation phase was started.
