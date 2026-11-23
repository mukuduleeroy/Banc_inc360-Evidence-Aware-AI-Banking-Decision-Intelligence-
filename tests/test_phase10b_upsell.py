"""Independent synthetic-only higher-tier policy and evidence evaluation."""
from dataclasses import replace
import pytest
from phase10b_upsell import *

@pytest.fixture
def base():return demo_scenarios()[0][1]

def test_registered_higher_tier_relationship_and_review(base):
    assert validate_relationship(UpgradeSpec()).source.tier<UpgradeSpec().target.tier
    r=assess_upsell(base);assert r['assessment']==ELIGIBLE and not r['failed_checks'] and not r['missing_evidence']
    assert r['source_product']==BASE.name and r['target_product']==PREMIUM.name
    assert r['human_review_required'] and r['synthetic'] and not r['bank_approved'] and not r['operational_authorization'] and not r['operational_g5_evaluated']
    assert 'higher-tier' in r['explanation'] and 'not an operational six-gate decision' in r['notice']

@pytest.mark.parametrize('spec',[
 replace(UpgradeSpec(),target=BASE),replace(UpgradeSpec(),source=PREMIUM,target=BASE),
 replace(UpgradeSpec(),target=replace(PREMIUM,tier=1)),replace(UpgradeSpec(),target=replace(PREMIUM,family='Other')),
 replace(UpgradeSpec(),relationship='CROSS_SELL'),replace(UpgradeSpec(),bank_approved=True),replace(UpgradeSpec(),synthetic=False),
 replace(UpgradeSpec(),provenance='bank approved'),replace(UpgradeSpec(),version='unknown'),replace(UpgradeSpec(),required_attributes=('income',)),
 replace(UpgradeSpec(),min_events_180d=0),replace(UpgradeSpec(),min_requests_180d=True),replace(UpgradeSpec(),human_review_required=False),
 replace(UpgradeSpec(),target=replace(PREMIUM,name='BancABC Premium Account')),replace(UpgradeSpec(),target=replace(PREMIUM,product_id='UNKNOWN')),
 replace(UpgradeSpec(),source=replace(BASE,name=None)),replace(UpgradeSpec(),target=replace(PREMIUM,tier=True))])
def test_invalid_relationships_and_assumptions_rejected(base,spec):
    with pytest.raises(ValueError):validate_relationship(spec)
    r=assess_upsell(base,spec);assert r['assessment']==INELIGIBLE and 'DEMO_RELATIONSHIP' in r['failed_checks']

@pytest.mark.parametrize('changes,expected,code',[
 ({'products':(BASE.product_id,PREMIUM.product_id)},INELIGIBLE,'DEMO_TARGET_ABSENT'),
 ({'products':()},INELIGIBLE,'DEMO_SOURCE_OWNERSHIP'),
 ({'products':None,'ownership_verified':None},MISSING,'DEMO_SOURCE_OWNERSHIP'),
 ({'ownership_verified':False},MISSING,'DEMO_SOURCE_OWNERSHIP'),
 ({'events_180d':None},MISSING,'DEMO_ACTIVITY_HISTORY'),({'events_180d':1},MISSING,'DEMO_ACTIVITY_HISTORY'),
 ({'events_180d':True},MISSING,'DEMO_ACTIVITY_HISTORY'),({'events_180d':-1},MISSING,'DEMO_ACTIVITY_HISTORY'),
 ({'expanded_service_requests_180d':0},MISSING,'DEMO_UPGRADE_NEED'),({'expanded_service_requests_180d':float('nan')},MISSING,'DEMO_UPGRADE_NEED'),
 ({'customer_status':'Restricted'},INELIGIBLE,'DEMO_CUSTOMER_STATUS'),({'account_status':'Frozen'},INELIGIBLE,'DEMO_ACCOUNT_STATUS'),
 ({'kyc_status':'Pending'},INELIGIBLE,'DEMO_KYC'),({'kyc_status':None},MISSING,'DEMO_KYC'),
 ({'human_review_required':False},INELIGIBLE,'DEMO_HUMAN_CONTROL'),({'automatic_outreach':True},INELIGIBLE,'DEMO_HUMAN_CONTROL'),
 ({'products':('UNRECOGNIZED',)},MISSING,'DEMO_SOURCE_OWNERSHIP'),({'products':(['invalid'],)},MISSING,'DEMO_SOURCE_OWNERSHIP'),
 ({'products':(BASE.product_id,BASE.product_id)},MISSING,'DEMO_SOURCE_OWNERSHIP')])
def test_missing_blocking_and_eligibility_evidence(base,changes,expected,code):
    r=assess_upsell(replace(base,**changes));assert r['assessment']==expected
    assert code in r['failed_checks']+r['missing_evidence']
    if code=='DEMO_SOURCE_OWNERSHIP':assert 'not established' in r['source_product'] and r['source_product']!=BASE.name

@pytest.mark.parametrize('changes',[{'demo_id':'C-'+'A'*24},{'synthetic':False},{'provenance':'copied real customer'},{'demo_id':None}])
def test_real_or_unverified_identity_never_accepted(base,changes):
    r=assess_upsell(replace(base,**changes));assert r['assessment']==INELIGIBLE and r['customer']=='DEMO-UNVERIFIED'
    assert r['operational_authorization'] is False


def test_restriction_precedes_missing_evidence_and_all_fixtures_separate(base):
    r=assess_upsell(replace(base,kyc_status='Pending',events_180d=None));assert r['assessment']==INELIGIBLE and r['failed_checks'] and r['missing_evidence']
    summary=demo_summary();assert summary['customers']==7 and sum(summary['counts'].values())==7
    assert summary['counts']=={ELIGIBLE:1,MISSING:3,INELIGIBLE:3}
    assert all('Hypothetical' in s.source.name and 'Hypothetical' in s.target.name for _,_,s in demo_scenarios())


def test_does_not_evaluate_original_g5_or_operational_engine(base,monkeypatch):
    import engine
    monkeypatch.setattr(engine,'evaluate',lambda *a:(_ for _ in ()).throw(AssertionError('Operational engine must not assess synthetic upgrades')))
    assert assess_upsell(base)['assessment']==ELIGIBLE
    assert assess_upsell({'customer_id':'REAL'})['assessment']==INELIGIBLE
