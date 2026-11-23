"""Banc-Inc360 entry point: native navigation over the validated Phase 2 workspace."""
import os
from urllib.parse import urlsplit
import streamlit as st
from data_access import FeatureValidationError
from ui_shell import Workspace,PAGES,REAL,SYNTHETIC,ROOT,selection_controls,provenance

st.set_page_config(page_title='Banc-Inc360 | Banking Intelligence',layout='wide',initial_sidebar_state='expanded')
from design_system import apply_design,identity,system_information
apply_design()
st.logo(str(ROOT/'assets/brand.svg'),size='large')
if 'audit' not in st.session_state:st.session_state.audit=[]
from deployment_data import configuration,load_dataset,DeploymentError
try:
    config=configuration()
except DeploymentError as exc:
    st.error(exc.code+': '+str(exc));st.stop()
path=config.path
st.session_state['_feature_path']=str(path)
with st.sidebar:
    mode=st.radio('Data source',[SYNTHETIC] if config.mode=='DEMO' else [REAL,SYNTHETIC],key='data_source')
index=None
if mode==REAL:
    try:
        with st.spinner('Validating the dataset and preparing the complete decision index…'):
            index=load_dataset(config)
    except (FeatureValidationError,DeploymentError,OSError) as exc:
        st.error((exc.code+': '+str(exc)) if hasattr(exc,'code') else 'Data or private identity configuration cannot be read.')
        st.stop()
    if index.lineage_issues:st.error('Unverified provenance: real recommendations withheld. '+' '.join(i['code']+': '+i['message'] for i in index.lineage_issues))
    groups={}
    for slug,title,group in PAGES:
        groups.setdefault(group,[]).append(st.Page('views/'+slug+'.py',title=title,default=slug=='executive_overview'))
    page=st.navigation(groups,position='sidebar',expanded=True)
    selection_controls(index)
    with st.sidebar:
        size=st.selectbox('Cases per page',[25,50],key='page_size')
        # Main-script controls keep the same identity across native pages.
        lane=st.selectbox('Analytics outcome filter',['ALL','SUPPORTED','CAUTION','ABSTAIN'],key='analytics_lane')
        st.caption('Outcome filter applies to analytics charts/tables. Queue lanes and full-portfolio KPIs have their own explicit scope.')
else:
    page=st.navigation([st.Page('views/synthetic_demo.py',title='Synthetic gate demonstrations',default=True)],expanded=True)
    size=25;lane='ALL'
work=Workspace(index,mode,size,lane);st.session_state['_workspace']=work
provenance(work)
identity()

st.title(page.title)
descriptions = {
    'executive_overview': 'Review portfolio engagement, relationship activity and cases requiring attention.',
    'customer_360': 'Explore customer activity and account relationships. Inspect the supporting Decision Passport.',
    'inactivity_intelligence': 'Identify changes in recorded engagement and review customers with sufficient history.',
    'relationship_value': 'Compare historical relationship activity and identify customers for further value review.',
    'product_opportunities': 'Review potential Savings opportunities and inspect the evidence supporting each case.',
    'decision_passport': 'Examine the six decision checks and complete the required evidence review.',
    'evidence_replay': 'Explore a simulated eligibility change, compare the outcome and reset to source evidence.',
    'manager_work_queue': 'Prioritize eligible cases, inspect evidence and record a reasoned human review.',
    'audit_validation': 'Inspect data quality, decision provenance and the review audit trail.',
}
st.caption(descriptions.get(next((slug for slug, title, _ in PAGES if title==page.title), ''), 'Explore an illustrative scenario using synthetic evidence.'))
page.run()

with st.sidebar.container(key='companion_links'):
    st.html('<style>.st-key-companion_links [data-testid="stPageLink-NavLink"] p {white-space: normal;}</style>')
    st.divider()
    st.caption('ADDITIONAL CAPABILITIES')
    for label, variable, default, explanation in (
        ('Data Management', 'BANCINC_INGESTION_URL', 'http://127.0.0.1:8511',
         'Separate companion; activation does not update the original dashboards.'),
        ('Business Opportunities', 'BANCINC_BUSINESS_URL', 'http://127.0.0.1:8515',
         'Separate companion; synthetic upselling is not an approved operational banking decision.'),
    ):
        url = os.environ.get(variable, default).strip()
        try:
            target = urlsplit(url)
            valid = target.scheme in ('http', 'https') and bool(target.hostname) and not target.username and not target.password
            valid = valid and (target.port is None or 1 <= target.port <= 65535)
        except ValueError:
            valid = False
        if valid:
            st.page_link(url, label=label, help=explanation)
        else:
            st.warning(f'{label}: set {variable} to a valid HTTP(S) URL.')

with st.sidebar:
    system_information()
