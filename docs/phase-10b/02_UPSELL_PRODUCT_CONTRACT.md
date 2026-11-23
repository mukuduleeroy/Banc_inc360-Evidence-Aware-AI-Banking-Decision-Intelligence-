# Isolated illustrative upsell product contract

Specification: **hypothetical-package-upgrade-v1**, implemented in `phase10b_upsell.py::UpgradeSpec` and `validate_relationship`. No bank-approved tier evidence exists in the accepted data; this is exclusively a wholly synthetic demonstration.

| Contract item | Explicit definition |
|---|---|
| Existing source | HYP-STANDARD — **Hypothetical Standard Account Package**, tier 1 |
| Upgrade target | HYP-PREMIUM — **Hypothetical Premium Account Package**, tier 2 |
| Family/relationship | Same hypothetical account-package family; UPGRADE_WITHIN_PRODUCT_FAMILY; target tier must be strictly higher |
| Hierarchy | Registered Standard tier 1 → Premium tier 2; no prices, rates, terms, guarantees or actual BancABC product claims |
| Evidence ownership | Independent DEMO-UP-NNN fixture; explicit known hypothetical holdings and synthetic ownership verification |
| Activity evidence | At least four recorded qualifying events in preceding 180 days; count is synthetic, finite nonnegative integer |
| Need evidence | At least two recorded synthetic requests for expanded package features in preceding 180 days |
| Eligibility | Synthetic customer/account Active and KYC Verified; unknown evidence withheld; restrictions block |
| Exclusions | Already-held target; absent source; invalid/same/downgrade/family-mismatched relationship; unsupported specification/assumptions; unverified provenance; restrictions; failed human controls |
| Human control | Human review mandatory, no automatic outreach; there is no approval/save/account-action endpoint |
| Provenance | Independently invented student demonstration; **synthetic=True, bank_approved=False**; no accepted customer aliases or actual ownership rows used |
| Operational scope | No engine Case registration, no Savings-specific G5 evaluation, no review database or Phase 9 registry interaction |

The 4-event/2-request thresholds are explicit illustrative specification assumptions, not BancABC eligibility policy and not a modification to G2/G5. Only the registered version and exact supported attribute set/thresholds are accepted. This is a valid hypothetical upgrade relationship, not evidence that BancABC sells the packages or real customers qualify for them.

## Pure evaluation and outcome separation

`assess_upsell` returns full check names/status/reasons, passed/failed/missing lists, known synthetic evidence, existing verified synthetic product (or unavailable), required source tier, proposed upgrade, explanation, specification version and provenance. It does not invent source ownership when the required tier is known only from the specification.

- **DEMO_ELIGIBLE_FOR_REVIEW**: every illustrative check passes; human review remains required.
- **DEMO_NEEDS_MORE_EVIDENCE**: no explicit blocker, but ownership/history/need/status evidence is missing or below the illustrative evidence requirement.
- **DEMO_NOT_ELIGIBLE**: failed relationship/identity/ownership/restriction/control check. A blocker takes precedence over missing evidence.

These statuses never enter SUPPORTED / CAUTION / ABSTAIN totals or original queue ranking. The old six-gate ABSTAIN/CAUTION precedence is unchanged. Results explicitly expose `operational_authorization=False`, `operational_g5_evaluated=False`, `bank_approved=False` and a synthetic notice.

`validate_relationship` rejects identical IDs/names, downgrade/same tier, cross-family/cross-sell substitution, unregistered products or product facts, unsupported version/provenance, invented eligibility keys, changed thresholds and removed review control. Record admission rejects real C-* aliases and non-synthetic evidence. Known target ownership blocks; unknown/malformed/duplicated holdings never become an empty known portfolio. No external input is deserialized or executed.

## Independent fixture population

`demo_scenarios()` returns seven independent invented records and immutable specifications:

1. Eligible Standard → Premium review: eight synthetic events, three recorded synthetic expanded-service requests, known source/absent target, Active/Verified checks.
2. Already holds target: not eligible.
3. Missing activity evidence: needs more evidence.
4. Restricted synthetic customer: not eligible.
5. Unverified source ownership: needs more evidence; displayed existing ownership remains unavailable.
6. Invalid source=target relationship: not eligible.
7. One historical event: insufficient activity evidence, needs more evidence.

Denominator **7**, with **1 DEMO_ELIGIBLE_FOR_REVIEW / 3 DEMO_NEEDS_MORE_EVIDENCE / 3 DEMO_NOT_ELIGIBLE**. This denominator is never merged with 50,000 original customers or 2,052 operational staff-review cases. Fixtures are code-defined and read no source dataset. No hypothetical product tier is attached to a real customer.
