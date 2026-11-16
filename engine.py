from dataclasses import dataclass, asdict
from datetime import date

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
    relationship_activity_percentile: float = 0.70
    service_issue: bool = False

def evaluate(case: Case):
    gates=[]
    def add(name,status,reason): gates.append({'gate':name,'status':status,'reason':reason})
    if not str(case.customer_id or '').strip() or str(case.customer_id).strip().lower() in ('nan','none') or not case.account_link_valid or not case.transaction_date_valid or case.future_snapshot_as_history:
        add('G1 Integrity','ABSTAIN','Invalid linkage/date or future snapshot used as historical evidence')
    else: add('G1 Integrity','PASS','Historical identifiers and dates valid')
    n=case.qualifying_events_180d
    add('G2 History','ABSTAIN' if n<=1 else 'CAUTION' if n<=3 else 'PASS',f'{n} qualifying events in preceding 180 days')
    if case.uses_model_for_action and not case.model_approved:
        add('G3 Model reliability','ABSTAIN','Model not approved; cannot drive ranking or product offers')
    else: add('G3 Model reliability','PASS','Rule-based action; unapproved model not used')
    restricted=(case.customer_status!='Active' or case.account_status in ('Frozen','Dormant') or case.kyc_status!='Verified')
    add('G4 Current status','ABSTAIN' if restricted else 'PASS','Sales blocked: customer/account restriction or unverified KYC' if restricted else 'Current account and KYC checks passed (not used for historical prediction)')
    held=case.proposed_product in case.products_held
    no_reason=not case.behavioural_reason.strip()
    unsupported=case.proposed_product != 'Savings Account'
    add('G5 Product suitability','ABSTAIN' if held or no_reason or unsupported else 'PASS','Unsupported product: no validated suitability policy' if unsupported else 'Product already held' if held else 'No behavioural evidence for product discussion' if no_reason else 'Product gap and observed behavioural reason; staff must verify suitability')
    human_failed=case.automatic_outreach or not case.human_review_required or not case.staff_verification_required
    add('G6 Human control','ABSTAIN' if human_failed else 'PASS','Automatic/unreviewed action prohibited' if human_failed else 'Staff review and logged decision required; no automated outreach')
    rating='ABSTAIN' if any(g['status']=='ABSTAIN' for g in gates) else 'CAUTION' if any(g['status']=='CAUTION' for g in gates) else 'SUPPORTED'
    priority=round(0.45*min(case.recency_days/90,1)+0.35*case.relationship_activity_percentile+0.2*int(case.service_issue),3)
    return {'customer_id':case.customer_id,'rating':rating,'action':'Withhold sales offer; investigate' if rating=='ABSTAIN' else 'Manual investigation required' if rating=='CAUTION' else 'Eligible for staff review only','priority':priority,'gates':gates,'evidence':{'recency_days':case.recency_days,'events_180d':n,'behavioural_reason':case.behavioural_reason,'product_gap':case.proposed_product not in case.products_held,'product':case.proposed_product},'human_review_required':True}

DEMO_CASES=[
    Case('DEMO-001',qualifying_events_180d=8,recency_days=65,relationship_activity_percentile=.87),
    Case('DEMO-002',kyc_status='Pending',qualifying_events_180d=7,recency_days=80),
    Case('DEMO-003',qualifying_events_180d=1),
    Case('DEMO-004',products_held=('Savings Account',)),
    Case('DEMO-005',qualifying_events_180d=3),
    Case('DEMO-006',customer_status='Restricted'),
    Case('DEMO-007',account_link_valid=False),
    Case('DEMO-008',uses_model_for_action=True,model_approved=False),
    Case('DEMO-009',automatic_outreach=True),
]
