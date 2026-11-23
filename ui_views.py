"""Nine views, sharing analytics and the unchanged Phase 2 decision authority."""
from pathlib import Path
import json,math,re
import pandas as pd
import streamlit as st
from analytics import portfolio_frame,distribution,reason_distribution,metrics
from data_access import row_case,manifest_path
from engine import evaluate,DEMO_CASES,POLICY_VERSION
from evidence import holdings,state,KYC_STATES,ACCOUNT_STATES
from replay import simulate
from ui_shell import workspace,selected_alias,select_customer,ROOT
from ui_components import metric_cards,kpis,bars,analytic_filter,paginated,display_number,passport_body,rationale,review_notes,outcome,banking_segment_selector,render_savings_evidence,historical_ai_comparison
from validation_evidence import json_report,test_report,evidence_status


def current():
    work=workspace()
    if not work.index or not work.index.records:
        st.info('No uniquely identified customer is available. Inspect source validation or use a synthetic demonstration.');st.stop()
    return work.index,selected_alias()


def executive_overview():
    index=workspace().index
    st.caption('Portfolio outcomes indicate staff-review eligibility, not bank approval.')
    kpis(index)
    frame=analytic_filter(portfolio_frame(index));m=metrics(index)
    with st.container(horizontal=True):
      with st.container(width=500):
        bars(distribution(frame,'rating','Outcome'),'Outcome','Decision permissions',outcomes=True,key='outcome_chart')
      with st.container(width=500):
        quality=pd.DataFrame({'Evidence quality':['Valid typed feature evidence','Invalid evidence withheld'],'Customers':[int((~frame.invalid_evidence).sum()),int(frame.invalid_evidence.sum())]})
        bars(quality,'Evidence quality','Evidence quality',key='quality_chart')
    st.caption('Valid evidence can still correctly produce ABSTAIN. Quarantined identities are excluded from evaluated charts and disclosed in the input reconciliation.')
    with st.container(border=True):
        st.subheader('Historical engagement')
        metric_cards([('Median historical recency (days)',display_number(m['median_recency_days'])),('Customers with recency >90 days',m['observed_recency_gt90']),('Customers with 4+ events / 180d',m['history_4plus'])],width=290,border=False)
        st.caption('Full-portfolio descriptive indicators at the observation cutoff; no future inactivity prediction.')
    with st.container(horizontal=True):
      with st.container(width=500,border=True):
        st.subheader('Relationship activity')
        metric_cards([('Median activity percentile',display_number(m['median_activity_percentile'],'.0%')),('Median recorded product breadth',display_number(m['median_product_breadth']))],width=210)
        st.caption('Observed activity proxy and current product breadth; not profitability or lifetime value.')
      with st.container(width=500,border=True):
        st.subheader('Product opportunity evidence')
        metric_cards([('Recorded savings gaps',m['savings_gap_candidates']),('Gap + observed deposit rationale',m['savings_gap_with_rationale'])],width=210)
        st.caption('Candidate evidence only. All proposed actions still pass through the six gates.')
    with st.container(horizontal=True):
      with st.container(width=500):bars(distribution(frame,'activity_band','Activity segment'),'Activity segment','Relationship activity segments',key='activity_chart')
      with st.container(width=500):bars(distribution(frame,'savings_gap','Ownership evidence'),'Ownership evidence','Savings ownership evidence',key='gap_chart')
    st.subheader('Why sales actions are withheld')
    reasons=reason_distribution(index)
    bars(reasons,'Reason code','Abstention reasons · full portfolio',key='reasons_chart')
    st.caption('These are non-pass reason codes on ABSTAIN passports. A caution code can accompany another blocking gate; it does not cause abstention by itself. Codes overlap and must not be summed as unique customers.')
    st.page_link('views/audit_validation.py',label='Inspect provenance, policy and validation evidence',icon=':material/verified:')


def customer_360():
    index,alias=current();p=index.passport(alias)
    frame=portfolio_frame(index);r=frame[frame.customer==alias].iloc[0]
    st.subheader(alias)
    from segment_context import selected_banking_segment
    segment=selected_banking_segment(index,alias)
    with st.container(border=True):
        st.write('**Banking segment — source-provided snapshot**')
        st.write(segment['banking_segment'])
        st.caption(segment['explanation']+' Effective date: unknown.')
    outcome(p['rating'])
    metric_cards([('Qualifying events / 180d',display_number(p['evidence']['events_180d'])),('Historical recency (days)',display_number(p['evidence']['recency_days'])),('Activity percentile',display_number(p['evidence']['relationship_activity_percentile'],'.1%')),('Recorded accounts · snapshot',display_number(r.account_count))])
    with st.container(horizontal=True):
      with st.container(width=500,border=True):
        st.subheader('Historical evidence')
        st.dataframe(pd.DataFrame({'Indicator':['Qualifying events / 90d','Absolute transaction volume / 180d (USD)','Cash deposit events / 180d','History coverage band'],'Value':[display_number(r.events_90d),display_number(r.transaction_volume_180d_usd,',.2f'),display_number(r.deposit_events_180d),r.frequency_band]}),hide_index=True,width='stretch')
        st.write('**Savings discussion rationale:**',rationale(p['evidence']['behavioural_reason']))
        st.caption('Volume is observed activity, not balance, revenue, profit or salary evidence.')
      with st.container(width=500,border=True):
        st.subheader('Current snapshot evidence')
        st.dataframe(pd.DataFrame({'Check':['Customer status','Account status','KYC','Recorded product breadth'],'Value':[r.customer_status,r.account_status,r.kyc_status,display_number(r.product_breadth)]}),hide_index=True,width='stretch')
        st.write('**Products:**',', '.join(r.products) if r.products else 'Explicitly empty portfolio' if r.products==() else 'Ownership evidence unavailable')
        st.caption('Snapshot effective date is unknown. These fields do not reconstruct historical eligibility.')
    st.caption('Unavailable evidence can withhold a recommendation. Inspect the Decision Passport before proceeding.')
    st.page_link('views/decision_passport.py',label='Inspect this customer’s six-gate Decision Passport',icon=':material/fact_check:')
    st.page_link('views/evidence_replay.py',label='Try a labeled evidence simulation',icon=':material/science:')


def inactivity_intelligence():
    index=workspace().index;frame=banking_segment_selector(index,analytic_filter(portfolio_frame(index)),'inactivity')
    st.caption('Historical Analysis • days since the last qualifying transaction. Observed inactivity is not a prediction of churn.')
    try:
        cutoff=pd.Timestamp(index.cutoff) if isinstance(index.cutoff,str) and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',index.cutoff) else None
        if cutoff is not None and pd.isna(cutoff):cutoff=None
    except ValueError:cutoff=None
    st.caption(f'Cutoff (exclusive): {index.cutoff} • 180-day window begins {str((cutoff-pd.Timedelta(days=180)).date()) if cutoff is not None else "unavailable"} • 90-day window begins {str((cutoff-pd.Timedelta(days=90)).date()) if cutoff is not None else "unavailable"}. Source timezone is unspecified; timestamps are naive.')
    with st.container(horizontal=True):
      with st.container(width=500):bars(distribution(frame,'recency_band','Observed recency'),'Observed recency','Observed recency distribution',key='recency_chart')
      with st.container(width=500):bars(distribution(frame,'frequency_band','Historical events / 180d'),'Historical events / 180d','Historical evidence coverage',key='frequency_chart')
    st.caption('0–1, 2–3 and 4+ event bands describe the existing G2 evidence thresholds. The engine remains the authority on final permissions; this view remains descriptive. Offline experimental evaluation is separate and does not authorize actions.')
    band=st.selectbox('Observed recency band',['ALL','0–30 days','31–60 days','61–90 days','>90 days','Unavailable'],key='recency_filter')
    coverage=st.selectbox('History coverage',['ALL','0–1 events','2–3 events','4+ events','Unavailable'],key='coverage_filter')
    filtered=frame[(frame.recency_band==band) if band!='ALL' else pd.Series(True,index=frame.index)]
    if coverage!='ALL':filtered=filtered[filtered.frequency_band==coverage]
    paginated(filtered,['customer','recency_days','qualifying_events_180d','events_90d','frequency_band','rating'],'inactivity',sort=['recency_days','customer'])
    historical_ai_comparison(index,st.session_state['_feature_path'])


def relationship_value():
    index=workspace().index;frame=banking_segment_selector(index,analytic_filter(portfolio_frame(index)),'relationship')
    st.caption('Historical Analysis • relationship activity ranks qualifying transaction turnover over 180 days. Activity is not profitability, revenue or lifetime value.')
    with st.container(horizontal=True):
      with st.container(width=500):bars(distribution(frame,'activity_band','Descriptive segment'),'Descriptive segment','Relationship activity segments',key='relationship_chart')
      with st.container(width=500):bars(distribution(frame,'product_breadth','Recorded product count'),'Recorded product count','Current product breadth',key='breadth_chart')
    st.caption('Descriptive segments: lower <40th percentile; middle 40th–<80th; higher ≥80th. These display bands are not new gate thresholds. Product/account breadth is a current snapshot, not historical prediction evidence.')
    segment=st.selectbox('Observed activity band',['ALL','Higher activity (80th+)','Middle activity (40th–<80th)','Lower activity (<40th)','Unavailable'],key='activity_segment')
    filtered=frame if segment=='ALL' else frame[frame.activity_band==segment]
    paginated(filtered,['customer','relationship_activity_percentile','transaction_volume_180d_usd','product_breadth','account_count','activity_band','rating'],'relationship',sort=['relationship_activity_percentile','customer'])


def product_opportunities():
    index=workspace().index;full=portfolio_frame(index);frame=banking_segment_selector(index,analytic_filter(full),'opportunities')
    st.caption('Savings opportunities require supporting evidence and all six checks. SUPPORTED permits staff review, not an offer or customer contact.')
    metric_cards([('Recorded savings gaps',int((full.savings_gap=='Gap recorded').sum())),('Gap + recorded behavioural rationale',int(((full.savings_gap=='Gap recorded')&full.has_deposit_rationale).sum())),('Engine-supported staff-review cases',index.counts['SUPPORTED'])],width=310)
    bars(distribution(frame,'savings_gap','Savings ownership'),'Savings ownership','Ownership and gaps',key='opportunity_chart')
    context=st.selectbox('Opportunity context',['Supported staff review','Gap candidates · not an offer','Already-held suppression','Unknown ownership'],key='opportunity_context')
    if context=='Supported staff review':filtered=frame[frame.rating=='SUPPORTED']
    elif context=='Gap candidates · not an offer':
        filtered=frame[frame.savings_gap=='Gap recorded'];st.warning('Candidate gaps may be ineligible. Inspect the passport; CAUTION/ABSTAIN cannot authorize sales.')
    elif context=='Already-held suppression':filtered=frame[frame.savings_gap=='Already held']
    else:filtered=frame[frame.savings_gap=='Unknown ownership']
    paginated(filtered,['customer','savings_gap','deposit_events_180d','has_deposit_rationale','kyc_status','account_status','rating'],'opportunities')
    if selected_alias() in set(filtered.customer):render_savings_evidence(index,selected_alias())
    else:st.info('Selected customer is outside this filtered opportunity table. Selection is retained; choose a customer explicitly to inspect its Savings evidence.')


def decision_passport():
    index,alias=current()
    passport_body(index.passport(alias),notes=True)


def reset_simulation():
    for key in list(st.session_state):
        if key.startswith('replay_'):del st.session_state[key]


def evidence_replay():
    index,alias=current();base=index.customer_values(alias);baseline=index.passport(alias)
    st.caption('Simulated Eligibility Change • what-if assumptions, not customer facts. Changes are not saved and cannot authorize action.')
    context=(index.dataset_hash,index.policy_hash,alias)
    if st.session_state.get('replay_context')!=context:
        reset_simulation();st.session_state['replay_context']=context
    st.write('**Starting customer:**',alias)
    st.button('Reset simulation',key='reset_replay',on_click=reset_simulation)
    left,right=st.columns(2)
    kyc_options=sorted(KYC_STATES)+['Unknown (invalid)','Unavailable']
    account_options=sorted(ACCOUNT_STATES)+['Unknown (invalid)','Unavailable']
    kyc_base=state(base['kyc_status'],KYC_STATES) or 'Unavailable';account_base=state(base['account_status'],ACCOUNT_STATES) or 'Unavailable'
    with left:
        kyc=st.selectbox('SIMULATED KYC status',kyc_options,index=kyc_options.index(kyc_base),key='replay_kyc')
        account=st.selectbox('SIMULATED account status',account_options,index=account_options.index(account_base),key='replay_account')
    n=baseline['evidence']['events_180d'];products=holdings(base['products_held'])
    with right:
        unavailable=st.checkbox('SIMULATED history unavailable',value=n is None,key='replay_missing_history')
        count=st.number_input('SIMULATED qualifying events / 180d',min_value=0,value=int(n) if n is not None else 0,step=1,key='replay_count',disabled=unavailable)
        held=st.checkbox('SIMULATED Savings Account already held',value=products is not None and 'Savings Account' in products,key='replay_held')
    overrides={}
    mapped=lambda v:None if v=='Unavailable' else 'UNKNOWN' if v=='Unknown (invalid)' else v
    if mapped(kyc)!=state(base['kyc_status'],KYC_STATES):overrides['kyc_status']=mapped(kyc)
    if mapped(account)!=state(base['account_status'],ACCOUNT_STATES):overrides['account_status']=mapped(account)
    new_count=None if unavailable else int(count)
    if new_count!=n:overrides['qualifying_events_180d']=new_count
    base_held=products is not None and 'Savings Account' in products
    if held!=base_held:
        changed=list(products or ())
        changed=[p for p in changed if p!='Savings Account']
        if held:changed.append('Savings Account')
        overrides['products_held']=changed
    result=simulate(index,alias,overrides)
    from design_system import replay_highlight
    replay_highlight(result)
    a,b=st.columns(2)
    with a.container(border=True):st.metric('Baseline decision',result['baseline']['rating']);st.caption('Unmodified validated dataset')
    with b.container(border=True):st.metric('SIMULATED decision',result['simulated']['rating']);st.caption('Counterfactual only • not actionable')
    st.write('**Modified fields:**',', '.join(result['modified_fields']) or 'None — simulation matches baseline')
    if result['changed_gates']:
        st.dataframe(pd.DataFrame(result['changed_gates']),hide_index=True,width='stretch',key='changed_gates')
        st.write('**SIMULATED final reason codes:**',', '.join(result['simulated']['reason_codes']) or 'All simulated gates passed; still not actionable')
    else:st.info('No gates changed. Reset restores the unmodified baseline.')
    st.caption('Subwindow/deposit counts are held fixed. A conflicting simulated history total also fails G1; validation is never bypassed to force a preferred result. Product gap is derived again when simulated holdings change.')
    with st.expander('Baseline and SIMULATED gate details'):
        st.dataframe(pd.DataFrame(result['baseline']['gates']),hide_index=True,width='stretch')
        st.dataframe(pd.DataFrame(result['simulated']['gates']),hide_index=True,width='stretch')
    st.page_link('views/decision_passport.py',label='Return to the real-data Decision Passport',icon=':material/fact_check:')


def manager_work_queue():
    index=workspace().index;kpis(index)
    lane=st.selectbox('Decision lane',['SUPPORTED','CAUTION','ABSTAIN'],key='lane')
    search=st.text_input('Filter presentation identifier',placeholder='C-…',key='alias_filter').strip()
    from ui_review import queue_status
    matches=queue_status(index.table(lane,search),index)
    local_state=st.selectbox('Review case status',['ALL','NOT_OPENED','OPEN','INVESTIGATION_REQUIRED','DEFERRED','APPROVED_LOCAL','REJECTED','STALE'],key='local_case_filter')
    if local_state!='ALL':matches=matches[matches.case_status==local_state]
    st.caption('Engine eligibility remains separate from local review state. APPROVED_LOCAL is not bank authorization or permission to contact a customer.')
    size=workspace().page_size;pages=max(1,math.ceil(len(matches)/size))
    context=(index.dataset_hash,index.policy_hash,lane,search,local_state,size)
    if st.session_state.get('page_context')!=context:
        st.session_state['page_context']=context;st.session_state['queue_page']=1
    page=st.number_input('Page',min_value=1,max_value=pages,value=1,step=1,key='queue_page')
    visible=matches.iloc[(int(page)-1)*size:int(page)*size].reset_index(drop=True)
    st.caption(f'{len(matches):,} matching {lane} cases • page {int(page)} of {pages}. Eligibility evaluation precedes filtering and pagination.')
    if lane!='SUPPORTED':st.warning('Investigation lane only. These cases are not actionable sales recommendations.')
    st.dataframe(visible,hide_index=True,width='stretch',key='manager_queue')
    if visible.empty:
        st.info('No cases match this lane and presentation-identifier filter. Clear the filter or choose another lane.')
        st.caption('The passport below is an unfiltered inspection case, outside the current queue filter.')
    if not index.records:st.stop()
    options=visible.customer.tolist() if not visible.empty else [selected_alias()]
    alias=st.selectbox('Inspect customer Decision Passport',options,key='passport_customer',on_change=lambda:select_customer(st.session_state['passport_customer']))
    if st.button('Open selected Decision Passport',key='queue_open_passport'):
        select_customer(alias);st.switch_page('views/decision_passport.py')
    st.subheader('Selected case evidence')
    passport_body(index.passport(alias),notes=True)


def audit_validation():
    index=workspace().index;kpis(index)
    st.subheader('Dataset and build provenance')
    manifest=json_report(manifest_path(st.session_state['_feature_path']))
    paths=[ROOT/'outputs/phase2/input_integrity_verification/reconciliation.json',ROOT/'outputs/phase2/final_verification/reconciliation.json']
    reports=[(p,json_report(p)) for p in paths]
    matched=next(((p,r) for p,r in reports if evidence_status(index,r)=='Matched source rebuild'),None)
    source_rows=matched[1].get('builder_audit',{}).get('total_transactions') if matched else None
    st.dataframe(pd.DataFrame({'Evidence':['Source','Source transaction rows','Imported feature rows','Evaluated customers','Historical cutoff','Snapshot effective date','Feature build version','Source comparison','Policy version'],'Recorded value':['Supplied local competition extract',display_number(source_rows),str(index.input_rows),str(len(index.records)),index.cutoff,'Unknown',manifest.get('builder_version','Unavailable') if manifest else 'Unavailable','Matched source rebuild' if matched else 'Unavailable or stale',POLICY_VERSION]}),hide_index=True,width='stretch')
    with st.expander('Integrity fingerprints'):
        st.json({'dataset_sha256':index.dataset_hash,'policy_sha256':index.policy_hash,'source_sha256':manifest.get('source_sha256') if manifest else None,'lineage_issues':index.lineage_issues})
    st.caption('Hashes bind local artifacts; manifests are trusted local build evidence, not externally signed banking attestation. Source reconciliation is checked against the currently loaded feature fingerprint.')
    st.subheader('Recorded automated test evidence')
    available=False
    for path in [ROOT/'outputs/phase7/tests.xml',ROOT/'outputs/phase6/tests.xml',ROOT/'outputs/phase5/tests.xml',ROOT/'outputs/phase4/tests.xml',ROOT/'outputs/phase3/tests.xml',ROOT/'outputs/phase2/tests.xml']:
        report=test_report(path)
        if report:
            available=True
            st.dataframe(pd.DataFrame([{'Artifact':report['artifact'],'Recorded timestamp':report['timestamp'],'Tests':report['tests'],'Passed':report['passed'],'Failures':report['failures'],'Errors':report['errors'],'Skipped':report['skipped']}]),hide_index=True,width='stretch')
    if not available:st.info('No readable, internally reconciled test report is available. No passing test count is assumed.')
    st.caption('Counts above come from parsed JUnit artifacts. A past run is not an automatic certification of the current source revision; rerun validation after changes.')
    st.subheader('Known limits and required controls')
    st.write('• Current snapshots have no verified effective date.\n• Descriptive activity proxies are not profitability or future predictions.\n• Historical experimental evaluation is available when its artifact is verified; approved live fitted inference is unavailable.\n• Evidence Replay is a controlled simulation, not a transaction-level historical replay.\n• Legacy notes are session-only. Durable local review events are available; no authenticated staff authorization or bank approval is implemented.\n• No customer outreach or financial action is connected.')
    historical_ai_comparison(index,st.session_state['_feature_path'])
    from ui_review import render_audit_history
    render_audit_history(index)
    st.subheader('Legacy session notes — not bank approvals')
    st.dataframe(pd.DataFrame(st.session_state.audit),hide_index=True,width='stretch',key='audit_notes')


def synthetic_demonstration():
    st.info('SYNTHETIC controlled gate demonstration. Portfolio metrics and real-data analytics are not shown in this mode.')
    case=st.selectbox('Select synthetic test scenario',DEMO_CASES,format_func=lambda c:c.customer_id,key='synthetic_case')
    p=evaluate(case)
    queue=[evaluate(c) for c in DEMO_CASES if evaluate(c)['rating']=='SUPPORTED']
    st.dataframe(pd.DataFrame([{'customer':p['customer_id'],'rating':p['rating'],'action':p['action']} for p in queue]),hide_index=True,width='stretch')
    passport_body(p,notes=True)
