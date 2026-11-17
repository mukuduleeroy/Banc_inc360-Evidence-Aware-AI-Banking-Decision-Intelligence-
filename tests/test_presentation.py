"""Disposable test databases only; presentation reset must retain existing history."""
from pathlib import Path
import json,hashlib,subprocess,sys
import pandas as pd
import pytest
from presentation import initialize,read_config,environment
from audit_store import AuditStore,AuditError
from review_service import ReviewService
from data_access import load_index

@pytest.fixture
def source(feature_row,write_features):
 a=dict(feature_row);b=dict(feature_row,customer_id='SYNTHETIC-2',kyc_status='Pending')
 return write_features(pd.DataFrame([a,b]))

def test_reset_retains_old_history_and_isolates_new_database(tmp_path,source):
 root=tmp_path/'managed';a=initialize(root,source);_,db=read_config(root);service=ReviewService(AuditStore(db),features_path=source);case=service.open_case(a['aliases']['SUPPORTED'],'DEMO-RM-01','open');service.record_review(case['case_id'],'DEMO-RM-01','APPROVE','Synthetic test passport inspected.',case['revision'],case['current_snapshot_id'],'approve',True)
 b=initialize(root,source,True);_,new=read_config(root);assert new!=db;assert AuditStore(new).summary()['events']==0;assert AuditStore(db).summary()['events']==2;assert AuditStore(root/b['previous_backup']).summary()['events']==2;assert a['aliases']==b['aliases']

def test_unmanaged_directory_never_reset(tmp_path,source):
 p=tmp_path/'unmanaged';p.mkdir();(p/'important.txt').write_text('retain')
 with pytest.raises(ValueError):initialize(p,source,True)
 assert (p/'important.txt').read_text()=='retain'

def test_existing_demo_requires_explicit_reset(tmp_path,source):
 p=tmp_path/'demo';initialize(p,source)
 with pytest.raises(FileExistsError):initialize(p,source)

def test_path_traversal_rejected(tmp_path):
 (tmp_path/'demo.json').write_text(json.dumps({'marker':'bancinc-managed-demo-v1','database':'../review_audit.sqlite3'}))
 with pytest.raises(ValueError):read_config(tmp_path)

def test_environment_is_private_and_fail_closed(tmp_path,source):
 p=tmp_path/'demo';a=initialize(p,source);env=environment(p);assert Path(env['BANCINC_AUDIT_DB']).parent==p;assert a['bank_authorization'] is False and a['automatic_outreach'] is False;assert all(v is None or v.startswith('C-') for v in a['aliases'].values());source.write_text(source.read_text()+'\n')
 with pytest.raises(ValueError):environment(p)

def test_fresh_process_review_persistence_and_no_action(tmp_path,source):
 p=tmp_path/'demo';a=initialize(p,source);_,db=read_config(p);s=ReviewService(AuditStore(db),features_path=source);c=s.open_case(a['aliases']['SUPPORTED'],'DEMO-RM-01','open');e=s.record_review(c['case_id'],'DEMO-RM-01','APPROVE','Synthetic local review only.',c['revision'],c['current_snapshot_id'],'save',True)
 code="from audit_store import AuditStore;import sys,json;s=AuditStore(sys.argv[1]);print(json.dumps({'state':s.cases()[0]['state'],'events':s.summary()['events'],'snapshot':s.snapshot(s.cases()[0]['current_snapshot_id'])['payload']}))"
 r=json.loads(subprocess.check_output([sys.executable,'-c',code,str(db)],text=True));assert r['state']=='APPROVED_LOCAL' and r['events']==2;assert r['snapshot']['automatic_outreach'] is False and r['snapshot']['bank_authorization'] is False;assert 'SYNTHETIC-1' not in json.dumps(r)

def test_full_nine_view_workflow_and_replay_isolation(tmp_path,source,monkeypatch):
 from streamlit.testing.v1 import AppTest
 from ui_shell import PAGES
 before=hashlib.sha256(source.read_bytes()).hexdigest();root=tmp_path/'full-demo';initialize(root,source);_,db=read_config(root);monkeypatch.setenv('BANCINC_AUDIT_DB',str(db));monkeypatch.setenv('BANCINC_FEATURES_PATH',str(source))
 app=AppTest.from_file('app.py',default_timeout=120).run()
 for slug,title,_ in PAGES:
  app.switch_page('views/'+slug+'.py').run();assert not app.exception and app.title[0].value==title
 app.switch_page('views/evidence_replay.py').run();app.selectbox(key='replay_kyc').select('Pending').run();assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='ABSTAIN';assert not any(b.key=='save_durable_review' for b in app.button)
 app.button(key='reset_replay').click().run();assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='SUPPORTED';assert AuditStore(db).summary()['events']==0
 app.switch_page('views/manager_work_queue.py').run();app.selectbox(key='durable_reviewer').select('DEMO-RM-01').run();app.button(key='open_review_case').click().run();app.text_area(key='durable_reason').set_value('Synthetic full-system test review only.');app.checkbox(key='durable_ack').set_value(True);app.button(key='save_durable_review').click().run();assert not app.exception
 fresh=AppTest.from_file('app.py',default_timeout=120).run();fresh.switch_page('views/audit_validation.py').run();assert not fresh.exception;assert AuditStore(db).cases()[0]['state']=='APPROVED_LOCAL';assert AuditStore(db).summary()['events']==2;assert hashlib.sha256(source.read_bytes()).hexdigest()==before
 for table in fresh.dataframe:assert 'SYNTHETIC-1' not in table.value.to_json()

def test_demo_stale_evidence_requires_refresh(tmp_path,source,write_features):
 root=tmp_path/'stale';a=initialize(root,source);_,db=read_config(root);s=ReviewService(AuditStore(db),features_path=source);c=s.open_case(a['aliases']['SUPPORTED'],'DEMO-RM-01','open')
 changed=pd.read_csv(source);changed.loc[0,'kyc_status']='Pending';path=write_features(changed,'changed.csv');other=ReviewService(AuditStore(db),features_path=path)
 with pytest.raises(AuditError,match='stale'):other.record_review(c['case_id'],'DEMO-RM-01','APPROVE','Stale synthetic context.',c['revision'],c['current_snapshot_id'],'stale',True)
 assert AuditStore(db).summary()['events']==1
