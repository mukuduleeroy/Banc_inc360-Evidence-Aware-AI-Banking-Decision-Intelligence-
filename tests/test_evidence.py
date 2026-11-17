import pytest
from engine import Case,evaluate

@pytest.mark.parametrize('field,value',[
 ('account_status',None),('account_status',''),('account_status','Unknown'),('account_status','unfrozen'),
 ('kyc_status',None),('kyc_status',''),('kyc_status','Unknown'),('kyc_status','approved'),
 ('qualifying_events_180d',float('nan')),('qualifying_events_180d',float('inf')),('qualifying_events_180d',-1),('qualifying_events_180d','5'),('qualifying_events_180d',2.5),('qualifying_events_180d',True),
 ('products_held',None),('products_held',''),('products_held','[bad'),('products_held','Savings Account'),('products_held',{}),('products_held',['Savings Account','savings account']),('products_held',[None]),
 ('recency_days',-1),('recency_days',float('inf')),('relationship_activity_percentile',float('nan')),('relationship_activity_percentile',1.01),
 ('service_issue','False'),('human_review_required','True')])
def test_invalid_evidence_fails_closed_with_codes(field,value):
    p=evaluate(Case('SYNTHETIC',**{field:value}))
    assert p['rating']=='ABSTAIN'
    assert p['validation_issues']
    assert p['reason_codes']
    assert all(g['reason_code'] and g['reason'] for g in p['gates'])

@pytest.mark.parametrize('state',['Verified',' verified ','VERIFIED'])
def test_only_unambiguous_status_variants_normalize(state):
    assert evaluate(Case('SYNTHETIC',kyc_status=state))['rating']=='SUPPORTED'

@pytest.mark.parametrize('events,rating',[(1,'ABSTAIN'),(3,'CAUTION'),(5,'SUPPORTED')])
def test_valid_ratings_keep_policy(events,rating):
    assert evaluate(Case('SYNTHETIC',qualifying_events_180d=events))['rating']==rating

@pytest.mark.parametrize('changes',[{'automatic_outreach':True},{'human_review_required':False},{'staff_verification_required':False},{'uses_model_for_action':True,'model_approved':True},{'account_link_valid':False},{'transaction_date_valid':False},{'future_snapshot_as_history':True}])
def test_unauthorized_action_or_invalid_lineage_stays_blocked(changes):
    assert evaluate(Case('SYNTHETIC',**changes))['rating']=='ABSTAIN'

def test_raw_identifier_absent_from_original_evidence():
    p=evaluate(Case('SYNTHETIC-PRIVATE',qualifying_events_180d=float('nan')))
    assert 'SYNTHETIC-PRIVATE' not in str(p['evidence'])
    assert p['evidence']['original_values']['qualifying_events_180d']=='nan'

@pytest.mark.parametrize('products',[['Unknown'],['None'],['N/A'],['not available']])
def test_ambiguous_product_tokens_are_not_empty_ownership(products):
    p=evaluate(Case('SYNTHETIC',products_held=products))
    assert p['rating']=='ABSTAIN' and 'INVALID_HOLDINGS' in p['reason_codes']

@pytest.mark.parametrize('products',[[],(),'[]','()'])
def test_explicit_empty_holdings_are_distinct_from_missing(products):
    assert evaluate(Case('SYNTHETIC',products_held=products))['rating']=='SUPPORTED'

def test_unrepresentable_history_integer_is_withheld_not_crashed():
    p=evaluate(Case('SYNTHETIC',qualifying_events_180d=10**400))
    assert p['rating']=='ABSTAIN' and 'INVALID_QUALIFYING_EVENTS_180D' in p['reason_codes']

def test_unrecognized_portfolio_labels_are_unknown_evidence():
    assert evaluate(Case('SYNTHETIC',products_held=['Unrecognized Holding']))['rating']=='ABSTAIN'

def test_safe_original_portfolio_and_flags_preserved():
    case=Case('SYNTHETIC',products_held="['Current Account']",automatic_outreach=True)
    p=evaluate(case)
    assert p['evidence']['original_values']['products_held']=="['Current Account']"
    assert p['evidence']['original_values']['automatic_outreach'] is True
