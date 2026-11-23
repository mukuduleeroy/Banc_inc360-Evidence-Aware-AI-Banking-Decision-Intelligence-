"""Separate local Streamlit companion; accepted app.py and nine routes are untouched."""
from pathlib import Path
import os
import pandas as pd
import streamlit as st
from design_system import apply_design,identity,gate_cards
from phase9_ingestion import SnapshotStore,IngestionError,SOURCE_FIELDS,DISCLAIMER,DEFAULT_STORAGE,MAX_BYTES
from data_access import load_index

st.set_page_config(page_title='Banc-Inc360 | Dataset Ingestion & Refresh',page_icon='B',layout='wide')
apply_design();identity('LOCAL')
st.title('Dataset Ingestion & Refresh')
st.warning('CONTROLLED LOCAL DEMONSTRATION • isolated companion preview • no outreach, model inference or banking authorization.')
if st.get_option('server.maxUploadSize')>5:
    st.error('Start this companion with --server.maxUploadSize 5 before enabling uploads.');st.stop()
if os.environ.get('BANCINC_RUNTIME','LOCAL').upper()!='LOCAL':
    st.error('This companion is enabled for local runtime only.');st.stop()
try:
    store=SnapshotStore(os.environ.get('BANCINC_PHASE9_STORAGE',str(DEFAULT_STORAGE)))
except (IngestionError,OSError):
    st.error('Private Phase 9 storage is unavailable. Check the local storage configuration; accepted application data is unaffected.');st.stop()

st.subheader('A · Dataset Upload')
st.caption('UTF-8 transaction CSV only • 5 MiB / 25,000 rows maximum • already-normalized USD amounts • explicit observation date. Synthetic demonstration examples: outputs/phase9/examples/.')
with st.expander('Supported source fields and limits'):
    st.write(list(SOURCE_FIELDS));st.write('Optional Currency must be USD. Pipe-separated known product holdings; source-provided banking segments. Multiple transactions per customer/account are valid. Exact transaction duplicates are audited; conflicting duplicates are rejected. Missing eligibility remains unknown and cannot support a banking action.')
cutoff=st.text_input('Observation date (YYYY-MM-DD)',value='2026-07-01',key='p9_cutoff')
upload=st.file_uploader('Upload compatible CSV',type=['csv'],key='p9_upload')
if upload is not None:
    st.write('Uploaded filename:',upload.name);st.caption(f'File size: {upload.size:,} bytes')
    context=(upload.name,upload.file_id,cutoff)
    if st.session_state.get('p9_upload_context')!=context:
        previous=st.session_state.pop('p9_token',None)
        if previous:
            try:store.cleanup(previous)
            except (IngestionError,OSError):pass
        for key in ('p9_validation','p9_candidate'):st.session_state.pop(key,None)
        st.session_state['p9_upload_context']=context
    if st.button('Validate upload',key='p9_validate'):
        try:
            previous=st.session_state.pop('p9_token',None)
            if previous:store.cleanup(previous)
            if upload.size>MAX_BYTES:raise IngestionError('FILE_SIZE','CSV exceeds the 5 MiB local demonstration limit.')
            upload.seek(0);receipt=store.stage(upload.name,upload);st.session_state['p9_token']=receipt['token']
            st.session_state['p9_validation']=store.validate(receipt['token'],cutoff)
            st.session_state['p9_upload_sha']=receipt['sha256']
        except (IngestionError,OSError) as exc:
            st.session_state.pop('p9_validation',None)
            st.error(str(exc) if isinstance(exc,IngestionError) else 'Upload could not be staged safely. Check local permissions.')

st.subheader('B · Validation Report')
validation=st.session_state.get('p9_validation')
if validation:
    st.caption('Received file SHA-256: '+st.session_state['p9_upload_sha'])
    (st.success if validation['valid'] else st.error)('Validation PASSED' if validation['valid'] else 'Validation FAILED — processing and activation of this upload are blocked.')
    st.json(validation)
else:st.info('Upload and validate a compatible CSV. No dataset is activated automatically.')
if st.button('Discard staged upload',key='p9_cleanup',disabled=not st.session_state.get('p9_token')):
    try:store.cleanup(st.session_state['p9_token'])
    except (IngestionError,OSError):st.error('Cleanup did not complete; accepted artifacts are unaffected.')
    else:
        for key in ('p9_token','p9_validation','p9_candidate'):st.session_state.pop(key,None)
        st.rerun()

st.subheader('C · Processing Summary')
if st.button('Process validated dataset',key='p9_process',disabled=not (validation and validation['valid'] and st.session_state.get('p9_token'))):
    try:
        with st.spinner('Processing through the existing feature builder and decision engine…'):
            result=store.process(st.session_state['p9_token'],cutoff)
        st.session_state['p9_candidate']=result['snapshot_id'];st.session_state.pop('p9_token',None)
        st.success('Validated candidate created. It is not active until explicitly activated.')
    except (IngestionError,OSError) as exc:st.error(str(exc) if isinstance(exc,IngestionError) else 'Processing did not complete; prior active selection is retained.')

try:registry=store.state()
except (IngestionError,OSError):st.error('Registry unavailable. No activation is allowed.');st.stop()
candidate=st.session_state.get('p9_candidate')
if candidate:
    try:
        meta,_=store.inspect(candidate);st.json(meta['reconciliation'])
        st.caption('Candidate snapshot: '+candidate+' • created '+meta['created_at']+' • cutoff '+meta['observation_date'])
        if st.button('Preview candidate snapshot',key='p9_show_candidate'):st.session_state['p9_preview']=candidate
    except (IngestionError,OSError):st.error('Candidate fingerprint no longer verifies; activation is blocked.')

st.subheader('D · Decision Preview')
st.info(DISCLAIMER)
choices=['baseline',*registry['snapshots']]
if st.session_state.pop('p9_return_baseline',False):st.session_state['p9_preview']='baseline'
preview=st.selectbox('Preview dataset',choices,key='p9_preview',format_func=lambda s:'Accepted Phase 8B baseline (read-only)' if s=='baseline' else 'Phase 9 candidate '+s)
meta=None
try:
    if preview=='baseline':index=load_index(Path(__file__).resolve().parent/'outputs/customer_features.csv')
    else:meta,index=store.inspect(preview)
    if index.lineage_issues:raise IngestionError('LINEAGE','Dataset provenance is unavailable; preview blocked.')
    columns=st.columns(4)
    for col,(name,value) in zip(columns,[('Evaluated customers',len(index.records)),*index.counts.items()]):col.metric(name,value)
    st.caption('Preview selection is separate from activation. Display is limited to the first 50 engine-ranked customer aliases; no source identifiers or service free text are shown.')
    st.dataframe(index.table().head(50),hide_index=True,width='stretch',key='p9_decisions')
    aliases=[r.alias for r in index.records[:50]]
    if aliases:
        selected=st.selectbox('Inspect customer evidence',aliases,key='p9_customer')
        passport=index.passport(selected);gate_cards(passport['gates'])
        st.dataframe(pd.DataFrame(passport['gates']),hide_index=True,width='stretch',key='p9_gates')
        st.write('Decision:',passport['rating']);st.write('Reason codes:',passport['reason_codes']);st.json(passport['lineage'])
except (IngestionError,OSError,ValueError):st.error('Preview could not verify source/policy fingerprints. Return to baseline; no action is authorized.')

st.subheader('E · Snapshot Management')
st.write('Active companion selection:',registry['active'])
st.caption('Activation changes this companion registry only. The original nine dashboards always retain their existing dataset selection and behaviour.')
if st.button('Activate validated preview snapshot',key='p9_activate',disabled=preview=='baseline'):
    try:store.activate(preview)
    except (IngestionError,OSError):st.error('Activation failed integrity checks or atomic storage. Previously active selection is retained.')
    else:st.success('Snapshot activated in companion preview only.');st.rerun()
if st.button('Return to accepted baseline',key='p9_rollback'):
    try:store.rollback()
    except (IngestionError,OSError):st.error('Rollback state could not be saved. Accepted baseline files remain untouched.')
    else:st.session_state['p9_return_baseline']=True;st.rerun()

st.subheader('F · Audit and Provenance')
st.caption('Local prototype receipts; not a production audit database. Source CSVs and snapshots remain private on this machine. No existing review/audit history is accessed or changed by the ingestion workflow.')
if meta:st.json({k:v for k,v in meta.items() if k not in ('files','validation')})
st.json({'registry_generation':registry['generation'],'active_selection':registry['active'],'events':registry['events'][-20:]})
