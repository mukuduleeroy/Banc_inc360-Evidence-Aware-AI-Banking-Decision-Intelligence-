"""Explicit synthetic review evidence; real-data persistence is demonstrated separately."""
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta
from pathlib import Path
import json,sqlite3,copy
import pandas as pd
import pytest
from audit_store import AuditStore,AuditError
from review_service import ReviewService,CurrentEvidence,normalize_passport
from data_access import build_index
from replay import simulate

@pytest.fixture
def review(tmp_path,feature_row):
    index=build_index(pd.DataFrame([feature_row]),b'synthetic audit unit key',dataset_hash='a'*64,policy_hash='b'*64,cutoff='2026-07-01')
    alias=index.records[0].alias
    context=CurrentEvidence(alias,index.passport(alias),'a'*64,'c'*64,'b'*64,'d'*64,'2026-07-01')
    holder={'context':context};store=AuditStore(tmp_path/'audit.sqlite3')
    service=ReviewService(store,provider=lambda requested:holder['context'])
    return store,service,holder,index


def opened(review):
    store,service,holder,index=review
    return service.open_case(holder['context'].alias,'DEMO-RM-01','open-request')

def record(service,case,**changes):
    args=dict(case_id=case['case_id'],reviewer_id='DEMO-RM-01',action='APPROVE',reason='Controlled local prototype review only.',expected_revision=case['revision'],viewed_snapshot_id=case['current_snapshot_id'],request_id='review-request',passport_reviewed=True)
    args.update(changes);return service.record_review(**args)


def test_supported_review_persistence_snapshot_and_feature_refs(review):
    store,service,holder,index=review;case=opened(review);result=record(service,case)
    assert result['state']=='APPROVED_LOCAL' and result['revision']==2
    assert store.case(case['case_id'])['state']=='APPROVED_LOCAL'
    history=store.timeline(case['case_id']);assert [e['action'] for e in history]==['OPEN','APPROVE']
    assert all(e['reviewer_id']=='DEMO-RM-01' for e in history)
    assert all(datetime.fromisoformat(e['event_utc']).utcoffset()==timedelta(0) for e in history)
    snap=store.snapshot(result['snapshot_id']);payload=snap['payload']
    assert len(payload['gates'])==6 and payload['outcome']=='SUPPORTED'
    assert payload['bank_authorization'] is False and payload['automatic_outreach'] is False
    assert payload['method']['name']=='deterministic_rules'
    assert payload['traceability_level']=='FEATURE_LEVEL' and payload['source_event_references']==[]
    assert len(snap['evidence_references'])==8
    assert all(r['source_event_reference'] is None for r in snap['evidence_references'])
    assert {r['temporal_kind'] for r in snap['evidence_references']}=={'HISTORICAL','CURRENT_SNAPSHOT'}
    assert all(r['cutoff'] is None for r in snap['evidence_references'] if r['temporal_kind']=='CURRENT_SNAPSHOT')
    restarted=AuditStore(store.path)
    assert restarted.summary()==store.summary() and restarted.timeline(case['case_id'])==history
    assert restarted.snapshot(result['snapshot_id'])['snapshot_hash']==snap['snapshot_hash']

@pytest.mark.parametrize('action,state',[('DEFER','DEFERRED'),('REJECT','REJECTED')])
def test_supported_other_review_outcomes(review,action,state):
    store,service,_,_=review;result=record(service,opened(review),action=action)
    assert result['state']==state

@pytest.mark.parametrize('rating',['CAUTION','ABSTAIN'])
def test_non_supported_cannot_approve_but_can_defer(review,feature_row,rating):
    store,service,holder,_=review
    row=dict(feature_row,qualifying_events_180d=3 if rating=='CAUTION' else 5,customer_status='Active' if rating=='CAUTION' else 'Restricted')
    index=build_index(pd.DataFrame([row]),b'synthetic audit unit key',dataset_hash='a'*64,policy_hash='b'*64,cutoff='2026-07-01')
    holder['context']=replace(holder['context'],passport=index.passport(index.records[0].alias))
    case=opened(review);assert case['state']=='INVESTIGATION_REQUIRED'
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='APPROVAL_REQUIRES_SUPPORTED' and store.summary()['events']==1
    assert record(service,case,action='DEFER')['state']=='DEFERRED'

@pytest.mark.parametrize('reviewer',[None,'','UNKNOWN',"DEMO-RM-01' OR 1=1 --"])
def test_explicit_valid_reviewer_required(review,reviewer):
    store,service,holder,_=review
    with pytest.raises(AuditError) as exc:service.open_case(holder['context'].alias,reviewer,'open-request')
    assert exc.value.code=='REVIEWER_REQUIRED' and store.summary()['events']==0

@pytest.mark.parametrize('reason',[None,'','   ','x'*2001],ids=['none','empty','whitespace','too-long'])
def test_required_bounded_reason(review,reason):
    store,service,_,_=review;case=opened(review)
    with pytest.raises(AuditError) as exc:record(service,case,reason=reason)
    assert exc.value.code=='REASON_REQUIRED' and store.summary()['events']==1


def test_inspection_and_exact_snapshot_revision_required(review):
    store,service,_,_=review;case=opened(review)
    with pytest.raises(AuditError) as exc:record(service,case,passport_reviewed=False)
    assert exc.value.code=='PASSPORT_INSPECTION_REQUIRED'
    with pytest.raises(AuditError) as exc:record(service,case,viewed_snapshot_id='wrong')
    assert exc.value.code=='REVIEW_CONFLICT' and store.summary()['events']==1


def test_duplicate_event_idempotency_and_payload_conflict(review):
    store,service,_,_=review;case=opened(review)
    first=record(service,case);again=record(service,case)
    assert first['event_id']==again['event_id'] and again['idempotent'] is True
    assert store.summary()['events']==2
    with pytest.raises(AuditError) as exc:record(service,case,reason='Different content')
    assert exc.value.code=='IDEMPOTENCY_CONFLICT'

@pytest.mark.parametrize('field',['dataset_hash','manifest_hash','policy_hash'])
def test_stale_fingerprints_block_until_explicit_refresh(review,field):
    store,service,holder,_=review;case=opened(review);old_snapshot=store.snapshot(case['current_snapshot_id'])
    holder['context']=replace(holder['context'],**{field:'e'*64})
    assert service.status(case,holder['context'])=='STALE'
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='STALE_EVIDENCE' and store.summary()['events']==1
    service.refresh_case(case['case_id'],'DEMO-RM-02','Explicitly refresh changed evidence.',case['revision'],'refresh-request')
    current=store.case(case['case_id'])
    assert current['state']=='OPEN' and current['revision']==2
    assert store.snapshot(case['current_snapshot_id'])['snapshot_hash']==old_snapshot['snapshot_hash']
    result=record(service,current,request_id='after-refresh')
    assert result['state']=='APPROVED_LOCAL' and [e['action'] for e in store.timeline(case['case_id'])]==['OPEN','REFRESH','APPROVE']


def test_changed_policy_version_is_stale(review):
    store,service,holder,_=review;case=opened(review)
    holder['context']=replace(holder['context'],policy_hash='e'*64,passport=dict(holder['context'].passport,policy_version='controlled-test-v2'))
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='STALE_EVIDENCE'


def test_changed_outcome_even_with_same_hash_cannot_reuse_supported(review,feature_row):
    store,service,holder,_=review;case=opened(review)
    index=build_index(pd.DataFrame([dict(feature_row,customer_status='Restricted')]),b'synthetic audit unit key',dataset_hash='a'*64,policy_hash='b'*64,cutoff='2026-07-01')
    holder['context']=replace(holder['context'],passport=index.passport(index.records[0].alias))
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='STALE_EVIDENCE' and store.summary()['events']==1


def test_write_failure_rolls_back_snapshot_refs_and_state(review,monkeypatch):
    store,service,_,_=review;case=opened(review);before=store.summary()
    def fail(*args):raise sqlite3.OperationalError('controlled storage failure')
    monkeypatch.setattr(service,'_insert_event',fail)
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='AUDIT_WRITE_FAILED' and store.summary()==before
    assert store.case(case['case_id'])['state']=='OPEN'


def test_evidence_change_before_commit_rolls_back_all_writes(review,monkeypatch):
    store,service,holder,_=review;case=opened(review);before=store.summary();original=service._assert_still_current;calls=[]
    def guard(context):
        calls.append(1)
        if len(calls)==2:holder['context']=replace(holder['context'],dataset_hash='e'*64)
        original(context)
    monkeypatch.setattr(service,'_assert_still_current',guard)
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='STALE_EVIDENCE' and store.summary()==before


def test_concurrent_reviews_use_optimistic_revision(review):
    store,service,_,_=review;case=opened(review)
    def attempt(n):
        try:return record(service,case,request_id='parallel-'+str(n))['state']
        except AuditError as exc:return exc.code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,[1,2]))
    assert sorted(results)==sorted(['APPROVED_LOCAL','REVIEW_CONFLICT'])
    assert store.summary()['events']==2


def test_events_snapshots_references_append_only_and_no_silent_state_edit(review):
    store,service,_,_=review;case=opened(review);record(service,case)
    for sql in ["UPDATE review_events SET reason='changed'","DELETE FROM review_events","UPDATE passport_snapshots SET outcome='ABSTAIN'","DELETE FROM passport_snapshots","DELETE FROM evidence_references","UPDATE review_cases SET state='REJECTED'"]:
        with pytest.raises(sqlite3.IntegrityError):
            with store.transaction() as con:con.execute(sql)
    assert [e['action'] for e in store.timeline(case['case_id'])]==['OPEN','APPROVE']


def test_snapshot_corruption_is_detected_if_owner_bypasses_trigger(review):
    store,service,_,_=review;case=opened(review)
    with store.transaction() as con:
        con.execute('DROP TRIGGER passport_snapshots_no_update')
        con.execute('UPDATE passport_snapshots SET normalized_json=? WHERE snapshot_id=?',('{}',case['current_snapshot_id']))
    with pytest.raises(AuditError) as exc:store.snapshot(case['current_snapshot_id'])
    assert exc.value.code=='SNAPSHOT_INTEGRITY_FAILURE'


def test_sql_is_parameterized_and_private_identity_not_persisted(review,feature_row):
    store,service,_,_=review;case=opened(review)
    reason="Controlled O'Reilly review; DROP TABLE review_events; --"
    record(service,case,reason=reason)
    text=json.dumps(store.timeline(case['case_id']))+json.dumps(store.snapshot(store.case(case['case_id'])['current_snapshot_id']))
    assert feature_row['customer_id'] not in text
    assert store.timeline(case['case_id'])[-1]['reason']==reason
    assert store.summary()['events']==2


@pytest.mark.parametrize('overrides',[{}, {'kyc_status':'Pending'}])
def test_replay_cannot_enter_real_case_channel(review,overrides):
    store,service,holder,index=review;before=store.summary()
    simulated=simulate(index,index.records[0].alias,overrides)['simulated']
    holder['context']=replace(holder['context'],passport=simulated)
    with pytest.raises(AuditError) as exc:opened(review)
    assert exc.value.code=='SIMULATION_FORBIDDEN' and store.summary()==before


def test_requested_identity_must_match_current_provider(review):
    store,service,_,_=review
    with pytest.raises(AuditError) as exc:service.open_case('C-'+'F'*24,'DEMO-RM-01','wrong-identity')
    assert exc.value.code=='IDENTITY_MISMATCH' and store.summary()['events']==0


def test_missing_source_event_references_remain_feature_level(review):
    store,service,_,_=review;case=opened(review);snapshot=store.snapshot(case['current_snapshot_id'])
    assert snapshot['payload']['source_event_references']==[]
    assert all(r['reference_level']=='FEATURE_LEVEL' and r['source_event_reference'] is None for r in snapshot['evidence_references'])

def test_policy_file_change_requires_reload_without_modifying_engine(review,monkeypatch):
    import review_service
    store,_,_,_=review
    default=ReviewService(store,features_path='unused-features.csv')
    monkeypatch.setattr(review_service,'policy_fingerprint',lambda:'e'*64)
    with pytest.raises(AuditError) as exc:default.current('C-'+'A'*24)
    assert exc.value.code=='POLICY_RELOAD_REQUIRED' and store.summary()['events']==0


def test_fresh_default_adapter_reads_changed_feature_bytes(review,feature_row,write_features):
    store,_,_,_=review;path=write_features(pd.DataFrame([feature_row]))
    service=ReviewService(store,features_path=path)
    alias=load_actual_alias(path)
    case=service.open_case(alias,'DEMO-RM-01','real-adapter-open')
    write_features(pd.DataFrame([dict(feature_row,kyc_status='Pending')]))
    with pytest.raises(AuditError) as exc:record(service,case)
    assert exc.value.code=='STALE_EVIDENCE' and store.summary()['events']==1


def load_actual_alias(path):
    from data_access import load_index
    return load_index(path).records[0].alias
