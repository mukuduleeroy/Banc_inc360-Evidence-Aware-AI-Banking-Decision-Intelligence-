"""Native UI review workflow; SQLite artifacts are isolated per test."""
from pathlib import Path
import json,hashlib,sqlite3,subprocess,sys
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from audit_store import AuditStore,AuditError
from data_access import load_index
from review_service import ReviewService
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def durable_app(tmp_path,monkeypatch):
    db=tmp_path/'ui-audit.sqlite3';monkeypatch.setenv('BANCINC_AUDIT_DB',str(db))
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    app.switch_page('views/manager_work_queue.py').run();assert not app.exception
    return app,db


def open_ui(app):
    assert app.selectbox(key='durable_reviewer').value is None
    app.selectbox(key='durable_reviewer').select('DEMO-RM-01').run()
    app.button(key='open_review_case').click().run()
    assert not app.exception


def save_ui(app,action='Approve'):
    app.selectbox(key='durable_action').select(action)
    app.text_area(key='durable_reason').set_value('Controlled local demonstration review; no banking action.')
    app.checkbox(key='durable_ack').set_value(True)
    app.button(key='save_durable_review').click().run()
    assert not app.exception


def test_real_supported_review_survives_new_app_session_and_auditor_view(durable_app):
    app,db=durable_app;open_ui(app);save_ui(app)
    storage=AuditStore(db);case=storage.cases()[0]
    assert case['state']=='APPROVED_LOCAL'
    assert [e['action'] for e in storage.timeline(case['case_id'])]==['OPEN','APPROVE']
    fresh=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    fresh.switch_page('views/manager_work_queue.py').run()
    assert not fresh.exception and 'APPROVED_LOCAL' in set(fresh.dataframe[0].value.case_status)
    assert fresh.session_state['audit']==[]
    fresh.switch_page('views/audit_validation.py').run()
    timeline=next(t.value for t in fresh.dataframe if 'event_sequence' in t.value.columns)
    assert list(timeline.action)==['OPEN','APPROVE']
    assert set(timeline.reviewer_id)=={'DEMO-RM-01'}


def test_required_reason_and_acknowledgement_have_no_success_or_event(durable_app):
    app,db=durable_app;open_ui(app)
    app.button(key='save_durable_review').click().run()
    assert any('REASON_REQUIRED' in e.value for e in app.error)
    app.text_area(key='durable_reason').set_value('Controlled reason')
    app.button(key='save_durable_review').click().run()
    assert any('PASSPORT_INSPECTION_REQUIRED' in e.value for e in app.error)
    assert AuditStore(db).summary()['events']==1


def test_caution_workflow_only_investigates(durable_app):
    app,db=durable_app
    app.selectbox(key='lane').select('CAUTION').run();open_ui(app)
    assert app.selectbox(key='durable_action').options==['Defer','Reject']
    save_ui(app,'Defer')
    assert AuditStore(db).cases()[0]['state']=='DEFERRED'


def test_replay_does_not_create_or_modify_real_audit(durable_app):
    app,db=durable_app;open_ui(app);save_ui(app)
    storage=AuditStore(db);before=storage.summary();history=storage.timeline()
    raw=hashlib.sha256((ROOT/'outputs/customer_features.csv').read_bytes()).hexdigest()
    app.switch_page('views/evidence_replay.py').run()
    app.selectbox(key='replay_kyc').select('Pending').run()
    assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='ABSTAIN'
    assert not any(b.key=='save_durable_review' for b in app.button)
    app.button(key='reset_replay').click().run()
    assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='SUPPORTED'
    assert storage.summary()==before and storage.timeline()==history
    assert raw==hashlib.sha256((ROOT/'outputs/customer_features.csv').read_bytes()).hexdigest()


def test_stale_ui_requires_refresh_and_does_not_offer_approval(feature_row,write_features,tmp_path,monkeypatch):
    path=write_features(pd.DataFrame([feature_row]));db=tmp_path/'stale.sqlite3'
    monkeypatch.setenv('BANCINC_FEATURES_PATH',str(path));monkeypatch.setenv('BANCINC_AUDIT_DB',str(db))
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();app.switch_page('views/manager_work_queue.py').run();open_ui(app)
    write_features(pd.DataFrame([dict(feature_row,kyc_status='Pending')]))
    app.run()
    assert not app.exception
    assert any('STALE EVIDENCE' in w.value for w in app.warning)
    assert app.button(key='save_durable_review').disabled
    app.text_input(key='refresh_reason').set_value('Controlled changed evidence refresh').run()
    app.button(key='refresh_review_case').click().run()
    assert not app.exception
    assert app.selectbox(key='durable_action').options==['Defer','Reject']
    assert app.checkbox(key='durable_ack').value is False
    assert [e['action'] for e in AuditStore(db).timeline()]==['OPEN','REFRESH']


def test_storage_failure_is_visible_and_not_reported_as_saved(durable_app,monkeypatch):
    app,db=durable_app;open_ui(app)
    def fail(*args,**kwargs):raise AuditError('AUDIT_WRITE_FAILED','Controlled transaction failure; no success recorded.')
    monkeypatch.setattr(ReviewService,'record_review',fail)
    save_ui(app)
    assert any('AUDIT_WRITE_FAILED' in e.value for e in app.error)
    assert AuditStore(db).summary()['events']==1
    assert not any('committed' in s.value for s in app.success)
