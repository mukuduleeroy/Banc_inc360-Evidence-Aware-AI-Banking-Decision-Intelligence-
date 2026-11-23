"""Presentation helpers only. Permission outcomes always come from engine/index."""
from datetime import datetime,timezone
import math,re
import altair as alt
import pandas as pd
import streamlit as st
from ui_shell import workspace,selected_alias,select_customer

from design_system import COLORS as TOKENS,STATUS_COLORS,FONT,gate_cards
NAVY=TOKENS['navy'];TEAL=TOKENS['primary'];TEXT=TOKENS['text'];MUTED=TOKENS['muted']
COLORS=STATUS_COLORS

def display_number(value,format_string=',.0f'):
    return 'Unavailable' if value is None or pd.isna(value) else format(value,format_string)

def metric_cards(entries,width=190,border=True):
    # Native wrapping containers keep values readable even with the sidebar expanded.
    with st.container(horizontal=True,gap='small'):
        for label,value in entries:
            with st.container(width=width,height=144,border=False,key='kpi_'+re.sub('[^a-z0-9]+','_',label.lower())):
                st.caption('Actionable review cases' if label=='Actionable manager-review cases' else label)
                st.metric(label,value,label_visibility='collapsed')

def kpis(index):
    counts=index.counts
    metric_cards(list(zip(['Total evaluated customers','SUPPORTED','CAUTION','ABSTAIN','Actionable manager-review cases'],[len(index.records),counts['SUPPORTED'],counts['CAUTION'],counts['ABSTAIN'],counts['SUPPORTED']])))
    st.caption(f'Full population before filters • {index.input_rows:,} input rows • {len(index.exclusions):,} quarantined identities • {index.invalid_records:,} invalid-evidence cases withheld.')

def outcome(rating):
    text=f'{rating} · '+('Eligible for staff review only' if rating=='SUPPORTED' else 'Investigation required; no sales action')
    {'SUPPORTED':st.success,'CAUTION':st.warning,'ABSTAIN':st.info}[rating](text)

def bars(data,category,title,outcomes=False,key=None):
    if data.empty:
        st.info('No available evidence for this chart.');return
    chart=alt.Chart(data).mark_bar(cornerRadiusEnd=4).encode(x=alt.X('Customers:Q',title='Customers',axis=alt.Axis(tickCount=4,format='~s',labelOverlap=True),scale=alt.Scale(domain=[0,max(1,float(data['Customers'].max()))*1.2])),y=alt.Y(category+':N',title=None,sort='-x'),tooltip=[alt.Tooltip(category+':N'),alt.Tooltip('Customers:Q',format=',')])
    chart=chart.encode(color=alt.Color(category+':N',scale=alt.Scale(domain=list(COLORS),range=list(COLORS.values())),legend=None)) if outcomes else chart.encode(color=alt.value(TEAL))
    labels=alt.Chart(data).mark_text(align='left',dx=6,color=TEXT,fontSize=12).encode(x=alt.X('Customers:Q',axis=alt.Axis(tickCount=4,format='~s',labelOverlap=True),scale=alt.Scale(domain=[0,max(1,float(data['Customers'].max()))*1.2])),y=alt.Y(category+':N',sort='-x'),text=alt.Text('Customers:Q',format=','))
    chart=(chart+labels).properties(title=title,height=max(180,min(320,len(data)*38))).configure_axis(labelColor=TEXT,titleColor=TEXT,labelLimit=155,labelFontSize=12,titleFontSize=12,gridColor=TOKENS['border']).configure_title(color=NAVY,anchor='start',fontSize=15).configure_view(stroke=None).configure(background=TOKENS['surface'],font=FONT)
    st.altair_chart(chart,use_container_width=True,key=key,theme=None)
    with st.expander('View chart data — '+title):st.dataframe(data,hide_index=True,width='stretch')

def analytic_filter(frame):
    lane=workspace().analysis_lane
    if lane!='ALL':
        st.caption(f'Analytics filter: {lane}. Executive population KPIs and actionable queue totals remain unfiltered.')
        return frame[frame.rating==lane]
    return frame

def paginated(frame,columns,prefix,sort=None):
    if sort:frame=frame.sort_values(sort,ascending=[False]+[True]*(len(sort)-1),kind='stable')
    size=workspace().page_size
    context=(tuple(frame.customer) if 'customer' in frame else len(frame),size)
    context_key=prefix+'_context';page_key=prefix+'_page'
    if st.session_state.get(context_key)!=context:
        st.session_state[context_key]=context;st.session_state[page_key]=1
    pages=max(1,math.ceil(len(frame)/size))
    page=st.number_input('Page',min_value=1,max_value=pages,value=1,step=1,key=page_key)
    visible=frame.iloc[(int(page)-1)*size:int(page)*size]
    st.caption(f'{len(frame):,} matching customers • page {int(page)} of {pages} • {size} per page')
    st.dataframe(visible[columns],hide_index=True,width='stretch',key=prefix+'_table',column_config={
        'customer':st.column_config.TextColumn('Customer alias',width='medium'),
        'recency_days':st.column_config.NumberColumn('Recency (days)',format='%d'),
        'qualifying_events_180d':st.column_config.NumberColumn('Qualifying events / 180d',format='%d'),
        'events_90d':st.column_config.NumberColumn('Qualifying events / 90d',format='%d'),
        'relationship_activity_percentile':st.column_config.NumberColumn('Activity percentile (0–1)',format='%.4f'),
        'transaction_volume_180d_usd':st.column_config.NumberColumn('Observed 180d volume (USD)',format='%.2f'),
        'product_breadth':st.column_config.NumberColumn('Products · current snapshot',format='%d'),
        'account_count':st.column_config.NumberColumn('Accounts · current snapshot',format='%d'),
        'rating':st.column_config.TextColumn('Decision'),
    })
    if visible.empty:st.info('No cases match the current filters. Clear a filter to inspect available evidence.')
    elif 'customer' in visible:
        options=visible.customer.tolist();current=selected_alias()
        key=prefix+'_customer'
        choice=st.selectbox('Inspect a customer',options,index=options.index(current) if current in options else 0,key=key,on_change=lambda:select_customer(st.session_state[key]))
        left,right=st.columns(2)
        if left.button('Open Customer 360',key=prefix+'_open_customer'):
            select_customer(choice);st.switch_page('views/customer_360.py')
        if right.button('Open Decision Passport',key=prefix+'_open_passport'):
            select_customer(choice);st.switch_page('views/decision_passport.py')
    return visible

def rationale(text):
    if isinstance(text,str) and (re.fullmatch(r'\d+ observed cash deposits in previous 180 days',text) or text=='Repeated qualifying deposits'):
        return text
    return 'No sufficient observed deposit signal' if not isinstance(text,str) or not text.strip() else 'Recorded behavioural evidence; staff verification required.'

def passport_body(p,notes=False,simulated=False):
    st.metric('Decision rating',p['rating'])
    outcome(p['rating'])
    st.write('**Customer:**',p['customer_id'])
    st.write('**Candidate action:**',p['action'])
    gate_cards(p['gates'])
    st.dataframe(pd.DataFrame(p['gates']),hide_index=True,width='stretch',key='passport_gates')
    st.write('**Reason codes:**',', '.join(p['reason_codes']) or 'All evidence gates passed')
    st.caption('Requires Human Review • decision policy '+p['policy_version']+' • evidence-based rules')
    with st.expander('Evidence and provenance',expanded=False):
        evidence=dict(p['evidence']);evidence['behavioural_reason']=rationale(evidence.get('behavioural_reason'))
        st.json(evidence)
        if 'lineage' in p:st.json(p['lineage'])
    st.caption('Required staff action: verify current status and suitability, review evidence and record a reason. SUPPORTED is not bank approval.')
    if notes and not simulated:
        review_notes(p)
        from ui_shell import REAL
        if workspace().mode==REAL:
            from ui_review import render_workflow
            render_workflow(workspace().index,p['customer_id'])

def review_notes(p):
    st.subheader('Session review notes')
    st.caption('Notes remain in this session. They are not bank approval or a saved review. Avoid personal information.')
    context=(workspace().mode,p['customer_id'],p.get('lineage',{}).get('dataset_sha256'),p['policy_version'])
    if st.session_state.get('_review_context')!=context:
        st.session_state['_review_context']=context
        st.session_state['staff_reason']=''
        st.session_state['staff_choice']='Review'
    choice=st.selectbox('Decision',['Review','Investigate','No action'],key='staff_choice')
    reason=st.text_input('Reason (required)',key='staff_reason')
    if st.button('Record decision',key='record_decision'):
        if not reason.strip():st.error('Reason required')
        else:
            st.session_state.audit.append({'utc':datetime.now(timezone.utc).isoformat(),'customer':p['customer_id'],'source':workspace().mode,'dataset_sha256':p.get('lineage',{}).get('dataset_sha256'),'policy_version':p['policy_version'],'passport':p['rating'],'reason_codes':p['reason_codes'],'staff_decision':choice,'reason':reason})
            st.success('Session note recorded. No customer contact or financial action was taken.')
    st.dataframe(pd.DataFrame(st.session_state.audit),hide_index=True,width='stretch',key='session_audit')


def banking_segment_selector(index,frame,prefix):
    from segment_context import BANKING_SEGMENTS,banking_segment_frame,filter_banking_segment
    selected=st.selectbox('Banking segment — source snapshot',['All',*BANKING_SEGMENTS,'Unknown'],key=prefix+'_banking_segment')
    context=(index.dataset_hash,selected)
    if st.session_state.get(prefix+'_banking_filter_context')!=context:
        st.session_state[prefix+'_banking_filter_context']=context;st.session_state[prefix+'_page']=1
    result=filter_banking_segment(frame,banking_segment_frame(index),selected)
    st.caption(f'Banking segment: {selected} • {len(result):,} customers in this analytic subset before other page filters. Full-population KPIs remain unfiltered. Source snapshot effective date: unknown.')
    return result


def savings_opportunity_evidence(index,alias):
    from evidence import holdings
    from analytics import numeric
    p=index.passport(alias);values=index.customer_values(alias);gates={g['gate'].split()[0]:g for g in p['gates']}
    return {'customer':p['customer_id'],'product':'Savings Account' if p['evidence']['product']=='Savings Account' else 'Unavailable','products':holdings(values.get('products_held')),'savings_gap':p['evidence']['product_gap'],'deposit_events_180d':numeric(values.get('deposit_events_180d'),integer=True),'rationale':rationale(p['evidence']['behavioural_reason']),'gates':[dict(gates[g]) for g in ('G4','G5')],'rating':p['rating'],'cutoff':index.cutoff,'dataset_sha256':index.dataset_hash,'policy_sha256':index.policy_hash,'snapshot_effective_date':None}


def render_savings_evidence(index,alias):
    e=savings_opportunity_evidence(index,alias)
    with st.expander('Savings evidence — selected customer',expanded=True):
        st.caption('Requires Human Review • Savings discussion candidate, not an approved offer or permission to contact the customer.')
        st.write('**Selected customer:**',e['customer'])
        st.write('**Current known holdings:**',', '.join(e['products']) if e['products'] else 'Explicitly empty portfolio' if e['products']==() else 'Unavailable ownership evidence')
        st.write('**Recorded Savings gap:**','Yes' if e['savings_gap'] is True else 'No' if e['savings_gap'] is False else 'Unavailable')
        st.write('**Historical qualifying cash-deposit events / 180d:**',display_number(e['deposit_events_180d']))
        st.write('**Observed rationale:**',e['rationale'])
        st.write('**Final engine decision:**',e['rating'])
        st.dataframe(pd.DataFrame(e['gates'])[['gate','status','reason_codes','reason']],hide_index=True,width='stretch',key='savings_explanation_gates')
        st.caption('Segment-specific bank suitability policy: unavailable. Current holdings/status effective dates are unknown; staff verification remains required.')
        st.caption('Historical cutoff: '+e['cutoff']+' • feature SHA-256 '+e['dataset_sha256']+' • policy SHA-256 '+e['policy_sha256'])


def historical_ai_comparison(index,feature_path):
    from experimental_evidence import load_historical_comparison,LIVE_UNAVAILABLE,CONFIG
    st.subheader('Historical experimental AI comparison')
    st.write('**Current operational method:** deterministic six-gate rules. Operational triage uses descriptive recency and composite priority; no fitted ML model drives the decision engine. The offline recency-only comparator is not the operational composite score.')
    evidence=load_historical_comparison(index,feature_path=feature_path)
    if evidence.status=='Verified':
        st.caption('VERIFIED HISTORICAL EVIDENCE • experimental only • '+evidence.version)
        frame=pd.DataFrame(evidence.rows,columns=['Model','ROC-AUC','Average Precision','Precision@500','Lift@500'])
        st.dataframe(frame,hide_index=True,width='stretch',column_config={k:st.column_config.NumberColumn(k,format='%.4f') for k in frame.columns if k!='Model'},key='historical_ai_metrics')
        st.caption(f'Training cutoff {CONFIG["train_cutoff"]}: {evidence.training_customers:,} customers ({evidence.training_prevalence:.2%} target prevalence). Holdout cutoff {CONFIG["holdout_cutoff"]}: {evidence.holdout_customers:,} customers ({evidence.holdout_prevalence:.2%}). {evidence.shared_customers:,} customers appear in both cohorts.')
        st.info('Target: observed 90-day inactivity (no qualifying non-service-fee activity), not verified churn. Average Precision is the step-integral PR metric. This limited chronological evaluation contains repeated customers; metrics do not prove customer-retention uplift or real-world model deployment.')
        with st.expander('Historical experiment provenance'):
            st.json({'experiment_version':evidence.version,'artifact_sha256':evidence.artifact_sha256,'source_sha256':evidence.source_sha256,'feature_sha256':evidence.feature_sha256,'evaluation_code_sha256':evidence.code_sha256,'observation_days':CONFIG['observation_days'],'target_days':CONFIG['target_days'],'minimum_events':CONFIG['minimum_events'],'experimental_only':True,'operational_model_approval':False})
    else:st.warning(evidence.status+' — '+evidence.message+' ['+evidence.code+']')
    st.write('**Live fitted inference:** '+LIVE_UNAVAILABLE)
