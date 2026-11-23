# Phase 9 baseline integrity report

**PASS.** The accepted Phase 8B system remains intact. Verification is read-only; no canonical data rebuild or frozen-reference regeneration occurred.

Current source HEAD: `6d06878a992980971f468535e8486b5eb577ade3`. Historical Phase 8B report HEAD `ab02f09bc78d7e809ee22cb25f0819680151f16d` is preserved. The newer revision was verified by actual source bytes, not assumed equivalent: all 79 accepted source files matched the hash-bound Phase 8B run manifest before implementation and still match after implementation.

The user clarified the accepted **16-column contract** on 2026-11-19. Its exact names/order/types/semantics are preserved by reusing the unchanged builder/index; no seventeenth field exists. Only new Phase 9 documentation corrects the older count; historical acceptance reports remain untouched.

## Frozen data/policy/decision evidence

| Artifact | Unchanged SHA-256 |
|---|---|
| Canonical CSV | `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993` |
| Manifest | `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c` |
| Policy | `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae` |
| Full customer decision/priority/reason digest | `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3` |

Population: **50,000**; **2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN**. No excluded/invalid canonical customer records. The full keyed digest binds exact unrounded priorities, outcomes, reason lists and validity flags; customer IDs are hashed in memory and never exported into this report.

## Protected source and persistent evidence

- All **79** accepted source/test/config/asset hashes unchanged, including dashboards/navigation, engine/evidence, builder/data access/analytics, segmentation, Savings rules, replay, review/audit, historical evaluation and design tokens.
- All **24** protected artifact hashes unchanged, including canonical data/manifest, alias key and historical model receipts.
- All **49** database/sidecar files from the old Phase 8B protection checkpoint verified unchanged during initial inspection.
- Phase 9 then captured **55 currently existing** database/sidecar files, including later Phase 8B demonstration evidence. Every one stayed byte-identical during Phase 9. No existing database was migrated, reset, overwritten or used for ingestion.
- All **504** accepted test IDs retained; no accepted test implementation changed. Original gate-combination count remains 96.
- No existing tracked application file has a working diff from the implementation; only new Phase 9 files/documentation/tests were introduced.

Private checkpoint: `outputs/phase9/checkpoint.json`. Source-only 79-file rollback archive: `outputs/phase9/rollback-source.zip`; it contains no customer data, alias key or database. Detailed post-integration proof: `outputs/final_acceptance/phase-9-final/phase9_acceptance.json` and `outputs/phase9/final_preservation.json`.

## Six-gate and AI integrity

G1–G6 thresholds/precedence, eligibility, evidence sufficiency, product suitability, approved-method controls and human-review restrictions are unchanged. The adapter calls the existing builder/index/engine instead of reproducing gate logic. New synthetic tests compare full gate objects, exact priority scores and reason lists with direct existing-engine evaluation; original anti-bypass and all gate combinations passed.

No historical experiment/output was replaced, no live probability added, no model trained on real data, no fitted estimator loaded, and no ML score included in priority. The original historical recency-only comparison remains distinct from operational composite triage.

Activation affects a new companion JSON registry only. It cannot alter the original app's dataset selection or customer decisions. Rollback selects the original canonical dataset read-only; it does not regenerate data. Review persistence and replay/reset were reverified with fresh test databases. There is no customer outreach, banking authorization, public deployment or remote push.
