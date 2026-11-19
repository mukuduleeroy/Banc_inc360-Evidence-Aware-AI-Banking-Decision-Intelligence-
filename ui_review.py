"""Targeted durable review and audit UI. No engine policy, outreach or authentication."""
from pathlib import Path
import os,uuid
import pandas as pd
import streamlit as st
from audit_store import AuditStore,AuditError
from review_service import ReviewService,file_digest
from evidence_trace import TRACEABILITY_NOTICE
from engine import POLICY_VERSION
from ui_shell import workspace,ROOT,REAL
from data_access import manifest_path


from deployment_data import audit_configuration,DeploymentError

def database_path():return audit_configuration()[0]

def storage_notice():
    try:cloud=audit_configuration()[1]
    except DeploymentError as exc:
        st.error(exc.code+': '+str(exc));return
    if cloud:
        st.warning('EPHEMERAL CLOUD REVIEW STORAGE — local SQLite may be lost on restart or redeployment. Cloud durability is not verified. Demo attribution only; do not enter personal information.')
    else:st.caption('LOCAL SQLITE REVIEW STORAGE — persists on this local filesystem; retain backups. Not authenticated bank approval.')
def store():return AuditStore(database_path())
def service(storage):return ReviewService(storage,features_path=st.session_state['_feature_path'])

def freshness(case,index):
    if not case:return 'NOT_OPENED'
    try:manifest_hash=file_digest(manifest_path(st.session_state['_feature_path']))
    except OSError:return 'STALE'
    return case['state'] if (case['dataset_hash'],case['manifest_hash'],case['policy_hash'],case['policy_version'])==(index.dataset_hash,manifest_hash,index.policy_hash,POLICY_VERSION) else 'STALE'

def queue_status(frame,index):
    """Add workflow state without changing any authoritative eligibility field/order."""
    result=frame.copy()
    try:
        cases={c['customer_ref']:c for c in store().cases()}
        result['case_status']=[freshness(cases.get(alias),index) for alias in result.customer]
        result['last_demo_reviewer']=[cases.get(alias,{}).get('last_reviewer_id') for alias in result.customer]
        result['latest_review_action']=[cases.get(alias,{}).get('last_action') for alias in result.customer]
        result['review_timestamp_utc']=[cases.get(alias,{}).get('updated_utc') for alias in result.customer]
    except (AuditError,DeploymentError,OSError):
        st.error('Audit storage is unavailable. No durable review action can be saved.')
        result['case_status']='AUDIT_UNAVAILABLE'
    return result

def render_workflow(index,alias):
    if workspace().mode!=REAL:
        st.caption('Durable real-case review is unavailable in synthetic or simulation mode.');return
    st.subheader('Durable human review — local prototype only')
    storage_notice()
    st.caption('SQLite-backed local review events survive restarts on retained storage. Demo reviewer labels are unverified attribution, not login, identity verification or bank authorization. No review outcome initiates outreach or a financial action.')
    try:
        storage=store();reviews=service(storage);context=reviews.current(alias);case=storage.case_for_customer(alias)
        reviewers=storage.reviewers();labels={r['reviewer_id']:r['reviewer_id']+' · '+r['display_name']+' (unverified)' for r in reviewers}
        reviewer=st.selectbox('Demo reviewer — explicit unverified selection',list(labels),index=None,format_func=lambda v:labels.get(v,v),placeholder='Select a demonstration reviewer',key='durable_reviewer')
        current_status=reviews.status(case,context)
        st.write('**Case status:**',current_status)
        if case:
            st.caption('Case '+case['case_id']+' • revision '+str(case['revision'])+' • latest action '+str(case['last_action'])+' • last demo reviewer '+str(case['last_reviewer_id'])+' • UTC '+case['updated_utc'])
        else:
            if st.button('Open case and inspect Passport',key='open_review_case',disabled=reviewer is None):
                reviews.open_case(alias,reviewer,'open-'+uuid.uuid4().hex)
                st.session_state['_durable_notice']='Case opened with an immutable passport snapshot. Inspect the current gates before recording a local outcome.';st.rerun()
            st.info('Select a demo reviewer and open the case to begin a durable review. Existing session notes are not migrated into approvals.')
            return
        notice=st.session_state.pop('_durable_notice',None)
        if notice:st.success(notice)
        if current_status=='STALE':st.warning('STALE EVIDENCE — the stored case is not currently eligible for a review action. Refresh it and inspect the new passport; historical approvals remain history only.')
        with st.expander('Refresh evidence and reopen review',expanded=current_status=='STALE'):
            refresh_reason=st.text_input('Required refresh reason',key='refresh_reason',max_chars=2000)
            if st.button('Refresh case evidence',key='refresh_review_case',disabled=reviewer is None):
                reviews.refresh_case(case['case_id'],reviewer,refresh_reason,case['revision'],'refresh-'+uuid.uuid4().hex)
                st.session_state['_durable_notice']='Evidence refreshed; previous events retained. Inspect the new snapshot before another review.';st.rerun()
        form_context=(case['case_id'],case['revision'],context.dataset_hash,context.manifest_hash,context.policy_hash,reviewer)
        if st.session_state.get('_durable_form_context')!=form_context:
            st.session_state['_durable_form_context']=form_context
            st.session_state['durable_reason']='';st.session_state['durable_ack']=False
            st.session_state['_durable_request_id']='review-'+uuid.uuid4().hex
        options=['Approve','Defer','Reject'] if context.passport['rating']=='SUPPORTED' else ['Defer','Reject']
        if context.passport['rating']!='SUPPORTED':st.info('CAUTION/ABSTAIN: approval is unavailable. Investigate, defer or reject; do not treat this as a sales recommendation.')
        with st.form('durable_review_form'):
            action=st.selectbox('Local prototype review outcome',options,key='durable_action')
            reason=st.text_area('Required review reason — no personal data or credentials',key='durable_reason',max_chars=2000)
            acknowledged=st.checkbox('I inspected this current six-gate Passport and understand this is not authenticated bank approval.',key='durable_ack')
            save=st.form_submit_button('Save durable review',key='save_durable_review',disabled=reviewer is None or current_status=='STALE')
        if save:
            result=reviews.record_review(case['case_id'],reviewer,action.upper(),reason,case['revision'],case['current_snapshot_id'],st.session_state['_durable_request_id'],acknowledged)
            st.session_state['_durable_notice']='Local review event '+result['event_id']+(' was already recorded; no duplicate event written.' if result['idempotent'] else ' committed. No outreach or bank approval occurred.');st.rerun()
        with st.expander('Stored passport snapshot and feature references'):
            snap=storage.snapshot(case['current_snapshot_id'])
            st.caption('Immutable snapshot '+snap['snapshot_id']+' • SHA-256 '+snap['snapshot_hash'])
            st.json(snap['payload'])
            st.caption(TRACEABILITY_NOTICE)
            st.dataframe(pd.DataFrame(snap['evidence_references']),hide_index=True,width='stretch',key='case_evidence_refs')
        st.subheader('Case audit timeline — complete sequence')
        history=storage.timeline(case['case_id'])
        st.dataframe(pd.DataFrame(history),hide_index=True,width='stretch',key='case_timeline')
    except (AuditError,DeploymentError) as exc:st.error(exc.code+': '+str(exc))
    except OSError:st.error('AUDIT_STORAGE_UNAVAILABLE: Durable storage cannot be accessed; no success is recorded.')


def render_audit_history(index):
    st.subheader('Durable review audit')
    storage_notice()
    st.caption('Append-only application events and immutable snapshots in local SQLite; not tamper-proof storage or authenticated bank approval. Database owner access remains an administrative trust boundary.')
    try:
        storage=store();summary=storage.summary()
        a,b,c=st.columns(3);a.metric('Persisted cases',summary['cases']);b.metric('Immutable review events',summary['events']);c.metric('Passport snapshots',summary['snapshots'])
        st.caption('Schema version '+str(summary['schema_version'])+' • event timestamps UTC • explicit DEMO_UNVERIFIED reviewer attribution')
        cases=storage.cases()
        if not cases:st.info('No durable case has been opened. Choose a supported queue case and an explicit demo reviewer.');return
        table=pd.DataFrame([{'case_id':c['case_id'],'customer':c['customer_ref'],'case_status':c['state'],'effective_status':freshness(c,index),'last_demo_reviewer':c['last_reviewer_id'],'latest_action':c['last_action'],'review_timestamp_utc':c['updated_utc']} for c in cases])
        st.dataframe(table,hide_index=True,width='stretch',key='durable_cases')
        ids=[c['case_id'] for c in cases];selected=st.selectbox('Audit case',ids,key='audit_case')
        timeline=storage.timeline(selected)
        st.dataframe(pd.DataFrame(timeline),hide_index=True,width='stretch',key='durable_timeline')
        events={e['event_id']:e for e in timeline}
        event=st.selectbox('Inspect event passport',list(events),key='audit_event')
        snapshot=storage.snapshot(events[event]['snapshot_id'])
        st.json(snapshot['payload'])
        st.caption('Snapshot SHA-256: '+snapshot['snapshot_hash'])
        st.caption(TRACEABILITY_NOTICE)
        st.dataframe(pd.DataFrame(snapshot['evidence_references']),hide_index=True,width='stretch',key='durable_references')
    except (AuditError,DeploymentError) as exc:st.error(exc.code+': '+str(exc))
    except OSError:st.error('AUDIT_STORAGE_UNAVAILABLE: Durable audit history cannot be accessed.')
