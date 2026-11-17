import pandas as pd
import pytest
from data_access import build_index
from replay import simulate

@pytest.fixture
def index(feature_row):return build_index(pd.DataFrame([feature_row]),b'synthetic replay test')

def test_no_override_and_reset_match_authoritative_baseline(index):
    alias=index.records[0].alias
    before=index.passport(alias)
    original=index.customer_values(alias)
    base=simulate(index,alias)
    assert base['changed_gates']==[] and base['baseline']['gates']==base['simulated']['gates']==before['gates']
    assert simulate(index,alias,{'kyc_status':'Pending'})['simulated']['rating']=='ABSTAIN'
    reset=simulate(index,alias)
    assert reset['simulated']['rating']==before['rating']
    assert original==index.customer_values(alias) and index.passport(alias)==before

@pytest.mark.parametrize('overrides,expected_gate',[({'kyc_status':'Pending'},'G4'),({'account_status':'Frozen'},'G4'),({'qualifying_events_180d':1},'G2'),({'products_held':['Savings Account']},'G5')])
def test_changes_go_through_engine(index,overrides,expected_gate):
    result=simulate(index,index.records[0].alias,overrides)
    assert result['simulated']['rating']=='ABSTAIN'
    assert any(g['Gate'].startswith(expected_gate) for g in result['changed_gates'])
    assert index.counts['SUPPORTED']==1

@pytest.mark.parametrize('overrides',[{'products_held':'[bad'},{'qualifying_events_180d':float('nan')},{'account_status':None},{'kyc_status':'Unknown'}])
def test_invalid_simulation_fails_closed(index,overrides):
    result=simulate(index,index.records[0].alias,overrides)
    assert result['simulated']['rating']=='ABSTAIN' and result['simulated']['validation_issues']

@pytest.mark.parametrize('field',['customer_id','validation_issues','automatic_outreach','model_approved','human_review_required'])
def test_unauthorized_override_fields_rejected(index,field):
    with pytest.raises(ValueError,match='UNSUPPORTED_SIMULATION_FIELD'):simulate(index,index.records[0].alias,{field:True})

def test_simulation_cannot_erase_lineage_failure(feature_row):
    issue={'gate':'G1','code':'MISSING_LINEAGE','message':'Synthetic missing lineage'}
    index=build_index(pd.DataFrame([feature_row]),b'synthetic',(issue,))
    result=simulate(index,index.records[0].alias,{'kyc_status':'Verified','products_held':[]})
    assert result['simulated']['rating']=='ABSTAIN'
    assert 'MISSING_LINEAGE' in result['simulated']['reason_codes']

def test_even_supported_simulation_never_authorizes_an_action(index):
    result=simulate(index,index.records[0].alias)
    assert result['simulated']['rating']=='SUPPORTED'
    assert result['simulated']['simulated'] is True
    assert result['simulated']['action_authorized'] is False
