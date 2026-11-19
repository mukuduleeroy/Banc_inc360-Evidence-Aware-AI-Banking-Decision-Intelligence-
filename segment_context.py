"""Source snapshot context only. Never an inference feature or eligibility rule."""
import re
import pandas as pd
from data_access import FEATURE_COLUMNS

BANKING_SEGMENTS=('Retail','SME','Corporate','NGO/NPO','Trust')
UNKNOWN='Unknown'
ORIGIN='Source-provided current snapshot'
EXPLANATION='Membership is supplied by source data, not inferred through clustering or transaction behaviour. Assignment criteria were not supplied.'
_ALIAS=re.compile(r'C-[A-F0-9]{24}')

def _label(value):
    if not isinstance(value,str):return UNKNOWN
    return {s.casefold():s for s in BANKING_SEGMENTS}.get(' '.join(value.split()).casefold(),UNKNOWN)

def _aliases(frame):
    if 'customer' not in frame or frame.customer.duplicated().any() or not frame.customer.map(lambda x:isinstance(x,str) and bool(_ALIAS.fullmatch(x))).all():
        raise ValueError('A unique presentation-safe customer alias is required for every context row.')

def banking_segment_frame(index):
    position=FEATURE_COLUMNS.index('customer_segment')
    frame=pd.DataFrame({'customer':[r.alias for r in index.records],'banking_segment':[_label(r.values[position]) for r in index.records],'segment_origin':[ORIGIN]*len(index.records)})
    _aliases(frame)
    return frame

def selected_banking_segment(index,alias):
    context=banking_segment_frame(index);row=context.loc[context.customer.eq(alias)]
    if len(row)!=1:raise ValueError('Selected presentation alias is unavailable or ambiguous.')
    return {'customer':alias,'banking_segment':row.iloc[0].banking_segment,'origin':ORIGIN,'effective_date':None,'explanation':EXPLANATION,'dataset_sha256':index.dataset_hash,'policy_sha256':index.policy_hash}

def filter_banking_segment(frame,context,selected):
    """One-to-one alias lookup; retain original columns, index, ordering and values."""
    _aliases(frame);_aliases(context)
    if {'customer_id','Customer ID','Account ID','legal_name','national_id_or_registration'} & set(frame.columns):raise ValueError('A privacy-safe analytic frame is required.')
    if 'banking_segment' not in context or not context.banking_segment.isin((*BANKING_SEGMENTS,UNKNOWN)).all():raise ValueError('Banking segment context is not allowlisted.')
    if not frame.customer.isin(context.customer).all():raise ValueError('Analytic rows lack a matching source-segment alias.')
    if selected in ('All','ALL'):return frame.copy(deep=True)
    if selected not in (*BANKING_SEGMENTS,UNKNOWN):raise ValueError('Select a known banking segment, Unknown or All.')
    labels=frame.customer.map(context.set_index('customer').banking_segment)
    return frame.loc[labels.eq(selected)].copy(deep=True)
