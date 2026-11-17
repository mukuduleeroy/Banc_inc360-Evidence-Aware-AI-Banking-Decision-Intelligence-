"""Six deterministic gates; SUPPORTED is permission for staff review only."""
from dataclasses import dataclass, asdict
from evidence import validate, safe_original, issue

POLICY_VERSION = 'phase2-1'

@dataclass
class Case:
    customer_id: str
    account_link_valid: bool = True
    transaction_date_valid: bool = True
    future_snapshot_as_history: bool = False
    qualifying_events_180d: int = 5
    model_approved: bool = False
    uses_model_for_action: bool = False
    customer_status: str = 'Active'
    account_status: str = 'Active'
    kyc_status: str = 'Verified'
    proposed_product: str = 'Savings Account'
    products_held: tuple = ()
    behavioural_reason: str = 'Repeated qualifying deposits'
    staff_verification_required: bool = True
    automatic_outreach: bool = False
    human_review_required: bool = True
    recency_days: int = 45
    relationship_activity_percentile: float = .70
    service_issue: bool = False
    validation_issues: tuple = ()

def evaluate(case):
    original = asdict(case)
    v, issues = validate(original)
    issues.extend(case.validation_issues)
    if case.account_link_valid is not True:
        issues.append(issue('G1', 'INVALID_OWNERSHIP', 'Account ownership linkage is not verified.'))
    if case.transaction_date_valid is not True or case.future_snapshot_as_history is not False:
        issues.append(issue('G1', 'INVALID_TEMPORAL_EVIDENCE', 'Dates are invalid or future snapshots were used as historical evidence.'))
    gates = []
    def add(prefix, name, status, code, reason):
        failures = [i for i in issues if i['gate'] == prefix]
        if failures:
            gates.append({'gate': name, 'status': 'ABSTAIN', 'reason_code': failures[0]['code'], 'reason_codes': [i['code'] for i in failures], 'reason': ' '.join(i['message'] for i in failures)})
        else:
            gates.append({'gate': name, 'status': status, 'reason_code': code, 'reason_codes': [code], 'reason': reason})
    add('G1', 'G1 Integrity', 'PASS', 'INTEGRITY_VALID', 'Identifiers, typed evidence and supplied linkage/temporal checks are valid.')
    n = v['qualifying_events_180d']
    history_status = 'ABSTAIN' if n is None or n <= 1 else 'CAUTION' if n <= 3 else 'PASS'
    add('G2', 'G2 History', history_status, 'HISTORY_INSUFFICIENT' if history_status == 'ABSTAIN' else 'HISTORY_BORDERLINE' if history_status == 'CAUTION' else 'HISTORY_SUFFICIENT', f'{n} qualifying events in preceding 180 days.' if n is not None else 'History is unavailable.')
    # No fitted method has approval in this prototype; a caller boolean cannot approve one.
    uses_model = case.uses_model_for_action is not False
    add('G3', 'G3 Model reliability', 'ABSTAIN' if uses_model else 'PASS', 'MODEL_NOT_APPROVED' if uses_model else 'APPROVED_RULE_METHOD', 'No model is registered for operational action.' if uses_model else 'Versioned deterministic rules; no model used.')
    restricted = v['customer_status'] != 'Active' or v['account_status'] != 'Active' or v['kyc_status'] != 'Verified'
    add('G4', 'G4 Current status', 'ABSTAIN' if restricted else 'PASS', 'CURRENT_RESTRICTION' if restricted else 'CURRENT_CHECKS_PASSED', 'Sales blocked by current customer/account state or KYC.' if restricted else 'Current Active account/customer and Verified KYC; snapshots are not historical predictors.')
    products = v['products_held']
    held = products is not None and isinstance(case.proposed_product, str) and case.proposed_product.casefold() in {p.casefold() for p in products}
    reason = v['behavioural_reason']
    supported_product = case.proposed_product == 'Savings Account'
    blocked = held or not reason.strip() or not supported_product or products is None
    code = 'UNSUPPORTED_PRODUCT' if not supported_product else 'PRODUCT_ALREADY_HELD' if held else 'NO_BEHAVIOURAL_EVIDENCE' if not reason.strip() else 'SUITABILITY_REVIEW_REQUIRED'
    add('G5', 'G5 Product suitability', 'ABSTAIN' if blocked else 'PASS', code, 'Product is unsupported, already held, or lacks usable behavioural/ownership evidence.' if blocked else 'Observed product gap and behavioural rationale; staff must verify suitability.')
    human_failed = case.automatic_outreach is not False or case.human_review_required is not True or case.staff_verification_required is not True
    add('G6', 'G6 Human control', 'ABSTAIN' if human_failed else 'PASS', 'UNAUTHORIZED_ACTION' if human_failed else 'HUMAN_REVIEW_REQUIRED', 'Automatic or unreviewed action prohibited.' if human_failed else 'Staff review and logged decision required; no automated outreach or financial approval.')
    rating = 'ABSTAIN' if any(g['status'] == 'ABSTAIN' for g in gates) else 'CAUTION' if any(g['status'] == 'CAUTION' for g in gates) else 'SUPPORTED'
    score = .45 * min((v['recency_days'] or 0) / 90, 1) + .35 * (v['relationship_activity_percentile'] or 0) + .2 * int(case.service_issue is True)
    return {'customer_id': case.customer_id, 'rating': rating, 'action': 'Withhold sales offer; investigate' if rating == 'ABSTAIN' else 'Manual investigation required' if rating == 'CAUTION' else 'Eligible for staff review only', 'priority': round(score, 3), 'priority_score': score, 'gates': gates, 'reason_codes': [code for g in gates if g['status'] != 'PASS' for code in g['reason_codes']], 'validation_issues': issues, 'policy_version': POLICY_VERSION, 'evidence': {'recency_days': v['recency_days'], 'events_180d': n, 'relationship_activity_percentile': v['relationship_activity_percentile'], 'behavioural_reason': reason, 'product_gap': None if products is None else not held, 'product': case.proposed_product, 'original_values': safe_original(original)}, 'human_review_required': True}

DEMO_CASES = [
    Case('DEMO-001', qualifying_events_180d=8, recency_days=65, relationship_activity_percentile=.87),
    Case('DEMO-002', kyc_status='Pending', qualifying_events_180d=7, recency_days=80),
    Case('DEMO-003', qualifying_events_180d=1),
    Case('DEMO-004', products_held=('Savings Account',)),
    Case('DEMO-005', qualifying_events_180d=3),
    Case('DEMO-006', customer_status='Restricted'),
    Case('DEMO-007', account_link_valid=False),
    Case('DEMO-008', uses_model_for_action=True, model_approved=False),
    Case('DEMO-009', automatic_outreach=True),
]
