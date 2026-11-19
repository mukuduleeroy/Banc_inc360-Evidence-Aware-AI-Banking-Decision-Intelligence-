# Phase 8A — six-gate contracts and integration boundaries

Audit date: 2026-11-18 (Africa/Harare). **Audit only; Phase 8B is not implemented or approved.** Local confidential evidence; no customer-level records or identifiers are included. VERIFIED = directly checked code/artifact/aggregate; INFERRED = reasoned conclusion; MISSING = not found in inspected scope; UNVERIFIED = not established by available evidence.

## Actual authority and precedence

**VERIFIED:** `engine.Case/evaluate` consumes normalized evidence from `evidence.validate` and `data_access.row_case`. It emits six gate records (`gate`, `status`, `reason_code`, `reason_codes`, `reason`), rating, action, priority, evidence, policy_version and human_review_required. Any ABSTAIN dominates CAUTION; any CAUTION dominates SUPPORTED. Priority does not override a gate. Current policy version is phase2-1.

| Gate | Input contract / actual failure behavior | Codes and tests | Integration risk |
| --- | --- | --- | --- |
| G1 Integrity | Identifier; strict booleans; linkage/date/future-snapshot controls; finite recency/pct; row_case checks 90-day/deposit/volume/account-count domains and counts consistency; manifest lineage issues. Failure → ABSTAIN | INTEGRITY_VALID; INVALID_CUSTOMER_ID, INVALID_OWNERSHIP, INVALID_TEMPORAL_EVIDENCE, INVALID_* typed flags/measures, INCONSISTENT_EVENT_COUNTS and manifest issues. `test_evidence`, `test_cohort`, `test_queue`, `test_deployment_data`, gate matrix | New helpers must not replace linkage/lineage flags or rewrite trusted data hashes; current flags rely on validated supplied inputs, not independent bank attestation |
| G2 History | qualifying_events_180d finite nonnegative integer. 0–1 → ABSTAIN; 2–3 → CAUTION; 4+ → PASS; invalid → ABSTAIN | HISTORY_INSUFFICIENT/BORDERLINE/SUFFICIENT; INVALID_QUALIFYING_EVENTS_180D. `test_engine` history boundaries, evidence and matrix | Segment/AI interest cannot impute unknown history or promote borderline evidence |
| G3 Method | uses_model_for_action must remain false for current operational rules; a requested fitted method → ABSTAIN even if model_approved=True | APPROVED_RULE_METHOD / MODEL_NOT_APPROVED. `test_evidence`, `test_gate_protection` combination/model-column tests | G3 blocks declared model use; it cannot autonomously detect a developer secretly using model scores while leaving the flag false |
| G4 Current status | Known Active customer/account and Verified KYC required; missing/unknown/restricted/frozen/dormant/other recognized noneligible state → ABSTAIN | CURRENT_CHECKS_PASSED / CURRENT_RESTRICTION / INVALID_CUSTOMER_STATUS, INVALID_ACCOUNT_STATUS, INVALID_KYC_STATUS. Existing domain/UI tests plus 18 G4/G5 cases | Product/segment/high-value scores cannot override restrictions; snapshots have unknown effective date |
| G5 Product suitability | Prototype Savings-only; known parseable holdings; not already held; usable nonblank rationale; consistent feature gap. Failure → ABSTAIN | SUITABILITY_REVIEW_REQUIRED / UNSUPPORTED_PRODUCT / PRODUCT_ALREADY_HELD / NO_BEHAVIOURAL_EVIDENCE / INVALID_HOLDINGS / INCONSISTENT_PRODUCT_GAP / INVALID_BEHAVIOURAL_REASON. Engine/evidence/queue/product UI/gate-protection tests | Source enum is not bank catalogue. Segment-specific suitability absent. Rationale semantic truth depends on source rebuild, not arbitrary free text |
| G6 Human control | automatic_outreach=False, human_review_required=True and staff_verification_required=True; otherwise ABSTAIN | HUMAN_REVIEW_REQUIRED / UNAUTHORIZED_ACTION; invalid flag types also fail G1. Human-control tests, replay/forgery matrix | PASS means mandatory human-control conditions, not completed bank sign-off or contact permission |

All statuses/reasons are existing strings; no new threshold, code, precedence or PENDING engine state was introduced by this audit. Display BLOCK · ABSTAIN is a Phase 7 visual mapping only (`design_system.gate_cards`).

## Review, stale evidence and forged outcomes

**VERIFIED:** `ReviewService.current()` uses fresh disk features/manifest and the engine. `record_review()` checks identity, data/manifest/policy/version/decision hashes, revision, inspected snapshot, reviewer, bounded reason and acknowledgement, plus current SUPPORTED eligibility for APPROVE. Evidence is checked again before commit. Explicit refresh appends a new snapshot/event; old history is preserved. `normalize_passport()` rejects incomplete/mismatched gates, inconsistent rating/control evidence and any simulated/action_authorized=False context.

`AuditStore` provides transactional cases/events/snapshots/references, reviewer attribution, FKs, append-only triggers and snapshot hashing. It is not tamper-proof against its filesystem/database owner. Demo reviewers are unverified labels. No current workflow sends communications or grants production authorization.

The optional ReviewService provider is a trusted test adapter, not an acceptable browser/upload/model-result channel. Do not expose it to untrusted JSON or experimental predictions. Production/default current evidence must continue to be recomputed from the validated source.

Tests: 96 representative gate status combinations, 18 G4/G5 cross-cases and seven forged SUPPORTED cases (`tests/test_gate_protection.py`); required actor/reason/inspection, current source/policy, concurrency, idempotency, rollback and append-only cases (`test_review_service.py`); native review/persistence/stale/error checks (`test_durable_ui.py`, `test_presentation.py`).

## Exact Phase 8B boundaries

1. Source banking segment is display/group metadata only. Do not add it to Case, alter G5 thresholds or imply source label = approved suitability.
2. New segment metadata must be allowlisted and join by alias into copies. Do not mutate index.records, Case fields, global ranking, canonical features or stored Passport payloads.
3. Product explanations must consume `index.passport(alias)` and its actual G4/G5/final reasons; never synthesize SUPPORTED or call a suggestion an approved offer.
4. Historical model metrics belong in an explicitly experimental comparison region with data/code/cutoff provenance. Do not write them into priority, product_gap, behavioural_reason, rating/action/gates or review context.
5. No fitted inference is available now. Any future experimental predictor must remain non-actionable and outside queue/review inputs; approval requires separate model governance, not a boolean/UI toggle.
6. Preserve G6 controls and call the existing review service for all real review writes. Add no communication/offer endpoint or AI-driven approval shortcut.
7. Preserve canonical data/manifest/policy fingerprints and full decision digest. Display filtering may change visible subsets but not the authoritative index or full-population outcome totals.
8. Keep replay pure and resettable; neither source metadata panels nor predictions can erase original lineage failures or save simulations as current facts.

## Known scope limitations

G1/manifest evidence is trusted local build lineage, not signed bank attestation. Current snapshot effective dates and bank-level segment/product rules are missing. No test set can prove all future integrations safe. Before accepting 8B, fix the regression runner's 308-versus-443 retention baseline (report 09), add behavior-specific isolation tests, then rerun full source-bound acceptance after team authorization. Do not implement those changes in Phase 8A.
