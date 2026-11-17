"""Actual local feature evidence, durable process restart, stale alternate build and backup.
Uses a fresh, separate demo DB; never rewrites canonical features or prior history.
"""
from pathlib import Path
from dataclasses import replace
import argparse,sys,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from audit_store import AuditStore,AuditError
from review_service import ReviewService
from data_access import load_index
from replay import simulate


def restart_read(db,case_id):
    code="from audit_store import AuditStore;import sys,json;s=AuditStore(sys.argv[1]);c=s.case(sys.argv[2]);print(json.dumps({'state':c['state'],'events':[e['action'] for e in s.timeline(c['case_id'])],'summary':s.summary()}))"
    return json.loads(subprocess.check_output([sys.executable,'-c',code,str(db),case_id],cwd=ROOT,text=True))


def verify(features,alternate,db,out,backup):
    features,db,out=Path(features),Path(db),Path(out)
    before=hashlib.sha256(features.read_bytes()).hexdigest();index=load_index(features)
    alt=load_index(alternate) if alternate else None
    available={r.alias for r in alt.records} if alt else {r.alias for r in index.records}
    alias=next(r.alias for r in index.records if r.rating=='SUPPORTED' and r.alias in available)
    storage=AuditStore(db)
    if storage.summary()['cases'] or storage.summary()['events']:raise ValueError('Choose a new empty demonstration audit database; existing history is preserved.')
    service=ReviewService(storage,features_path=features)
    case=service.open_case(alias,'DEMO-RM-01','actual-open')
    approved=service.record_review(case['case_id'],'DEMO-RM-01','APPROVE','Presentation rehearsal: current supported passport inspected; local prototype outcome only.',case['revision'],case['current_snapshot_id'],'actual-approve',True)
    restart=restart_read(db,case['case_id'])
    assert restart['state']=='APPROVED_LOCAL' and restart['events']==['OPEN','APPROVE']
    original_snapshot=storage.snapshot(approved['snapshot_id']);original_hash=original_snapshot['snapshot_hash'];before_replay=storage.summary()
    replay=simulate(index,alias,{'kyc_status':'Pending'})
    assert replay['simulated']['rating']=='ABSTAIN' and not replay['simulated']['action_authorized']
    assert simulate(index,alias)['simulated']['rating']=='SUPPORTED' and storage.summary()==before_replay
    result={'source':'actual authorized local feature builds','canonical_dataset_hash':index.dataset_hash,'canonical_cutoff':index.cutoff,'canonical_counts':index.counts,'restart_after_approval':restart,'replay_does_not_write_review_events':True,'source_traceability':'FEATURE_LEVEL; source transaction IDs are not retained in the verified feature artifact','source_event_references':[]}
    if alt:
        second=ReviewService(storage,features_path=alternate);current=storage.case(case['case_id'])
        try:second.record_review(current['case_id'],'DEMO-RM-02','APPROVE','Attempt against an older observation version.',current['revision'],current['current_snapshot_id'],'stale-attempt',True)
        except AuditError as exc:
            assert exc.code=='STALE_EVIDENCE';result['stale_dataset_rejection']=exc.code
        else:raise AssertionError('Stale review unexpectedly accepted')
        assert storage.summary()==before_replay
        second.refresh_case(current['case_id'],'DEMO-RM-02','Refresh against independently built January observation; retain prior history.',current['revision'],'actual-refresh')
        refreshed=storage.case(case['case_id'])
        result['alternate_dataset_hash']=alt.dataset_hash;result['alternate_cutoff']=alt.cutoff;result['alternate_counts']=alt.counts;result['alternate_case_outcome']=alt.passport(alias)['rating']
        second.record_review(current['case_id'],'DEMO-RM-02','DEFER','Further investigation of the refreshed observation is required; no bank action.',refreshed['revision'],refreshed['current_snapshot_id'],'actual-defer',True)
        assert storage.snapshot(approved['snapshot_id'])['snapshot_hash']==original_hash
    result['final_restart']=restart_read(db,case['case_id']);result['historical_snapshot_unchanged']=storage.snapshot(approved['snapshot_id'])['snapshot_hash']==original_hash
    storage.backup(backup);assert AuditStore(backup).summary()==storage.summary();result['backup_verified']=True
    result['canonical_csv_unchanged']=before==hashlib.sha256(features.read_bytes()).hexdigest();assert result['canonical_csv_unchanged']
    out.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--features',default='outputs/customer_features.csv');p.add_argument('--alternate');p.add_argument('--db',required=True);p.add_argument('--out',default='outputs/phase4/persistence_demo.json');p.add_argument('--backup',required=True);a=p.parse_args();verify(a.features,a.alternate,a.db,a.out,a.backup)
