"""Descriptive, privacy-safe analytics over the authoritative Phase 2 index.
No predictions, profit estimates or new permission rules are implemented here.
"""
from collections import Counter
from functools import lru_cache
import math
import pandas as pd
from data_access import FEATURE_COLUMNS
from evidence import number, holdings, state, ACCOUNT_STATES, CUSTOMER_STATES, KYC_STATES

NUMERIC = {'qualifying_events_180d':True,'events_90d':True,'recency_days':True,'transaction_volume_180d_usd':False,'deposit_events_180d':True,'account_count':True,'relationship_activity_percentile':False}

def numeric(value, integer=False, percentile=False):
    # CSV numbers may have object dtype if a different row is corrupt.
    if isinstance(value,str):
        try:value=float(value)
        except ValueError:return None
    return number(value,integer,1 if percentile else None)

def frequency_band(value):
    if value is None or pd.isna(value):return 'Unavailable'
    return '0–1 events' if value<=1 else '2–3 events' if value<=3 else '4+ events'

def recency_band(value):
    if value is None or pd.isna(value):return 'Unavailable'
    return '0–30 days' if value<=30 else '31–60 days' if value<=60 else '61–90 days' if value<=90 else '>90 days'

def activity_band(value):
    if value is None or pd.isna(value):return 'Unavailable'
    return 'Lower activity (<40th)' if value<.4 else 'Middle activity (40th–<80th)' if value<.8 else 'Higher activity (80th+)'

@lru_cache(maxsize=2)
def _frame(index):
    values=pd.DataFrame([r.values for r in index.records],columns=FEATURE_COLUMNS)
    # Raw customer IDs and unrestricted free text never enter the public analytics frame.
    frame=pd.DataFrame({'customer':[r.alias for r in index.records],'rating':[r.rating for r in index.records],'priority':[round(r.priority,3) for r in index.records],'invalid_evidence':[r.invalid for r in index.records]})
    for col,integer in NUMERIC.items():
        frame[col]=values[col].map(lambda v:numeric(v,integer,col=='relationship_activity_percentile'))
    for col,allowed in [('customer_status',CUSTOMER_STATES),('account_status',ACCOUNT_STATES),('kyc_status',KYC_STATES)]:
        frame[col]=values[col].map(lambda v:state(v,allowed) or 'Unavailable')
    portfolios=values.products_held.map(holdings)
    frame['products']=portfolios
    frame['product_breadth']=portfolios.map(lambda p:len(p) if p is not None else None)
    frame['savings_gap']=portfolios.map(lambda p:'Unknown ownership' if p is None else 'Already held' if 'Savings Account' in p else 'Gap recorded')
    frame['has_deposit_rationale']=values.behavioural_reason.map(lambda v:isinstance(v,str) and bool(v.strip()))
    frame['frequency_band']=frame.qualifying_events_180d.map(frequency_band)
    frame['recency_band']=frame.recency_days.map(recency_band)
    frame['activity_band']=frame.relationship_activity_percentile.map(activity_band)
    return frame

def portfolio_frame(index):
    return _frame(index).copy(deep=True)

def distribution(frame,column,label='Category'):
    return frame[column].fillna('Unavailable').value_counts(sort=False).rename_axis(label).reset_index(name='Customers')

def reason_distribution(index):
    counts=Counter(code for r in index.records if r.rating=='ABSTAIN' for code in set(r.reason_codes))
    return pd.DataFrame([{'Reason code':code,'Customers':n} for code,n in sorted(counts.items(),key=lambda v:(-v[1],v[0]))],columns=['Reason code','Customers'])

def metrics(index):
    frame=portfolio_frame(index)
    return {'evaluated':len(index.records),'input_rows':index.input_rows,'excluded':len(index.exclusions),'invalid':index.invalid_records,**index.counts,'observed_recency_gt90':int((frame.recency_days>90).sum()),'history_4plus':int((frame.qualifying_events_180d>=4).sum()),'savings_gap_candidates':int((frame.savings_gap=='Gap recorded').sum()),'savings_gap_with_rationale':int(((frame.savings_gap=='Gap recorded')&frame.has_deposit_rationale).sum()),'median_recency_days':float(frame.recency_days.median()) if frame.recency_days.notna().any() else None,'median_events_180d':float(frame.qualifying_events_180d.median()) if frame.qualifying_events_180d.notna().any() else None,'median_activity_percentile':float(frame.relationship_activity_percentile.median()) if frame.relationship_activity_percentile.notna().any() else None,'median_product_breadth':float(frame.product_breadth.median()) if frame.product_breadth.notna().any() else None}
