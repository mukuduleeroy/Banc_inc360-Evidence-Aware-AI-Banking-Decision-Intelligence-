# Phase 11 release freeze and integrity

Date: 2026-11-20 (Africa/Harare). **CONDITIONAL documentation freeze: application/data integrity verifies, but one pre-existing protected metadata checksum exception remains unresolved.** No accepted source, policy, dataset, model, test, report or application state was modified in this phase.

## Release identity and scope

Project: Banc-Inc360, an independent student banking decision-support prototype, not operated by BancABC. Source HEAD is `6d06878a992980971f468535e8486b5eb577ade3`. Phase 9/10B code and later documentation exist as uncommitted/untracked working files; HEAD alone is **not** the complete accepted release. The authoritative technical snapshot is the actual 96-file source/run manifest in `outputs/final_acceptance/phase-10b-final/run_manifest.json`, supplemented by the new-file/helper hashes in `outputs/phase10b/final_preservation.json`.

This is a documented freeze, not a new Git tag, permission lock, deployment or updated acceptance baseline. No commit, push, packaging archive or publication was performed. Only the ten Markdown files in `docs/phase-11/` are new deliverables.

## Verified release facts

| Item | Evidence and current verification |
|---|---|
| Original decisions | Read-only accepted index: 50,000; 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN; exact keyed priorities/reasons/digest unchanged |
| High Relationship Activity | Existing classification reconciles 10,003 original customers, 39,997 outside band, zero unavailable; no reranking |
| Canonical feature contract | Exactly 16 columns, unchanged header/semantics; no new feature fields |
| Nine original views | All nine `ui_shell.PAGES` entries and `views/*.py` exist; renderers/navigation source matches accepted manifest; prior all-nine browser/native tests recorded |
| Phase 9 companion | `phase9_app.py` separate; private candidate/registry activation only, original dashboards do not switch |
| Phase 10B companion | `phase10b_app.py` separate; seven independent synthetic upsell scenarios, 1 eligible / 3 missing / 3 ineligible, DEMO_* only; real source value proxy separate |
| Six gates / Savings policy | `engine.evaluate`, evidence/row adapter/priority and original G1–G6 unchanged; no model authorization or new product policy |
| Historical AI | Two prior real-source evaluation receipts, code/feature/model-result fingerprints unchanged; no fitted live artifact |
| Current source | All 96 covered source/test/config/asset hashes match completed run; Phase 10B new source/helper/report hashes also match |
| Historical test result | 647 passed / 0 failures/errors/skips; 96 gate-combination cases; exact JUnit matches prior completed source-bound run |
| Protected data/state/reports | **241 of 242** checkpoint hashes match; the sole exception is `docs/.DS_Store`, detailed below. All 58 checkpoint-protected database/sidecars match; no Phase 9 registry/snapshot drift |

### Test result provenance: no fresh 647-test claim

The accepted run completed on 2026-11-20, pytest duration 104.31s, recorded by `tests.xml`, `run_manifest.json`, `acceptance.json`, `phase9_acceptance.json`, `phase10b_acceptance.json`. Its JUnit has 647 case entries and no failure/error/skip elements. Its before/after source hashes agree and still match current source.

**The suite was not rerun in Phase 11.** Existing tests include estimator fitting and state-writing fixtures; the phase forbids model training and protected-state modification. No caches were deleted. Historical receipt verification is used as permitted, not misrepresented as a fresh pass. Source equality also does not erase the separate state-file checksum exception: current protection guards would reject that metadata mismatch until properly resolved.

## Exact protected metadata exception

Read-only comparison on entry found only:

| File | Accepted checkpoint SHA-256 | Observed entry SHA-256 |
|---|---|---|
| `docs/.DS_Store` | `ea6f322b7ab20d67065f222bab61cc09cb60a1fd0bace59b84e3efbab6eeb5a5` | `3c65d81d88a814fec6685ee5e52b414b8d587dc089ac155fde769b5759a1af19` |

The OS file-identification utility reports **Apple Desktop Services Store**. This is folder metadata, not application/business logic or banking evidence. The actor/time/cause of the change is not established; it was already different before Phase 11 reports were created. No other protected mismatch was found.

Do **not** delete, restore or edit it, relax tests or overwrite the old checkpoint to manufacture a clean result. Owner-reviewed disposition through the project's authorized release process is required before an unqualified checkpoint-conformant freeze. This report records an exception; it does not approve a new baseline. Current application/data can be demonstrated within its verified scope, but no unqualified release PASS is asserted.

## Frozen fingerprints

| Artifact | Verified SHA-256 |
|---|---|
| Canonical CSV | `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993` |
| Canonical manifest | `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c` |
| Policy | `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae` |
| Full original outcome/unrounded-priority/reason digest | `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3` |
| Accepted 647-case JUnit | `ee2297d3b34355eff70c8694190d3a49ce5a2b4ba09a6cca3cb2c33359a332bb` |
| Original source ZIP | `4a7919a7a98f8340d2d7589ec8cfdbe352742686df97cb6e8d6bd58d93fd4e1b` |

## Preservation protocol

An observed-entry inventory of **10,508 pre-existing files / 608,799,639 hashed content bytes**, including dependencies, existing caches, accepted source, reports, outputs, registries and databases, was captured in tool-session memory. This is a phase-preservation reference, **not replacement acceptance evidence**. VCS `.git` metadata and the new allowed `docs/phase-11/` subtree are excluded; file symlinks are represented by link text. Final comparison is reported in 10. The external original ZIP is separately hashed. No extra checkpoint file is written.

No server/browser, review/registry constructor, ingestion workflow, test runner, fitter or serializer was executed. `python -B`/PYTHONDONTWRITEBYTECODE read-only checks avoid new bytecode caches. Future live steps in 04 are a **runbook only**, using fresh disposable storage outside the protected tree; they were not performed during preparation.

Freeze discipline: stop feature development, preserve all accepted artifacts, keep synthetic/real/research boundaries explicit, and obtain the required manual release/organizer/data approvals listed in 09–10. Do not change protected code to resolve presentation issues.

## Completed phase-preservation comparison

Final comparison with the observed-entry inventory found **all 10,508 pre-existing files / 608,799,639 content bytes unchanged during Phase 11**, including the already-different metadata file. Sorted top-level group-summary SHA-256: `59f2a4b10a66f3aea6638b3bce481bb6ce4def4206214c1269852c36f7c48440`. External original source ZIP is unchanged. This proves phase preservation; it does **not** erase the pre-existing accepted-checkpoint exception: 241/242 match, `docs/.DS_Store` retains the observed entry hash above. Only the new Phase 11 report subtree is excluded as the authorized addition.
