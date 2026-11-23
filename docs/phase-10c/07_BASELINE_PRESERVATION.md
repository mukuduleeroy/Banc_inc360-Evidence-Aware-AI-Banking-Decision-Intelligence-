# Phase 10C baseline preservation — PASS

Date: 2026-11-20 (Africa/Harare). Investigation only. **Only the seven requested new Markdown reports under `docs/phase-10c/` were written.** No implementation, estimator fitting/loading, customer predictive scoring, model serialization, accepted file update or application-state mutation occurred.

## Accepted evidence verified before investigation

Current HEAD: `6d06878a992980971f468535e8486b5eb577ade3`. Existing Phase 9/10B/10A work remains uncommitted; accepted content was checked against actual manifests rather than assuming HEAD alone describes it.

- `outputs/final_acceptance/phase-10b-final/run_manifest.json`: PASS, pytest exit 0, matching before/after source hashes and **96 current source/test/config/asset files** still match. Exact JUnit bytes match that manifest.
- `tests.xml`: **647 recorded passing cases**, no failure/error/skip elements, including **96 gate-combination cases**. These are prior accepted results; the suite was **not rerun**, since its original synthetic reproducibility test would fit models and other tests can write isolated state.
- `phase10b_acceptance.json`: retains all 574 Phase 9 cases plus 73 new cases; original source/population invariants and separate synthetic/value reconciliations.
- `outputs/phase10b/checkpoint.json`: all **242 protected evidence/state hashes** still match, including canonical files, original source/policy modules, historical outputs, accepted reports, Phase 9 registry/snapshots and **58 pre-existing database/sidecars**.
- `outputs/phase10b/final_preservation.json`: every new implementation/helper/test and Phase 10B report hash matches. Phase 10B's original source-derived Higher activity count remains **10,003**; synthetic fixtures and original operational totals stay separate.

The canonical index was loaded read-only with the already-existing key (no key-creation helper), verified against the frozen reference and compared in RAM: **50,000 customers; 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN**, unchanged exact keyed outcome/unrounded-priority/reason digest and 16-column contract. This is deterministic accepted-baseline verification, not generation of fitted inactivity predictions or changes to decisions.

## Whole-project before/after verification

At audit start, **10,501 pre-existing files** totalling **608,744,095 hashed content bytes** were enumerated and hashed. This includes application source, tests, docs/accepted reports, all outputs/snapshots/registries/model-evaluation artifacts/history files, existing cache files and the entire local `.venv` dependency tree. File symlinks are represented by link text, without following external targets. VCS `.git` metadata is excluded; no commit, push or branch change was performed. The new `docs/phase-10c/` subtree is excluded because it is the only authorized addition.

Relative-path/content hashes were sorted within each top-level group and each group hashed as compact JSON. The complete group map, file inventory count and total content bytes were held **only in tool-session memory**, not written to another checkpoint/artifact. The final read-only pass found the same file sets/content digests/count/bytes in every group: **no added, missing or changed pre-existing project/dependency file outside the authorized report subtree**.

Aggregate SHA-256 of the sorted group summary:

`ba20d78748bbe4db761ee38d7709d51118a0c63cfad1a09d2a4c531d07863cdb`

The original source ZIP, outside the repository at `/Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip`, was additionally hashed before and after; it matches the canonical source manifest and remains unchanged. Content hashes are local preservation evidence, not externally signed banking attestation or production security certification.

## Frozen fingerprints

| Artifact | Verified unchanged SHA-256 |
|---|---|
| Canonical CSV | `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993` |
| Canonical manifest | `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c` |
| Operational policy | `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae` |
| Full accepted decision/priority/reason digest | `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3` |
| Accepted Phase 10B JUnit | `ee2297d3b34355eff70c8694190d3a49ce5a2b4ba09a6cca3cb2c33359a332bb` |
| Original source ZIP | `4a7919a7a98f8340d2d7589ec8cfdbe352742686df97cb6e8d6bd58d93fd4e1b` |
| Historical evaluation code | `3895e2801a63861d637fea3bc48a9b06be129ee541bc68d0480661d6b895155d` |
| Primary historical evaluation JSON | `ee516bb25c0e0c467b7d5d8fffdb9a8f4fe50bc76c2fd6d4c399376594a97200` |

## Execution boundaries actually followed

Read-only commands used `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B` for stdlib/JSON/XML/hash/dependency/code inspection, existing-key deterministic index checks and in-memory source aggregate analysis. Original `audit_source`, `cohort` and `validate_temporal_coverage` were used only as pure read/compute helpers to confirm observed labels/windows/distributions. No feature/label table or customer-level prediction was persisted, and no new performance metrics/calibration figures were calculated.

Deliberately **not executed**:

- `historical_evaluation.evaluate`, fit/predict methods, metrics/bootstrap, model save/load or any training test.
- `historical_evaluation.run` or CLI `--audit-only`: even audit-only creates an output directory/audit file in that wrapper.
- `build_data.run`: would write features/manifests; no canonical rebuild occurred.
- Streamlit/application/browser workflows: loading some accepted views may initialize review state even before a review click.
- `SnapshotStore` or `AuditStore` construction/recovery, SQL connections, migrations, review events or activations.
- Acceptance/regression runners, which write fresh outputs; old results were inspected instead.
- Any public deployment, data/model upload, customer communication, external banking API, Git commit or remote push.

Existing Phase 9 processing/registry/snapshots, Phase 10B code/fixtures/reconciliation/browser evidence, all nine original dashboards, historical evaluation outputs and protected database histories are preserved. The seven reports are the complete Phase 10C deliverable; no model, proposed feature, new prediction artifact or implementation authorization was created.
