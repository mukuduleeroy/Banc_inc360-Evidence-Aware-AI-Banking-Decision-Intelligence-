"""Banc-Inc360 local review application; historical analytics and current-state checks separated."""
from pathlib import Path
from datetime import datetime,timezone
import streamlit as st
import pandas as pd
import os
from engine import Case,evaluate,DEMO_CASES
st.set_page_config(page_title='Banc-Inc360 | Decision Passport',layout='wide')
st.title('Banc-Inc360 | Evidence-Aware Decision Intelligence')
st.caption('Prototype: human review only • no automated sales, credit or insurance decisions')
if 'audit' not in st.session_state: st.session_state.audit=[]
path=Path(os.environ.get('BANCINC_FEATURES_PATH', str(Path(__file__).parent/'outputs/customer_features.csv'))).expanduser()
if not path.is_file():
    st.warning('Customer features not found. Set BANCINC_FEATURES_PATH or rebuild with build_data.py. Synthetic demonstrations remain available.')
with st.sidebar:
    st.header('DecisionLab')
    mode=st.radio('Data source',['BancABC historical extract','Synthetic gate demonstrations'] if path.exists() else ['Synthetic gate demonstrations'])
    capacity=st.slider('Review capacity',25,50,25)
    st.caption('Priority = 45% recency + 35% relationship activity percentile + 20% service issue. Illustrative triage, not uplift.')
if mode=='BancABC historical extract':
    @st.cache_data
    def load():return pd.read_csv(path,dtype={'customer_id':str}).fillna({'recency_days':999,'behavioural_reason':'','customer_status':'','account_status':'','kyc_status':''})
    try:
        df=load()
        required={'customer_id','recency_days','qualifying_events_180d','relationship_activity_percentile','service_issue','products_held','behavioural_reason','customer_status','account_status','kyc_status'}
        if not required.issubset(df.columns):
            st.error('Customer feature file is missing required columns. Rebuild it with build_data.py.');st.stop()
    except (OSError,ValueError,pd.errors.ParserError) as exc:
        st.error('Cannot read customer features. Check BANCINC_FEATURES_PATH and rebuild the file.');st.stop()
    df['priority_sort']=.45*(df['recency_days']/90).clip(0,1)+.35*df['relationship_activity_percentile']+.2*df['service_issue'].astype(int)
    candidates=df.sort_values('priority_sort',ascending=False)
    search=st.text_input('Filter customer ID (masked in presentation)',placeholder='Enter customer ID')
    if search:candidates=candidates[candidates['customer_id'].str.contains(search,regex=False)]
    if candidates.empty:st.stop()
    row=candidates.iloc[st.selectbox('Select customer',range(min(len(candidates),250)),format_func=lambda i:f'Customer {i+1} • {candidates.iloc[i].customer_id[-3:].rjust(6,"*")}')]
    case=Case(customer_id='***'+str(row['customer_id'])[-3:],qualifying_events_180d=int(row['qualifying_events_180d']),recency_days=int(row['recency_days']),relationship_activity_percentile=float(row['relationship_activity_percentile']),service_issue=bool(row['service_issue']),products_held=tuple(str(row['products_held']).split('|')) if isinstance(row['products_held'],str) else tuple(row['products_held']) if isinstance(row['products_held'],list) else (),behavioural_reason=str(row['behavioural_reason']),customer_status=str(row['customer_status']),account_status=str(row['account_status']),kyc_status=str(row['kyc_status']))
    # Product holdings serialized as Python-list strings in CSV: use literal_eval, not eval.
    import ast
    try:case.products_held=tuple(ast.literal_eval(str(row['products_held'])))
    except (SyntaxError,ValueError,TypeError):case.products_held=()
    st.info('Historical features use transactions before 2026-07-01. Customer status, account status, KYC and product holdings are CURRENT snapshots used only for present-day offer screening.')
    a,b,c=st.columns(3);a.metric('Qualifying events / 180d',int(row['qualifying_events_180d']));b.metric('Historical recency (days)',int(row['recency_days']));c.metric('Activity percentile (not profit)',f'{float(row["relationship_activity_percentile"]):.1%}')
    st.write('**Product gap:**', 'Savings Account not recorded' if case.proposed_product not in case.products_held else 'Savings Account already held')
    st.write('**Evidence for savings discussion:**',case.behavioural_reason or 'No sufficient observed deposit signal')
else:
    case=st.selectbox('Select synthetic test scenario',DEMO_CASES,format_func=lambda c:c.customer_id)
    st.caption('Synthetic cases deliberately exercise gate failures and permitted reviews.')
p=evaluate(case)
st.subheader('Live Decision Passport')
st.metric('Decision rating',p['rating'])
st.write('**Proposed action:**',p['action'])
st.dataframe(pd.DataFrame(p['gates']),hide_index=True,use_container_width=True)
st.json(p['evidence'],expanded=False)
st.subheader('Manager work queue')
if mode=='BancABC historical extract':
    # Queue evaluates real candidate evidence; do not use current snapshots as predictive features.
    queue=[]
    for _,r in candidates.head(1500).iterrows():
        try:products=tuple(ast.literal_eval(str(r['products_held'])))
        except (SyntaxError,ValueError,TypeError):products=()
        c=Case(customer_id='***'+str(r['customer_id'])[-3:],qualifying_events_180d=int(r['qualifying_events_180d']),recency_days=int(r['recency_days']),relationship_activity_percentile=float(r['relationship_activity_percentile']),service_issue=bool(r['service_issue']),products_held=products,behavioural_reason=str(r['behavioural_reason']),customer_status=str(r['customer_status']),account_status=str(r['account_status']),kyc_status=str(r['kyc_status']))
        q=evaluate(c)
        if q['rating']=='SUPPORTED':queue.append(q)
        if len(queue)>=capacity:break
else:queue=sorted([evaluate(c) for c in DEMO_CASES if evaluate(c)['rating']=='SUPPORTED'],key=lambda p:p['priority'],reverse=True)[:capacity]
st.dataframe(pd.DataFrame([{'customer':q['customer_id'],'priority':q['priority'],'rating':q['rating'],'action':q['action']} for q in queue]),hide_index=True,use_container_width=True)
st.caption('Only SUPPORTED cases enter the sales-review queue; CAUTION and ABSTAIN require separate investigation. Review capacity is illustrative.')
st.subheader('Human decision and audit trail')
choice=st.selectbox('Decision',['Review','Investigate','No action']);reason=st.text_input('Reason (required)')
if st.button('Record decision'):
    if not reason.strip():st.error('Reason required')
    else:
        st.session_state.audit.append({'utc':datetime.now(timezone.utc).isoformat(),'customer':case.customer_id,'passport':p['rating'],'staff_decision':choice,'reason':reason});st.success('Recorded in local session')
st.dataframe(pd.DataFrame(st.session_state.audit),hide_index=True,use_container_width=True)
