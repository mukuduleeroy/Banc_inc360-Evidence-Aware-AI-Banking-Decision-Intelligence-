"""Synthetic unit fixtures test descriptive analytics, not fabricated banking performance."""
import pandas as pd
import pytest
from data_access import build_index
from analytics import portfolio_frame,metrics,distribution,reason_distribution,frequency_band,recency_band,activity_band

@pytest.fixture
def index(feature_row):
    return build_index(pd.DataFrame([feature_row,dict(feature_row,customer_id='SYNTHETIC-2',qualifying_events_180d=3,events_90d=2,relationship_activity_percentile=.2),dict(feature_row,customer_id='SYNTHETIC-3',customer_status='Restricted',relationship_activity_percentile=.9)]),b'synthetic analytics test')

def test_metrics_and_distributions_reconcile(index):
    frame=portfolio_frame(index);m=metrics(index)
    assert m['evaluated']==3 and m['SUPPORTED']==1 and m['CAUTION']==1 and m['ABSTAIN']==1
    for col in ['rating','recency_band','frequency_band','activity_band','savings_gap']:
        assert distribution(frame,col).Customers.sum()==3
    assert m['savings_gap_candidates']==3 and m['savings_gap_with_rationale']==3
    assert 'CURRENT_RESTRICTION' in set(reason_distribution(index)['Reason code'])

def test_privacy_safe_frame_is_detached_from_cache(index):
    frame=portfolio_frame(index)
    assert 'customer_id' not in frame and 'customer_segment' not in frame and 'behavioural_reason' not in frame
    assert all(v.startswith('C-') for v in frame.customer)
    frame.loc[0,'customer']='MUTATED'
    assert 'MUTATED' not in set(portfolio_frame(index).customer)

@pytest.mark.parametrize('value,expected',[(None,'Unavailable'),(0,'0–1 events'),(1,'0–1 events'),(2,'2–3 events'),(3,'2–3 events'),(4,'4+ events')])
def test_frequency_boundaries(value,expected):assert frequency_band(value)==expected

@pytest.mark.parametrize('value,expected',[(None,'Unavailable'),(30,'0–30 days'),(31,'31–60 days'),(60,'31–60 days'),(61,'61–90 days'),(90,'61–90 days'),(91,'>90 days')])
def test_recency_boundaries(value,expected):assert recency_band(value)==expected

@pytest.mark.parametrize('value,expected',[(None,'Unavailable'),(.3999,'Lower activity (<40th)'),(.4,'Middle activity (40th–<80th)'),(.8,'Higher activity (80th+)'),(1,'Higher activity (80th+)')])
def test_activity_segments(value,expected):assert activity_band(value)==expected

def test_invalid_metrics_remain_unavailable(feature_row):
    bad=build_index(pd.DataFrame([dict(feature_row,recency_days=float('nan'),products_held='[bad',relationship_activity_percentile=2)]),b'synthetic')
    frame=portfolio_frame(bad)
    assert frame.iloc[0].recency_band=='Unavailable'
    assert frame.iloc[0].activity_band=='Unavailable'
    assert frame.iloc[0].savings_gap=='Unknown ownership'
    assert metrics(bad)['median_recency_days'] is None
