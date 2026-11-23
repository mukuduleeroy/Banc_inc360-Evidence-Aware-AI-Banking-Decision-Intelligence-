# Phase 12 integrity exception finding

Date: 2026-11-20. Finding: **documented metadata-only functional exception; strict checkpoint conformance remains unresolved.** No file was repaired, deleted, regenerated or silently waived.

| Reference | docs/.DS_Store SHA-256 |
|---|---|
| Accepted Phase 10B checkpoint | `ea6f322b7ab20d67065f222bab61cc09cb60a1fd0bace59b84e3efbab6eeb5a5` |
| Phase 11 reported entry/exit; independently observed Phase 12 entry | `3c65d81d88a814fec6685ee5e52b414b8d587dc089ac155fde769b5759a1af19` |
| Phase 12 post-rehearsal observation | `071a4419aea731e4850134894d01ffc39c7c666580c0016bf1c2920d87bf6f13` |

The expected hash is an actual `protected_hashes` entry in `outputs/phase10b/checkpoint.json`, not a guessed checksum. `outputs/phase10b/final_preservation.json` records the original 242/242 acceptance. Phase 11 reports 01/10 document the first mismatch before Phase 11 writes, establishing that it predates this phase. We cannot independently date the earlier change or attribute either change to an actor.

`file docs/.DS_Store` identifies Apple Desktop Services Store. The current file is 6,148 bytes, with first 16 bytes `00000001427564310000100000000800` (Bud1 metadata header). Its observed modification timestamp is 2026-11-20T11:14:13.156591+00:00. Timestamp and format establish the observed file type/time, not the writer or a causal explanation. No banking content is extracted from it.

Application path inspection and `rg -n 'DS_Store' --glob '*.py' --glob '*.mjs' --glob '!outputs/**' --glob '!docs/**' .` found no direct application reference. Runtime loaders read named CSV/manifest/key/policy/JSON artifacts, views and assets; they do not load this docs metadata as customer evidence, policy or UI source. Existing source-manifest discovery walks Python source and assets, not this docs file. The exception is read by **integrity tooling**, because the protected checkpoint includes its path: `tests/test_phase10b_isolation.py::test_all_87_accepted_sources_and_protected_state_remain_unchanged` and `phase10b_acceptance.py` compare all protected hashes. Thus it is functionally irrelevant to banking decisions but relevant to exact acceptance policy. The three apps and targeted gates operated with the mismatch present.

## Entry/exit preservation

An in-memory entry inventory covered 10,518 pre-existing files / 608,902,097 content bytes, excluding `.git` and the new permitted `docs/phase-12/` subtree. Sorted per-top-level SHA-256 groups detected **only docs drift**. Replacing just the current DS_Store digest with its observed-entry digest in the comparison reproduced the exact original docs group SHA `9f21c514ee0a9d25122209a06b2a29eb1d313dffb9b5059f4be09b071ab62758`. This establishes that **all other 10,517 pre-existing files were unchanged**; the one newly observed delta is explicitly reported, not hidden by an updated baseline. Runtime work was stopped when this delta was detected. No command intentionally wrote that file; attribution is unknown.

Both entry and post-rehearsal checks found 241/242 old checkpoint files matching, the sole exception being this same metadata path. All 58 protected SQLite/sidecars match. All 96 accepted run-manifest files, the 87 prior sources, ten Phase 10B source/helper hashes and eight Phase 10B report hashes match. Phase 9 stores/snapshots and historical AI artifacts remain unchanged.

Canonical CSV SHA `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`; manifest `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c`; policy `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`. Full keyed outcome/exact-priority/reason digest before and after: `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3`. Original external ZIP remains `4a7919a7a98f8340d2d7589ec8cfdbe352742686df97cb6e8d6bd58d93fd4e1b`.

Disposition: classify as a **documented metadata-only exception for functional rehearsal**, without editing checkpoints/tests or declaring strict integrity PASS. Owner must explicitly acknowledge its release disposition if an exception is acceptable; a zero-difference checkpoint requirement is still unmet. Do not downgrade technical suitability solely for this file, or claim that Phase 12 achieved complete byte preservation.
