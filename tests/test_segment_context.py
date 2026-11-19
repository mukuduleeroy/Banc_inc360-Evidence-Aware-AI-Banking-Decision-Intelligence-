"""Synthetic segment fixtures; source labels never become gate inputs."""
from dataclasses import replace
import json
import pandas as pd
import pytest
from data_access import build_index
from analytics import portfolio_frame
from segment_context import BANKING_SEGMENTS,banking_segment_frame,selected_banking_segment,filter_banking_segment

@pytest.fixture
def index(feature_row):
 rows=[dict(feature_row,customer_id='SYNTHETIC-'+str(i),customer_segment=s) for i,s in enumerate((*BANKING_SEGMENTS,None,'<script>private</script>'))]
 return build_index(pd.DataFrame(rows),b'segment-only-fixture',dataset_hash='a'*64,policy_hash='b'*64)

def test_all_source_labels_and_privacy(index):
 f=banking_segment_frame(index);assert set(f.banking_segment)==set(BANKING_SEGMENTS)|{'Unknown'};assert 'customer_id' not in f and 'customer_segment' not in f;assert 'SYNTHETIC-' not in f.to_json();assert '<script>' not in f.to_json();assert list(f.customer)==[r.alias for r in index.records]

@pytest.mark.parametrize('label,expected',[(' retail ','Retail'),('ngo/npo','NGO/NPO'),('', 'Unknown'),('NGO','Unknown'),(123,'Unknown'),(['Retail'],'Unknown')])
def test_safe_normalization(feature_row,label,expected):
 i=build_index(pd.DataFrame([dict(feature_row,customer_segment=label)]),b'segment');assert banking_segment_frame(i).iloc[0].banking_segment==expected

def test_selected_context_source_and_unknown_date(index):
 c=selected_banking_segment(index,index.records[0].alias);assert c['effective_date'] is None and 'not inferred' in c['explanation'];assert c['dataset_sha256']=='a'*64 and c['policy_sha256']=='b'*64;assert 'SYNTHETIC-' not in json.dumps(c)

def test_filter_preserves_all_values_order_and_input(index):
 f=portfolio_frame(index);before=f.copy(deep=True);c=banking_segment_frame(index);pd.testing.assert_frame_equal(filter_banking_segment(f,c,'All'),f)
 out=filter_banking_segment(f,c,'Retail');expected=f.loc[f.customer.isin(c.loc[c.banking_segment.eq('Retail'),'customer'])];pd.testing.assert_frame_equal(out,expected);pd.testing.assert_frame_equal(f,before);assert list(out.columns)==list(f.columns)

def test_empty_intersection_and_unknown(index):
 f=portfolio_frame(index);c=banking_segment_frame(index);retail=filter_banking_segment(f,c,'Retail');assert filter_banking_segment(retail,c,'Trust').empty;assert len(filter_banking_segment(f,c,'Unknown'))==2

@pytest.mark.parametrize('side',['frame','context'])
def test_duplicate_alias_rejected(index,side):
 f=portfolio_frame(index);c=banking_segment_frame(index)
 if side=='frame':f=pd.concat([f,f.iloc[:1]])
 else:c=pd.concat([c,c.iloc[:1]])
 with pytest.raises(ValueError,match='unique'):filter_banking_segment(f,c,'All')

def test_missing_alias_or_malicious_selection_rejected(index):
 f=portfolio_frame(index);c=banking_segment_frame(index)
 with pytest.raises(ValueError,match='matching'):filter_banking_segment(f,c.iloc[1:],'All')
 with pytest.raises(ValueError,match='Select'):filter_banking_segment(f,c,'<script>')
 with pytest.raises(ValueError):selected_banking_segment(index,'raw-private-id')

def test_metadata_cannot_mutate_analytics_or_decisions(index):
 original=index.table();f=banking_segment_frame(index);f.loc[:,'banking_segment']='Changed';assert 'Changed' not in set(banking_segment_frame(index).banking_segment);assert 'customer_segment' not in portfolio_frame(index);assert index.table().equals(original)

def test_private_frame_and_unallowlisted_context_rejected(index):
 f=portfolio_frame(index);c=banking_segment_frame(index)
 with pytest.raises(ValueError,match='privacy-safe'):filter_banking_segment(f.assign(customer_id='PRIVATE'),c,'All')
 c.loc[0,'banking_segment']='untrusted free text'
 with pytest.raises(ValueError,match='allowlisted'):filter_banking_segment(f,c,'All')
