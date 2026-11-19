"""Mandatory acceptance: controlled synthetic attacks plus authorized local reconciliation."""
from dataclasses import replace
from itertools import product
from pathlib import Path
import json
import pandas as pd
import pytest
from engine import Case,evaluate
from data_access import build_index,load_index
from analytics import portfolio_frame,metrics
from audit_store import AuditStore,AuditError
from review_service import ReviewService,CurrentEvidence
from replay import simulate
from acceptance_checks import ROOT,verify_local_baseline,sha256,decision_fingerprint

# Independent policy expectations. No gate thresholds or outcomes are changed by these tests.
BLOCKERS={
 'G1':({'account_link_valid':False},'INVALID_OWNERSHIP'),
 'G3':({'uses_model_for_action':True,'model_approved':True},'MODEL_NOT_APPROVED'),
 'G4':({'kyc_status':'Pending'},'CURRENT_RESTRICTION'),
 'G5':({'products_held':('Savings Account',)},'PRODUCT_ALREADY_HELD'),
 'G6':({'automatic_outreach':True},'UNAUTHORIZED_ACTION'),
}
MASKS=list(product((False,True),repeat=5))
MASK_IDS=['+'.join(g for g,b in zip(BLOCKERS,bits) if b) or 'no-other-blocks' for bits in MASKS]

@pytest.mark.parametrize('bits',MASKS,ids=MASK_IDS)
@pytest.mark.parametrize('events,history_status,history_code',[(5,'PASS','HISTORY_SUFFICIENT'),(3,'CAUTION','HISTORY_BORDERLINE'),(1,'ABSTAIN','HISTORY_INSUFFICIENT')],ids=['history-pass','history-caution','history-abstain'])
def test_all_gate_combinations_preserve_authority(bits,events,history_status,history_code):
 changes={'qualifying_events_180d':events,'recency_days':90,'relationship_activity_percentile':1.,'service_issue':True}
 blocked={}
 for (gate,(change,code)),enabled in zip(BLOCKERS.items(),bits):
  if enabled:changes.update(change);blocked[gate]=code
 p=evaluate(Case('SYNTHETIC-GATE-MATRIX',**changes));gates={g['gate'].split()[0]:g for g in p['gates']}
 assert list(gates)==['G1','G2','G3','G4','G5','G6']
 for gate in BLOCKERS:
  assert gates[gate]['status']==('ABSTAIN' if gate in blocked else 'PASS')
  if gate in blocked:assert blocked[gate] in gates[gate]['reason_codes']
 assert gates['G2']['status']==history_status and history_code in gates['G2']['reason_codes']
 expected='ABSTAIN' if blocked or history_status=='ABSTAIN' else 'CAUTION' if history_status=='CAUTION' else 'SUPPORTED'
 assert p['rating']==expected;assert p['human_review_required'] is True
 for g in gates.values():assert g['reason'].strip() and g['reason_codes'] and g['reason_code'] in g['reason_codes']
 assert set(p['reason_codes'])=={c for g in gates.values() if g['status']!='PASS' for c in g['reason_codes']}
 assert p['action']=={'SUPPORTED':'Eligible for staff review only','CAUTION':'Manual investigation required','ABSTAIN':'Withhold sales offer; investigate'}[expected]

@pytest.mark.parametrize('restriction',[{'customer_status':'Restricted'},{'customer_status':'Dormant'},{'account_status':'Frozen'},{'account_status':'Dormant'},{'kyc_status':'Pending'},{'kyc_status':'Review Due'}],ids=['restricted-customer','dormant-customer','frozen-account','dormant-account','pending-kyc','review-due-kyc'])
@pytest.mark.parametrize('suitability',['candidate','already-held','no-rationale'])
def test_product_dashboard_cannot_bypass_g4_or_g5(feature_row,restriction,suitability):
 row=dict(feature_row,**restriction,recency_days=90,relationship_activity_percentile=1.,service_issue=True)
 if suitability=='already-held':row.update(products_held="['Savings Account']",product_gap=False)
 if suitability=='no-rationale':row['behavioural_reason']=''
 index=build_index(pd.DataFrame([row]),b'synthetic gate protection');assert index.counts=={'SUPPORTED':0,'CAUTION':0,'ABSTAIN':1};assert index.table('SUPPORTED').empty
 frame=portfolio_frame(index);assert set(frame.rating)=={'ABSTAIN'} and metrics(index)['SUPPORTED']==0
 p=index.passport(index.records[0].alias);g={v['gate'].split()[0]:v for v in p['gates']};assert g['G4']['status']=='ABSTAIN'
 if suitability!='candidate':assert g['G5']['status']=='ABSTAIN'
 assert 'CURRENT_RESTRICTION' in p['reason_codes']


def test_experimental_columns_do_not_become_operational_authority(feature_row):
 frame=pd.DataFrame([feature_row,dict(feature_row,customer_id='SYNTHETIC-BLOCKED',kyc_status='Pending')]);original=build_index(frame,b'synthetic offline model separation')
 attacked=frame.assign(experimental_inactivity_probability=1.,predicted_product_acceptance=1.,recommended_product='Loan',model_approved=True,segment_override='high-value',priority_override=999999)
 attempted=build_index(attacked,b'synthetic offline model separation');assert attempted.table().equals(original.table());assert decision_fingerprint(attempted)==decision_fingerprint(original)
 # A caller that explicitly requests any fitted method is still blocked, even if it claims approval.
 p=evaluate(Case('SYNTHETIC',uses_model_for_action=True,model_approved=True));assert p['rating']=='ABSTAIN';assert 'MODEL_NOT_APPROVED' in p['reason_codes']

FORGERIES=[('G1',dict(account_link_valid=False)),('G2',dict(qualifying_events_180d=1)),('G2-caution',dict(qualifying_events_180d=3)),('G3',dict(uses_model_for_action=True,model_approved=True)),('G4',dict(kyc_status='Pending')),('G5',dict(products_held=('Savings Account',))),('G6',dict(human_review_required=False))]

@pytest.mark.parametrize('gate,changes',FORGERIES,ids=[x[0] for x in FORGERIES])
def test_forged_supported_rating_cannot_create_review(tmp_path,gate,changes):
 alias='C-'+'A'*24;p=evaluate(Case('SYNTHETIC-FORGERY',**changes));assert p['rating']!='SUPPORTED';p['customer_id']=alias;p['rating']='SUPPORTED'
 context=CurrentEvidence(alias,p,'a'*64,'b'*64,'c'*64,'d'*64,'2026-07-01');store=AuditStore(tmp_path/'forged.sqlite3');service=ReviewService(store,provider=lambda requested:context)
 with pytest.raises(AuditError) as error:service.open_case(alias,'DEMO-RM-01','forged-open')
 assert error.value.code=='INVALID_PASSPORT';assert store.summary()['events']==0 and store.summary()['cases']==0


def test_whole_real_population_matches_frozen_reference():
 if not (ROOT/'outputs/customer_features.csv').exists():pytest.skip('Authorized local competition data absent; full-data final acceptance must not be claimed.')
 result=verify_local_baseline();assert result['full_population_decisions_unchanged']


def test_real_replay_reset_never_changes_canonical_or_audit(tmp_path):
 source=ROOT/'outputs/customer_features.csv'
 if not source.exists():pytest.skip('Authorized local competition data absent; real replay acceptance unavailable.')
 before=sha256(source);index=load_index(source);signature=decision_fingerprint(index);alias=next(r.alias for r in index.records if r.rating=='SUPPORTED');store=AuditStore(tmp_path/'replay-isolated.sqlite3');baseline=index.passport(alias)
 for override in ({'kyc_status':'Pending'},{'account_status':'Frozen'},{'products_held':('Savings Account',)}):
  result=simulate(index,alias,override);assert result['baseline']==baseline;assert result['simulated']['rating']=='ABSTAIN';assert result['simulated']['simulated'] is True and result['simulated']['action_authorized'] is False
  reset=simulate(index,alias);assert reset['baseline']==baseline and reset['simulated']['rating']=='SUPPORTED' and reset['modified_fields']==();assert reset['simulated']['action_authorized'] is False
 assert sha256(source)==before and decision_fingerprint(index)==signature;assert store.summary()['events']==0
