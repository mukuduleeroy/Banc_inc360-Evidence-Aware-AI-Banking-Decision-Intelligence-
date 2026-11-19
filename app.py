"""Banc-Inc360 entry point: native navigation over the validated Phase 2 workspace."""
import streamlit as st
from data_access import FeatureValidationError
from ui_shell import Workspace,PAGES,REAL,SYNTHETIC,ROOT,selection_controls,provenance

st.set_page_config(page_title='Banc-Inc360 | Banking Intelligence',layout='wide',initial_sidebar_state='expanded')
from design_system import apply_design,identity
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
identity('DEMO' if mode==SYNTHETIC else config.mode)
st.caption('BANC-INC360 / EVIDENCE-AWARE BANKING INTELLIGENCE')
st.title(page.title)
st.caption('Human review required • privacy-safe presentation • no automatic outreach or financial approvals')
page.run()
