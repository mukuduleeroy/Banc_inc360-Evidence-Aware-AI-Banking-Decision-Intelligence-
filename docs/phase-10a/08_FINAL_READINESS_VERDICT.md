# Phase 10A final competitive-readiness verdict

Date: 2026-11-20 (Africa/Harare).

**CONDITIONAL — technically verified local demonstration, but incomplete challenge coverage.** The build can be presented honestly as an evidence-aware analytics and governed review prototype. It should **not** be pitched as fully satisfying all challenge capabilities without further clarification/corrective work, chiefly actual upselling and a defensible high-value definition. The existing Phase 9 technical PASS remains valid; this audit does not rewrite it into business-completeness certification.

## Requirement counts and critical insufficiency

Using the **seven official statements supplied in the task**:

| Verdict | Count | Requirements |
|---|---:|---|
| MET | **4** | R1 transaction analysis; R5 actionable review insights; R6 dashboards/visualisations; R7 practical historical AI/data analytics |
| PARTIAL | **3** | R2 churn identification via inactivity proxy; R3 high-value identification via activity proxy; R4 combined cross-selling and upselling |
| MISSING | **0 whole statements** | R4 has a missing sub-capability, explicitly detailed below |
| UNVERIFIED | **0 whole statements** | External/production claims are separately unverified and are not silently included as met |

R4 decomposes into **cross-selling MET at prototype scope / upselling MISSING**. Across eight atomic capabilities (splitting that compound statement), totals are **5 MET / 2 PARTIAL / 1 MISSING / 0 UNVERIFIED**. There is a **CRITICAL insufficiently implemented requirement component: actual upselling**. No implemented tier hierarchy, upgrade relationship, upgrade eligibility or actual upsell example exists. A Savings gap discussion cannot be renamed an upsell.

MET does not imply bank approval, deployed AI, measured business effect or an organizer score. The challenge wording/weights were supplied by the user; an independently authenticated official organizer rules document was not found in the repository. External rule provenance beyond that brief remains UNVERIFIED.

## Highest-risk judging gaps

1. **Upselling is genuinely absent.** Existing known product holdings and one Savings cross-sell rule do not establish a product upgrade. Presentation alone cannot close this gap.
2. **“High value” is activity ranking, not commercial value.** The percentile uses absolute 180-day USD turnover; breadth/accounts are context. No balance/profit/margin/LTV classifier or validated segment-specific economic threshold exists. A manager can inspect high-activity customers but cannot demonstrate confirmed high profitability.
3. **Churn identification is an inactivity proxy with a disconnected historical experiment.** Operational output is recency/coverage/triage, not per-customer churn probability. The offline label is future 90-day no-activity, not verified churn. No retention intervention effect is measured.
4. **AI is real but historical.** Two verified prior offline experiments and an accurate JSON-driven panel exist. No saved fitted artifacts or operational inference exist. This meets historical practical-AI demonstration scope, but calling it deployed churn AI would be false.
5. **Demo/provenance distinctions need precision.** Original Audit page reads older phase JUnits (latest displayed 308), whereas accepted full Phase 9 JUnit is 574. Phase 9 activation affects its companion only, not nine-dashboard switching. Local review approval is not banking authority.

## Verified technical baseline and audit method

Read-only investigation confirmed:

- **574 prior tests passed**, including **504 retained + 70 Phase 9 cases**, zero failures/errors/skips and **96 gate-combination cases**. Actual JUnit parsed; manifest PASS/exit code 0, before/after source hashes equal and exact JUnit SHA verified. These are the accepted **2026-11-19 recorded results**, not a newly executed 2026-11-20 suite.
- **87 current source/test/config/asset hashes** match the full-run manifest; the **79 accepted Phase 8B source files** remain unchanged. Current HEAD is `6d06878a992980971f468535e8486b5eb577ade3`; existing uncommitted Phase 9 additions are included in verified hashes.
- Canonical index was loaded with an **explicit read-only existing key**, evaluated only in memory and compared to the frozen full keyed digest: **50,000 customers; 2,052 SUPPORTED / 20 CAUTION / 47,928 ABSTAIN**, no invalid/excluded customer cases, no lineage issues; **16-column contract** verified.
- All **24 protected artifact hashes**, old **49 Phase 8B database/sidecars** and **55 Phase 9 checkpoint database/sidecars** match. Additional Phase 9 source/helper hashes match final preservation evidence.
- Existing original-app browser receipt verifies nine native views, KYC replay/reset and real process restart with one persisted case/two events/two snapshots/16 feature references. Existing Phase 8B responsive evidence covers nine views at desktop/tablet/mobile; Phase 7 adds 1280-width samples.
- Existing Phase 9 browser receipt verifies synthetic upload→validation→processing→reconciliation→six-gate preview→activation→rollback→invalid-upload rejection, plus three responsive width samples. The stored registry currently remains on baseline.
- **303 pre-existing source/evidence/report/snapshot/history files were hashed at audit start and rechecked unchanged.** Initial/post-audit comparison found no missing or altered file. This includes existing accepted reports and Phase 9 private snapshot/registry files; no registry constructor/recovery operation or SQLite connection was used.

Execution was limited to `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B` read-only hash/JSON/XML/DOCX/CSV/index inspection, source reads/searches and in-memory analytics. **No pytest run, app/server/browser launch, fitting, source rebuild, upload, snapshot/registry write, review event, acceptance update, commit, push or deployment occurred.** Only the eight requested new Markdown reports under `docs/phase-10a/` were created.

### Frozen integrity fingerprints

| Artifact | Verified SHA-256 |
|---|---|
| Canonical CSV | `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993` |
| Canonical manifest | `e7498a20977dae9fe247c9ad4379ac0a62c74f09e75d3b8896d39861a3a60a7c` |
| Policy | `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae` |
| Full original decisions/priorities/reasons | `7b0b071c768b393a51d249fedf45937b5bd17f845a72dcaa23a5447c2b6fc0e3` |
| Accepted Phase 9 JUnit | `9cf3d25aa2705b651864b1cb34511e5d8fd73e3260cb0e9651e512ed8212cff8` |

Primary baseline evidence: `outputs/final_acceptance/phase-9-final/{tests.xml,run_manifest.json,acceptance.json,phase9_acceptance.json}`; protection checkpoints `outputs/phase8b/checkpoint.json`, `outputs/phase9/checkpoint.json`; final new-source/protection evidence `outputs/phase9/final_preservation.json`. No customer-level confidential record is copied into the reports; synthetic examples are existing independently invented fixtures.

## Business numbers a judge will challenge

- **95.856% ABSTAIN is withholding of sales permission**, not model uncertainty or churn rate. Among these cases, 39,928 have CURRENT_RESTRICTION, 27,483 NO_BEHAVIOURAL_EVIDENCE, 17,391 HISTORY_INSUFFICIENT and 10,000 PRODUCT_ALREADY_HELD; reasons overlap. Another 1,134 carry a HISTORY_BORDERLINE caution code alongside a blocker.
- All 2,052 supported cases have known other products and no Savings, so the additional-product relationship is established. **Only 23** are globally Higher activity; eligibility is not commercial value. No measured revenue, uptake or retention result exists.
- Historical LR ROC-AUC **0.965207**, AP **0.982397**; recency **0.940630 / 0.968649**; HGB **0.942177 / 0.965445**. All three Precision@500=1 and Lift@500=1.685568 on a 32,609-customer holdout with 59.3272% inactivity prevalence. These are not accuracy, conversions or retention uplift. Repeated identities, a single temporal holdout and source-completeness assumptions limit interpretation.

## Recommended corrective actions

**Without development:** rehearse the existing artifact-bound demonstration, show the genuine Savings additional-product relation, explain activity/value and inactivity/churn boundaries, show historical AI separately from operational rules, use the separate latest test receipt and distinguish the two interfaces. These improve honesty and evidence presentation immediately.

**Requires further specification/authorization:** a genuine upsell product/upgrade relationship with eligibility and evidence; agreement on whether an explicit activity-based value proxy suffices or economic value data are needed; any deployment of fitted churn predictions or expanded operational product policy. Do not weaken G3/G4/G5/G6, relabel unsupported actions, invent bank terms/profit, rewrite accepted data or add live inference merely to fill a slide.

**Ready for final pitch without further development?** Ready for a truthful **limited-prototype** demonstration, but **not recommended as a fully challenge-complete final entry** without resolving the missing upsell component and high-value/churn interpretation. Acknowledging limitations is necessary; it does not implement a missing capability. No new feature or corrective action was performed in Phase 10A.

## Report index

1. `01_OFFICIAL_REQUIREMENTS_MATRIX.md` — seven-statement matrix, atomic decomposition and weights.
2. `02_HIGH_VALUE_CUSTOMER_AUDIT.md` — exact activity definition, segments and reproducible proxy example.
3. `03_CROSS_SELL_UPSELL_AUDIT.md` — valid prototype cross-sell and absent upsell.
4. `04_CHURN_AND_AI_AUDIT.md` — chronology, target, metrics, model/runtime separation and limits.
5. `05_ACTIONABILITY_AND_INGESTION_AUDIT.md` — permission/queue/audit behavior, companion scope and nine-view technical evidence.
6. `06_JUDGE_QUESTIONS_AND_DEFENCES.md` — 14 difficult questions with truthful evidence, limitations and live-demo scope.
7. `07_PRIORITISED_GAP_REMEDIATION.md` — smallest safe corrective actions and protection risks, recommendations only.
8. This final readiness verdict.
