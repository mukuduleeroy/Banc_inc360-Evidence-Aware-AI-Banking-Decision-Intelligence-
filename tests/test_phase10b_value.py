"""Read-only activity proxy boundary, explainability and original rank preservation."""
from pathlib import Path
import hashlib
import pandas as pd
import pytest
from data_access import build_index,FEATURE_COLUMNS
from analytics import portfolio_frame
from acceptance_checks import decision_fingerprint
from segment_context import banking_segment_frame,filter_banking_segment
from phase10b_value import *

@pytest.fixture
def index(feature_row):
    rows=[{**feature_row,'customer_id':'SYNTHETIC-VALUE-'+str(n),'relationship_activity_percentile':p,'customer_segment':s} for n,(p,s) in enumerate(((.7999,'Retail'),(.8,'SME'),(1.,'Trust')))]
    return build_index(pd.DataFrame(rows),b'v'*32,dataset_hash='a'*64,policy_hash='b'*64,cutoff='2026-07-01')

@pytest.mark.parametrize('p,volume,cutoff,expected',[
 (.7999,100,'2026-07-01',OTHER),(.8,100,'2026-07-01',HIGH),(1.,0,'2026-07-01',HIGH),
 (None,100,'2026-07-01',UNAVAILABLE),(float('nan'),100,'2026-07-01',UNAVAILABLE),
 (1.1,100,'2026-07-01',UNAVAILABLE),(True,100,'2026-07-01',UNAVAILABLE),
 (.9,None,'2026-07-01',UNAVAILABLE),(.9,-1,'2026-07-01',UNAVAILABLE),
 (.9,100,'unknown',UNAVAILABLE),(.9,100,'2026-02-31',UNAVAILABLE),(.9,100,'01/07/2026',UNAVAILABLE)])
def test_boundary_missing_evidence_and_no_imputation(p,volume,cutoff,expected):assert classify_activity(p,volume,cutoff)==expected


def test_existing_percentiles_bands_order_and_decisions_are_unchanged(index):
    original=portfolio_frame(index);before=decision_fingerprint(index);frame=value_frame(index)
    pd.testing.assert_frame_equal(frame[list(original.columns)],original)
    assert frame.customer.tolist()==[r.alias for r in index.records]
    assert set(frame.columns)-set(original.columns)=={'banking_segment','value_proxy_classification'}
    assert decision_fingerprint(index)==before
    frame.loc[:,'relationship_activity_percentile']=0
    pd.testing.assert_frame_equal(portfolio_frame(index),original)


def test_window_segment_denominator_and_explanation(index):
    frame=value_frame(index);r=frame.loc[frame.banking_segment.eq('SME')].iloc[0];e=selected_value_explanation(index,r.customer)
    assert e['global_activity_percentile']==.8 and e['classification']==HIGH and e['original_activity_band']=='Higher activity (80th+)'
    assert e['observation_window']=={'start_inclusive':'2026-01-02','end_exclusive':'2026-07-01','days':180}
    assert e['ranking_population']==3 and e['source_segment_effective_date'] is None
    assert e['limitation']==LIMITATION and e['operational_permission'] is False
    assert '>=80th' in e['explanation'] and e['known_product_breadth']==0
    sub=filter_banking_segment(frame,banking_segment_frame(index),'SME')
    assert sub.iloc[0].relationship_activity_percentile==.8 and len(sub)==1
    assert value_reconciliation(index)['global_ranking_denominator']==3


def test_reconciliation_and_unknown_segment_are_explicit(index):
    r=value_reconciliation(index);assert r['reconciled'] and r['existing_higher_activity_band']==2 and r['classifications'][HIGH]==2 and r['classifications'][OTHER]==1
    with pytest.raises(ValueError):selected_value_explanation(index,'C-'+'F'*24)
    assert observation_window(None) is None


def test_unverified_lineage_rejected_and_no_canonical_contract_expansion(index):
    from dataclasses import replace
    with pytest.raises(ValueError):value_frame(replace(index,lineage_errors_json='[{"code":"STALE"}]'))
    assert len(FEATURE_COLUMNS)==16


def test_actual_population_classification_reconciles_without_rerank():
    ix=load_accepted_index();before=decision_fingerprint(ix);original=portfolio_frame(ix);frame=value_frame(ix);r=value_reconciliation(ix)
    pd.testing.assert_frame_equal(frame[list(original.columns)],original)
    assert r['customers']==50000 and r['existing_higher_activity_band']==10003 and r['classifications'][HIGH]==10003 and r['unavailable_evidence']==0 and r['reconciled']
    assert decision_fingerprint(ix)==before
    assert set(frame.banking_segment)=={'Retail','SME','Corporate','NGO/NPO','Trust'}
