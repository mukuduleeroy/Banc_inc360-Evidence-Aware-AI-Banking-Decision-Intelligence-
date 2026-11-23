# Cross-selling and upselling — separate findings

## Cross-selling: MET at a narrow prototype scope

The app establishes known holdings and the absence of **Savings Account**, then proposes a Savings discussion supported by observed cash deposits and the six gates. It does not offer a product already held. This is a potential additional-product relationship, not simply a generic recommendation label.

Exact flow:

- `build_data.run` (`build_data.py:86`–88): >=2 historical cash deposits produces the recorded behavioral rationale; current pipe-separated holdings are aggregated and the Savings gap derived. Blank holdings remain unknown.
- `evidence.holdings` (`evidence.py:33`): parses only valid known holdings; unknown/malformed/duplicate labels are not treated as an empty portfolio.
- `data_access.row_case` (`data_access.py:32`): checks consistency of stored gap with actual ownership and adapts evidence to the existing engine.
- `engine.evaluate` (`engine.py:30`): G1 validity; G2 history (0–1 ABSTAIN, 2–3 CAUTION, >=4 PASS); G3 deterministic rule method; G4 Active customer/account and Verified KYC; G5 supported product, not already held, known ownership and nonblank rationale; G6 mandatory staff verification/review and no automatic outreach. The only operational product is Savings Account.
- `ui_views.product_opportunities` (`ui_views.py:118`) and `ui_components.savings_opportunity_evidence`/`render_savings_evidence` (`ui_components.py:139,146`) display holdings, gap, deposit evidence, actual G4/G5 reasons, final rating and provenance. `passport_body` (line 89) displays all six gates in Decision Passport.

G5's PASS reason `SUITABILITY_REVIEW_REQUIRED` is not a bank suitability endorsement. Thresholds are prototype assumptions; terms, rates, preferences, balances and segment-specific bank product policies are unavailable. A deposit signal does not prove incremental demand, affordability or revenue. SUPPORTED permits staff review only, never an approved offer, contact or transaction.

### Reproducible examples

Main application: Product Opportunity Intelligence → Supported staff review → inspect the initially selected SUPPORTED customer, then its Savings explanation/Decision Passport. Read-only aggregate verification establishes **all 2,052 SUPPORTED customers have known nonempty existing holdings (2–3 products) and none already holds Savings**. Thus the accepted actionable population does establish additional-product ownership, not merely empty-customer acquisition. There are 40,000 recorded Savings gaps and 12,517 gaps with a deposit rationale; neither total is a count of eligible offers.

Existing synthetic example, not newly invented for this audit: `phase9_demo.synthetic_rows` (`phase9_demo.py:6`) and the stored candidate under `outputs/phase9/browser_verified/private/snapshots/`. `SYNTHETIC-SUPPORTED` already holds Current Account, has five historical cash deposits and no Savings, Active account/customer and Verified KYC; all gates PASS, final SUPPORTED. `SYNTHETIC-CAUTION` has only three deposits: G2 CAUTION, not a sales permission. Snapshot fields/decisions were read, not regenerated or activated. The companion's limited preview shows its Passport; the original main Product page supplies the fuller holdings explanation for its canonical population.

The engine by itself can also evaluate an explicitly empty known portfolio; that case alone would not prove cross-selling. The above existing canonical population and existing synthetic Current Account example supply the required additional-product relationship.

Tests in the accepted 574-case receipt: `tests/test_navigation.py::test_opportunity_view_contains_only_supported_actionable_rows`; `tests/test_product_context.py::test_savings_explanation_is_identical_to_authoritative_gates[...]`; `tests/test_gate_protection.py::test_product_dashboard_cannot_bypass_g4_or_g5[...]`; `tests/test_phase9_ingestion.py::test_engine_priority_gates_and_reasons_are_exactly_reused`; `tests/test_intelligence_views.py::test_product_global_kpis_context_and_selection_are_read_only`.

## Upselling: MISSING

No source-product → upgrade/higher-tier relationship, tier catalogue, increased service-level rule, upgrade eligibility check, upsell reason or actual upsell demonstration was found. Existing product ownership is known, but knowing holdings alone is not an upgrade capability. `engine.evaluate` supports Savings Account only and blocks an already-held product; `UNSUPPORTED_PRODUCT` prevents unrelated product proposals from bypassing G5. The ten-label holdings vocabulary is an ownership parser, not ten implemented recommendations or an upgrade hierarchy.

The absence is corroborated by actual engine/product renderer behavior and repository searches for upsell/upgrade/tier/hierarchy, not inferred solely from missing page titles. There is no dedicated upsell test or saved upsell output. No honest actual upsell example can be supplied.

### Requirement impact and smallest safe action

Official requirement R4 is PARTIAL: the cross-sell component is demonstrated, the explicit upsell component is not. This is the most direct uncovered business capability and a **CRITICAL requirement-coverage gap**, despite the technically accepted Phase 9 build.

Presentation can acknowledge the gap but cannot turn a Savings cross-sell into an upsell. A real fix requires a specified existing product, upgrade/tier relationship, evidence and eligibility/suitability controls, with explicit prototype/bank-approval status. A future isolated analytical demonstration could be additive, but it must not claim operational authorization under the present engine. Operational expansion beyond the current Savings policy would require separately authorized protected-policy changes and regression/gate safeguards. None is performed or authorized by this audit.
