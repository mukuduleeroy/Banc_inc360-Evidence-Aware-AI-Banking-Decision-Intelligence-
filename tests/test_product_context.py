"""Savings explanations consume the existing engine; no new policies or actions."""
import json
import pandas as pd
import pytest
from data_access import build_index
from ui_components import savings_opportunity_evidence

@pytest.mark.parametrize('changes',[{}, {'kyc_status':'Pending'}, {'account_status':'Frozen'}, {'products_held':"['Savings Account']",'product_gap':False}, {'behavioural_reason':''},{'qualifying_events_180d':3,'events_90d':2},{'products_held':'malformed','product_gap':None}],ids=['supported','kyc','frozen','held','no-rationale','caution','unknown-holdings'])
def test_savings_explanation_is_identical_to_authoritative_gates(feature_row,changes):
 i=build_index(pd.DataFrame([dict(feature_row,**changes)]),b'savings-context',dataset_hash='a'*64,policy_hash='b'*64,cutoff='2026-07-01');alias=i.records[0].alias;p=i.passport(alias);e=savings_opportunity_evidence(i,alias);assert e['rating']==p['rating'] and e['gates']==[g for g in p['gates'] if g['gate'].startswith(('G4','G5'))];assert e['savings_gap']==p['evidence']['product_gap'];assert e['dataset_sha256']=='a'*64 and e['policy_sha256']=='b'*64;assert e['snapshot_effective_date'] is None;assert 'SYNTHETIC-1' not in json.dumps(e)

def test_segment_and_experimental_scores_do_not_change_explanation_or_queue(feature_row):
 original=build_index(pd.DataFrame([feature_row]),b'context');altered=build_index(pd.DataFrame([dict(feature_row,customer_segment='Corporate',predicted_acceptance=.999,model_score=100)]),b'context');assert original.table().equals(altered.table());a=savings_opportunity_evidence(original,original.records[0].alias);b=savings_opportunity_evidence(altered,altered.records[0].alias);assert a==b
