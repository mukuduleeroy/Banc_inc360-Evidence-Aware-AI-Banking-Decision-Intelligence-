"""Shared native Streamlit shell and persistent, privacy-safe workspace selection."""
from dataclasses import dataclass
from pathlib import Path
import streamlit as st
from engine import DEMO_CASES

ROOT=Path(__file__).resolve().parent
REAL='BancABC historical extract'
SYNTHETIC='Synthetic gate demonstrations'
PAGES=(
 ('executive_overview','Executive Overview','OVERVIEW'),
 ('customer_360','Customer 360','OVERVIEW'),
 ('inactivity_intelligence','Inactivity Intelligence','CUSTOMER INTELLIGENCE'),
 ('relationship_value','Relationship Value Intelligence','CUSTOMER INTELLIGENCE'),
 ('product_opportunities','Product Opportunity Intelligence','CUSTOMER INTELLIGENCE'),
 ('decision_passport','Decision Passport','DECISION MANAGEMENT'),
 ('evidence_replay','Evidence Replay','DECISION MANAGEMENT'),
 ('manager_work_queue','Manager Work Queue','DECISION MANAGEMENT'),
 ('audit_validation','Audit & Validation Evidence','GOVERNANCE'),
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
        if work.mode!=REAL:
            st.caption('Illustrative Scenario • synthetic customer evidence')
        elif work.index.lineage_issues:
            st.warning('Data provenance requires attention; recommendations are withheld.')
