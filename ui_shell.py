"""Shared native Streamlit shell and persistent, privacy-safe workspace selection."""
from dataclasses import dataclass
from pathlib import Path
import streamlit as st
from engine import DEMO_CASES

ROOT=Path(__file__).resolve().parent
REAL='BancABC historical extract'
SYNTHETIC='Synthetic gate demonstrations'
PAGES=(
 ('executive_overview','Executive Overview','Portfolio'),
 ('customer_360','Customer 360','Customer intelligence'),
 ('inactivity_intelligence','Inactivity Intelligence','Customer intelligence'),
 ('relationship_value','Relationship Value Intelligence','Customer intelligence'),
 ('product_opportunities','Product Opportunity Intelligence','Customer intelligence'),
 ('decision_passport','Decision Passport','Decisions'),
 ('evidence_replay','Evidence Replay','Decisions'),
 ('manager_work_queue','Manager Work Queue','Decisions'),
 ('audit_validation','Audit & Validation Evidence','Assurance'),
)

@dataclass(frozen=True)
class Workspace:
    index: object
    mode: str
    page_size: int
    analysis_lane: str


def workspace():
    return st.session_state['_workspace']

def selected_alias():
    return st.session_state.get('selected_alias')

def select_from_widget(key):
    st.session_state['selected_alias']=st.session_state[key]

def select_customer(alias):
    st.session_state['selected_alias']=alias
    # This function is called inside a page, after the global selector has rendered.
    # Its dedicated state is synchronized on the next run; never mutate that widget here.

def selection_controls(index):
    context=(index.dataset_hash,index.policy_hash)
    if st.session_state.get('_selection_context')!=context:
        st.session_state['_selection_context']=context
        st.session_state['selected_alias']=next((r.alias for r in index.records if r.rating=='SUPPORTED'),index.records[0].alias if index.records else None)
    alias=selected_alias()
    with st.sidebar:
        st.subheader('Customer workspace')
        search=st.text_input('Find customer alias',placeholder='C-…',key='global_alias_search').strip()
        matches=[r.alias for r in index.records if search.upper() in r.alias]
        if not matches:
            st.info('No customer alias matches. The current selection is retained.')
        else:
            options=matches[:50]
            if alias and alias not in options:options=[alias]+options
            if st.session_state.get('global_customer') != alias:
                st.session_state['global_customer']=alias
            st.selectbox('Selected customer',options,index=options.index(alias) if alias in options else 0,key='global_customer',on_change=select_from_widget,args=('global_customer',))
        st.caption(f'{len(matches):,} matching aliases; up to 50 results shown. Refine the alias to reach any customer.')


def provenance(work):
    with st.sidebar:
        st.divider()
        st.caption('PRESENTATION MODE • aliases only')
        if work.mode==REAL:
            st.caption('COMPETITION DATA • validated feature extract' if not work.index.lineage_issues else 'UNVERIFIED IMPORT • recommendations withheld')
            st.write('Historical cutoff',work.index.cutoff)
            st.caption('Current snapshot effective date: unknown. Staff verification required.')
            st.caption(f'Data fingerprint: {work.index.dataset_hash[:12]}…')
            st.caption(f'Policy fingerprint: {work.index.policy_hash[:12]}…')
        else:
            st.caption('SYNTHETIC DEMONSTRATION • no real-data KPIs')
        from deployment_data import setting
        st.caption('DATA MODE · '+('DEMO' if work.mode==SYNTHETIC else str(setting('DATA_MODE','LOCAL')).upper()))
        if st.session_state.get('durable_reviewer'):
            st.caption('Reviewer · '+str(st.session_state['durable_reviewer'])+' · unverified demo attribution')
        st.caption('Independent student prototype • not operated by BancABC')
        st.caption('No outreach • no financial approvals')
