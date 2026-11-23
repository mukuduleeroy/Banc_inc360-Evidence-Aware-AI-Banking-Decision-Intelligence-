"""Independent synthetic transaction validation and immutable registry regression."""
import io,json,hashlib
from pathlib import Path
import pandas as pd
import pytest
import phase9_ingestion as p9
from phase9_demo import synthetic_rows,csv_bytes
from data_access import row_case,FEATURE_COLUMNS
from engine import evaluate
from acceptance_checks import decision_fingerprint

@pytest.fixture
def store(tmp_path):return p9.SnapshotStore(tmp_path/'private')
def stage(store,rows=None,fields=p9.SOURCE_FIELDS):return store.stage('synthetic.csv',io.BytesIO(csv_bytes(rows,fields)))
def candidate(store):
    u=stage(store);return store.process(u['token'],'2026-07-01')

def test_valid_transaction_contract_and_all_outcomes(store):
    u=stage(store);report=store.validate(u['token'],'2026-07-01')
    assert report['valid'] and report['source_rows']==14 and report['distinct_customers']==4 and report['distinct_accounts']==4
    m=store.process(u['token'],'2026-07-01');r=m['reconciliation']
    assert r['counts']=={'SUPPORTED':1,'CAUTION':1,'ABSTAIN':2} and r['decision_coverage']==1 and sum(r['counts'].values())==r['evaluated_customers']
    assert len(m['feature_columns'])==16 and m['feature_columns']==list(FEATURE_COLUMNS)
    assert store.state()['active']=='baseline'
    assert not list((store.root/'staging').iterdir())

@pytest.mark.parametrize('field,value,code',[
    ('transaction_date','not-a-date','INVALID_DATE'),('transaction_date','2026-06-01T00:00:00Z','INVALID_DATE'),
    ('Amount (USD)','oops','INVALID_AMOUNT'),('Amount (USD)','NaN','INVALID_AMOUNT'),('Amount (USD)','inf','INVALID_AMOUNT'),('Amount (USD)','1e99','INVALID_AMOUNT'),
    ('Customer ID','','IDENTIFIERS'),('Account ID','../x','IDENTIFIERS'),('Transaction ID','','IDENTIFIERS'),
    ('account_customer_id','SYNTHETIC-OTHER','OWNERSHIP'),('Type','UNKNOWN','TRANSACTION_TYPE'),
    ('dr_cr_indicator','WRONG','DIRECTION'),('products_held','Imaginary Account','PRODUCT_EVIDENCE'),
    ('service_reasons','=DANGEROUS()','UNSAFE_TEXT'),('customer_segment','Imaginary','SEGMENT')])
def test_invalid_source_fields_fail_closed(store,field,value,code):
    rows=synthetic_rows();rows[0][field]=value;u=stage(store,rows);v=store.validate(u['token'],'2026-07-01')
    assert not v['valid'] and code in {e['code'] for e in v['errors']}
    with pytest.raises(p9.IngestionError,match='Validation failed'):store.process(u['token'],'2026-07-01')
    assert store.state()['active']=='baseline' and not store.state()['snapshots']

@pytest.mark.parametrize('cutoff',['','2026-02-31','01/07/2026','2026-07-01T00:00:00'])
def test_explicit_valid_observation_date_required(store,cutoff):
    u=stage(store);assert not store.validate(u['token'],cutoff)['valid']

def test_missing_schema_and_currency_rejected(store):
    u=store.stage('missing.csv',io.BytesIO(b'Customer ID\nSYNTHETIC-X\n'));v=store.validate(u['token'],'2026-07-01')
    assert not v['valid'] and 'Account ID' in v['missing_fields']
    u=stage(store,[{**r,'Currency':'ZAR'} for r in synthetic_rows()],(*p9.SOURCE_FIELDS,'Currency'))
    v=store.validate(u['token'],'2026-07-01');assert v['counts']['unsupported_currencies']==14 and not v['valid']


def test_identical_duplicates_and_repeated_customer_ids_follow_builder(store):
    rows=synthetic_rows();rows.append(dict(rows[0]));u=stage(store,rows);v=store.validate(u['token'],'2026-07-01')
    assert v['valid'] and v['counts']['duplicate_records']==1
    m=store.process(u['token'],'2026-07-01');assert m['reconciliation']['accepted_source_rows']==14 and m['reconciliation']['source_rows']==15
    assert m['reconciliation']['counts']=={'SUPPORTED':1,'CAUTION':1,'ABSTAIN':2}


def test_conflicting_transaction_and_account_ownership_rejected(store):
    rows=synthetic_rows();rows.append({**rows[0],'Amount (USD)':'7'})
    u=stage(store,rows);assert not store.validate(u['token'],'2026-07-01')['valid']
    rows=synthetic_rows();rows[5]['Account ID']=rows[0]['Account ID'];u=stage(store,rows)
    assert any(e['code']=='OWNERSHIP' for e in store.validate(u['token'],'2026-07-01')['errors'])

@pytest.mark.parametrize('field',['kyc_status','customer_status','account_status','products_held'])
def test_missing_evidence_stays_unknown_and_abstains(store,field):
    rows=synthetic_rows()
    for r in rows:r[field]=''
    u=stage(store,rows);v=store.validate(u['token'],'2026-07-01');assert v['valid'] and v['warnings']
    m=store.process(u['token'],'2026-07-01');assert m['reconciliation']['counts']['SUPPORTED']==0 and m['reconciliation']['counts']['ABSTAIN']==4


def test_unknown_segment_not_injected_into_decision(store):
    rows=synthetic_rows()
    for r in rows:r['customer_segment']=''
    u=stage(store,rows);m=store.process(u['token'],'2026-07-01');assert m['reconciliation']['counts']=={'SUPPORTED':1,'CAUTION':1,'ABSTAIN':2}


def test_post_cutoff_only_customers_rejected_and_future_events_not_predictors(store):
    rows=synthetic_rows();rows.append({**rows[0],'Customer ID':'SYNTHETIC-FUTURE','account_customer_id':'SYNTHETIC-FUTURE','Account ID':'FUTURE-ACCOUNT','Transaction ID':'FUTURE-TX','transaction_date':'01/08/2026'})
    u=stage(store,rows);assert not store.validate(u['token'],'2026-07-01')['valid']
    rows=synthetic_rows();rows.append({**rows[0],'Transaction ID':'FUTURE-TX','transaction_date':'01/08/2026','Amount (USD)':'9000'})
    u=stage(store,rows);m=store.process(u['token'],'2026-07-01');_,ix=store.inspect(m['snapshot_id'])
    r=next(v for v in ix.records if dict(zip(FEATURE_COLUMNS,v.values))['customer_id']=='SYNTHETIC-SUPPORTED')
    assert ix.customer_values(r.alias)['qualifying_events_180d']==5

@pytest.mark.parametrize('name',['../x.csv','/tmp/x.csv','folder/x.csv','folder\\x.csv','x.zip','x.csv\n'])
def test_filename_traversal_and_extensions_rejected(store,name):
    with pytest.raises(p9.IngestionError):store.stage(name,io.BytesIO(csv_bytes()))
    assert not list((store.root/'staging').iterdir())

@pytest.mark.parametrize('content',[b'\xff\xfe',b'"unterminated',b'',b'a,a\n1,2\n',b'a\x00,b\n'])
def test_malformed_csv_rejected_safely(store,content):
    try:u=store.stage('bad.csv',io.BytesIO(content))
    except p9.IngestionError:return
    assert not store.validate(u['token'],'2026-07-01')['valid']


def test_file_row_and_field_limits(store,monkeypatch):
    monkeypatch.setattr(p9,'MAX_BYTES',10)
    with pytest.raises(p9.IngestionError,match='5 MiB'):stage(store)
    assert not list((store.root/'staging').iterdir())
    monkeypatch.setattr(p9,'MAX_BYTES',5*1024*1024);monkeypatch.setattr(p9,'MAX_ROWS',2)
    u=stage(store);v=store.validate(u['token'],'2026-07-01');assert not v['valid'] and any(e['code']=='ROW_LIMIT' for e in v['errors'])
    monkeypatch.setattr(p9,'MAX_ROWS',25000);rows=synthetic_rows();rows[0]['service_reasons']='x'*2049
    u=stage(store,rows);assert not store.validate(u['token'],'2026-07-01')['valid']


def test_staging_lineage_and_cleanup(store):
    u=stage(store);(store.root/'staging'/(u['token']+'.csv')).write_bytes(b'changed')
    with pytest.raises(p9.IngestionError):store.process(u['token'],'2026-07-01')
    store.cleanup(u['token']);assert not list((store.root/'staging').iterdir())


def test_engine_priority_gates_and_reasons_are_exactly_reused(store):
    m=candidate(store);_,ix=store.inspect(m['snapshot_id'])
    for r in ix.records:
        raw=ix.customer_values(r.alias);expected=evaluate(row_case(raw));actual=ix.passport(r.alias)
        assert expected['gates']==actual['gates'] and expected['reason_codes']==actual['reason_codes']
        assert expected['rating']==r.rating and expected['priority_score']==r.priority
        assert r.priority==.45*min(raw['recency_days']/90,1)+.35*raw['relationship_activity_percentile']+.2*int(raw['service_issue'])
    assert m['decision_fingerprint']==decision_fingerprint(ix)


def test_unique_immutable_snapshots_activation_rollback_and_no_rewrite(store):
    a=candidate(store);path=store.root/'snapshots'/a['snapshot_id'];before={p.name:p.read_bytes() for p in path.iterdir()}
    b=candidate(store);assert a['snapshot_id']!=b['snapshot_id']
    store.activate(a['snapshot_id']);assert store.state()['active']==a['snapshot_id']
    store.activate(b['snapshot_id']);assert store.state()['active']==b['snapshot_id']
    store.rollback();assert store.state()['active']=='baseline'
    assert before=={p.name:p.read_bytes() for p in path.iterdir()}

@pytest.mark.parametrize('filename',['source.csv','source.zip','customer_features.csv','customer_features.manifest.json','data_audit.json','decisions.json','snapshot.json'])
def test_tampered_snapshot_cannot_activate_or_displace_previous(store,filename):
    a=candidate(store);b=candidate(store);store.activate(a['snapshot_id'])
    (store.root/'snapshots'/b['snapshot_id']/filename).write_bytes(b'changed')
    with pytest.raises(p9.IngestionError):store.activate(b['snapshot_id'])
    assert store.state()['active']==a['snapshot_id']
    store.rollback();assert store.state()['active']=='baseline'


def test_atomic_activation_failure_retains_previous(store,monkeypatch):
    a=candidate(store);b=candidate(store);store.activate(a['snapshot_id']);replace=p9.os.replace
    def reject(src,dst):
        if Path(dst).name=='registry.json':raise OSError('controlled disk failure')
        return replace(src,dst)
    monkeypatch.setattr(p9.os,'replace',reject)
    with pytest.raises(OSError):store.activate(b['snapshot_id'])
    assert store.state()['active']==a['snapshot_id']
    assert not list(store.root.glob('.pending-*'))


def test_registry_recovers_last_committed_state_and_ignores_interrupted_writes(store):
    a=candidate(store);store.activate(a['snapshot_id']);store.rollback()
    previous=json.loads((store.root/'registry.previous.json').read_text())['payload']
    (store.root/'.pending-abandoned').write_text('incomplete');(store.root/'registry.json').write_text('interrupted')
    assert store.state()==previous
    assert p9.SnapshotStore(store.root).state()==previous
    store.rollback();assert store.state()['active']=='baseline'


def test_registry_failure_never_resets_or_deletes_snapshots(store):
    a=candidate(store)
    for name in ('registry.json','registry.previous.json'):(store.root/name).write_text('broken')
    with pytest.raises(p9.IngestionError):store.state()
    assert (store.root/'snapshots'/a['snapshot_id']).is_dir()

@pytest.mark.parametrize('token',['../x','x','/tmp/y','a'*33])
def test_snapshot_and_cleanup_paths_confined(store,token):
    with pytest.raises(p9.IngestionError):store.inspect(token)
    with pytest.raises(p9.IngestionError):store.cleanup(token)


def test_refuses_unmanaged_or_symlink_storage(tmp_path):
    existing=tmp_path/'existing';existing.mkdir();(existing/'history.sqlite3').write_bytes(b'protected')
    with pytest.raises(p9.IngestionError):p9.SnapshotStore(existing)
    link=tmp_path/'link';link.symlink_to(existing,target_is_directory=True)
    with pytest.raises(p9.IngestionError):p9.SnapshotStore(link)
    assert (existing/'history.sqlite3').read_bytes()==b'protected'
