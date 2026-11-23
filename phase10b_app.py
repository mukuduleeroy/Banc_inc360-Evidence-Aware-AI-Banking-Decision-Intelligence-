"""Standalone business-capability companion; existing nine dashboards remain untouched."""
from dataclasses import asdict
import os
import pandas as pd
import streamlit as st
from design_system import apply_design,identity,system_information
from phase10b_upsell import demo_scenarios,assess_upsell,demo_summary,UpgradeSpec,ELIGIBLE,MISSING,NOTICE
from phase10b_value import load_accepted_index,value_frame,value_reconciliation,selected_value_explanation,HIGH,UNAVAILABLE,LIMITATION
from segment_context import BANKING_SEGMENTS,banking_segment_frame,filter_banking_segment

st.set_page_config(page_title='Banc-Inc360 | Business Opportunities',page_icon='B',layout='wide')
apply_design();identity()
st.title('Business Opportunities')
st.caption('Explore illustrative account upgrades and source-derived relationship activity. Review the evidence and its scope.')
if os.environ.get('BANCINC_RUNTIME','LOCAL').upper()!='LOCAL':st.error('This companion is available for controlled local demonstration only.');st.stop()
view=st.sidebar.radio('Companion view',['Business Opportunity Overview','Upselling Intelligence','High-Value Customer Intelligence','Evidence and Methodology'],key='p10b_view')
st.header(view)


def accepted():
    try:return load_accepted_index()
    except (OSError,ValueError):st.error('Accepted source/policy fingerprints could not be verified. No customer classifications or fallback data are shown.');return None


if view=='Business Opportunity Overview':
    st.info('Review Savings cross-selling, illustrative account upgrades and historical relationship activity. Each analysis retains its own evidence and scope.')
    with st.container(border=True):
        st.subheader('Existing Savings cross-selling — original application')
        st.write('Known existing products + Savings gap + behavioral evidence + six authoritative gates → staff review only. Open the original Product Opportunity and Decision Passport views to inspect this accepted workflow.')
        st.caption('No product upgrade is claimed by the Savings rule. No new operational product is registered here.')
    index=accepted()
    if index is not None:
        a,b,c,d=st.columns(4)
        for col,(label,n) in zip((a,b,c,d),[('Accepted customers',len(index.records)),*index.counts.items()]):col.metric(label,n)
        proxy=value_reconciliation(index)
        st.metric('High Relationship Activity — original population',proxy['classifications'][HIGH])
        st.caption(LIMITATION)
    summary=demo_summary()
    with st.container(border=True):
        st.subheader('Synthetic upselling — separate illustrative population')
        st.caption('Illustrative Scenario • entirely synthetic customers and hypothetical Standard-to-Premium products • not bank-approved or an operational decision.')
        st.metric('Independent synthetic upsell scenarios',summary['customers'])
        st.json(summary)
        st.caption('DEMO_* outcomes are not included in the original SUPPORTED / CAUTION / ABSTAIN counts and cannot create manager review records.')

elif view=='Upselling Intelligence':
    st.caption('Illustrative Scenario • entirely synthetic customers and hypothetical Standard-to-Premium products • not bank-approved or an operational decision.')
    scenarios=demo_scenarios();labels=[label for label,_,_ in scenarios]
    name=st.selectbox('Synthetic scenario',labels,key='p10b_scenario')
    _,customer,spec=scenarios[labels.index(name)];result=assess_upsell(customer,spec)
    st.caption('Customer and all ownership, service-demand, activity and eligibility evidence below are entirely synthetic. No real customer alias is matched to these tiers.')
    st.write('Synthetic reference:',customer.demo_id)
    st.write('Existing verified synthetic product:',result['source_product']);st.write('Required source tier:',result['required_source_product']);st.write('Proposed upgrade:',result['target_product'])
    st.caption('Hypothetical same-family hierarchy: Standard tier 1 → Premium tier 2. No fees, rates, balances, benefit guarantees or BancABC product facts are specified.')
    st.write('**Illustrative assessment:**',result['assessment'])
    (st.success if result['assessment']==ELIGIBLE else st.warning if result['assessment']==MISSING else st.error)(result['explanation'])
    st.dataframe(pd.DataFrame(result['checks']),hide_index=True,width='stretch',key='p10b_upsell_checks')
    st.write('Passed checks:',result['passed_checks']);st.write('Failed checks:',result['failed_checks']);st.write('Missing evidence:',result['missing_evidence'])
    st.json(result['evidence'])
    st.info('Mandatory human review. This companion has no approval, saving, communication or financial-action control. Existing Savings-specific G5 has not evaluated or approved this hypothetical upgrade.')
    with st.expander('Illustrative product specification and provenance'):
        st.json(asdict(spec));st.json({k:result[k] for k in ('synthetic','bank_approved','human_review_required','operational_authorization','operational_g5_evaluated','spec_version','provenance')})

elif view=='High-Value Customer Intelligence':
    st.caption('Historical Analysis • source-derived relationship activity; synthetic product scenarios are excluded.')
    st.caption(LIMITATION)
    index=accepted()
    if index is not None:
        frame=value_frame(index);summary=value_reconciliation(index)
        a,b,c=st.columns(3);a.metric('Original global ranking population',summary['customers']);b.metric('High Relationship Activity',summary['classifications'][HIGH]);c.metric('Unavailable activity evidence',summary['classifications'][UNAVAILABLE])
        st.caption('Global average-tie percentile of absolute qualifying 180-day USD turnover, rounded by the existing builder to four decimals. Higher activity threshold >=0.8. Source snapshot effective dates and segment assignment criteria are unknown.')
        segment=st.selectbox('Source banking segment',['All',*BANKING_SEGMENTS,'Unknown'],key='p10b_segment')
        selected=st.selectbox('Display classification',['High Relationship Activity only','All classifications'],key='p10b_class')
        filtered=filter_banking_segment(frame,banking_segment_frame(index),segment)
        if selected=='High Relationship Activity only':filtered=filtered[filtered.value_proxy_classification==HIGH]
        filtered=filtered.sort_values(['relationship_activity_percentile','customer'],ascending=[False,True],kind='stable')
        context=(index.dataset_hash,segment,selected)
        if st.session_state.get('p10b_value_context')!=context:st.session_state['p10b_value_context']=context;st.session_state['p10b_page']=1
        pages=max(1,(len(filtered)+24)//25)
        page=st.number_input('Page',min_value=1,max_value=pages,step=1,key='p10b_page')
        visible=filtered.iloc[(page-1)*25:page*25]
        st.caption(f'{len(filtered):,} matching source-derived customers • page {page} of {pages} • global ranking denominator remains {len(index.records):,}; no segment-relative reranking.')
        columns=['customer','banking_segment','activity_band','relationship_activity_percentile','transaction_volume_180d_usd','product_breadth','account_count','value_proxy_classification']
        st.dataframe(visible[columns],hide_index=True,width='stretch',key='p10b_value_table',column_config={
            'customer':'Customer alias','banking_segment':'Banking segment','activity_band':'Activity band',
            'relationship_activity_percentile':st.column_config.NumberColumn('Activity percentile',format='%.4f'),
            'transaction_volume_180d_usd':st.column_config.NumberColumn('180-day turnover (USD)',format='%.2f'),
            'product_breadth':'Recorded products','account_count':'Recorded accounts','value_proxy_classification':'Review classification'})
        if visible.empty:st.info('No customers match these filters. Choose another segment or include all classifications.')
        else:
            alias=st.selectbox('Inspect source-derived customer',visible.customer.tolist(),key='p10b_value_alias')
            explanation=selected_value_explanation(index,alias)
            st.write(explanation['classification']);st.write(explanation['explanation'])
            st.json(explanation)
        with st.expander('Population and classification reconciliation'):st.json(summary)

else:
    st.subheader('Evidence boundaries and methodology')
    st.write('Original operational decisions: unchanged deterministic G1–G6, Savings-only suitability and mandatory staff review. Original historical ML: offline evaluation only; no live fitted inference has been added.')
    st.caption('Illustrative Scenario • entirely synthetic customers and hypothetical Standard-to-Premium products • not bank-approved or an operational decision.');st.caption(LIMITATION)
    st.write('Synthetic upgrades use a registered hypothetical same-family tier ordering and independently invented ownership/history/expanded-service requests/status. FAIL takes precedence over MISSING; all checks must PASS for DEMO_ELIGIBLE_FOR_REVIEW. No DEMO_* outcome is a six-gate operational decision.')
    st.json(asdict(UpgradeSpec()))
    st.write('Value proxy reuses the accepted global activity percentile and original activity band. It does not compute a new rank, segment-specific economics, profit, balance, fee income, LTV or future revenue. Breadth/account context is descriptive.')
    index=accepted()
    if index is not None:st.json(value_reconciliation(index))
    st.caption('Current snapshot dates are unknown. Upgrade thresholds are illustrative, not BancABC policy. Operational reviews and dataset selection remain separate.')

with st.sidebar:
    system_information()
