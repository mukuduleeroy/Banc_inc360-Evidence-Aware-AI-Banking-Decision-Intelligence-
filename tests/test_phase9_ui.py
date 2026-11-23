"""Native companion interactions; isolated storage and synthetic uploads only."""
from pathlib import Path
import io
import pytest
from streamlit.testing.v1 import AppTest
import streamlit as st
from phase9_demo import csv_bytes
from phase9_ingestion import SnapshotStore
ROOT=Path(__file__).resolve().parents[1]

class Upload(io.BytesIO):
    name='synthetic.csv';file_id='controlled-synthetic'
    @property
    def size(self):return len(self.getvalue())

@pytest.fixture
def app(tmp_path,monkeypatch):
    monkeypatch.setenv('BANCINC_PHASE9_STORAGE',str(tmp_path/'private'));monkeypatch.setenv('BANCINC_RUNTIME','LOCAL')
    original_option=st.get_option
    monkeypatch.setattr(st,'get_option',lambda key:5 if key=='server.maxUploadSize' else original_option(key))
    monkeypatch.setattr(st,'file_uploader',lambda *a,**kw:Upload(csv_bytes()))
    a=AppTest.from_file(str(ROOT/'phase9_app.py'),default_timeout=120).run();assert not a.exception
    return a,tmp_path/'private'

def test_complete_validate_process_preview_activate_inspect_rollback(app):
    a,path=app;assert a.title[0].value=='Dataset Ingestion & Refresh'
    assert a.button(key='p9_process').disabled
    a.button(key='p9_validate').click().run();assert not a.exception
    assert a.session_state['p9_validation']['valid']
    a.button(key='p9_process').click().run();assert not a.exception
    token=a.session_state['p9_candidate'];assert SnapshotStore(path).state()['active']=='baseline'
    a.selectbox(key='p9_preview').select(token).run();assert not a.exception
    metrics={m.label:m.value for m in a.metric};assert metrics=={'Evaluated customers':'4','SUPPORTED':'1','CAUTION':'1','ABSTAIN':'2'}
    gates=next(t.value for t in a.dataframe if 'gate' in t.value.columns);assert len(gates)==6
    a.button(key='p9_activate').click().run();assert not a.exception
    assert SnapshotStore(path).state()['active']==token
    a.button(key='p9_rollback').click().run();assert not a.exception
    assert a.selectbox(key='p9_preview').value=='baseline' and SnapshotStore(path).state()['active']=='baseline'
    assert not any(b.key in ('save_durable_review','record_decision') for b in a.button)


def test_invalid_upload_blocks_processing_and_cannot_activate(app,monkeypatch):
    a,path=app
    bad=Upload(b'Customer ID\nSYNTHETIC-ONLY\n');bad.file_id='invalid-synthetic'
    monkeypatch.setattr(st,'file_uploader',lambda *args,**kw:bad)
    a.run();a.button(key='p9_validate').click().run();assert not a.exception
    assert not a.session_state['p9_validation']['valid'] and a.button(key='p9_process').disabled and a.button(key='p9_activate').disabled
    assert SnapshotStore(path).state()['active']=='baseline'


def test_explicit_cleanup_and_cutoff_change_clear_staging(app):
    a,path=app;a.button(key='p9_validate').click().run()
    assert list((path/'staging').iterdir())
    a.text_input(key='p9_cutoff').set_value('2026-08-01').run()
    assert not a.exception and not list((path/'staging').iterdir()) and a.button(key='p9_process').disabled
    a.button(key='p9_validate').click().run();a.button(key='p9_cleanup').click().run()
    assert not a.exception and not list((path/'staging').iterdir())


def test_non_local_companion_refused(tmp_path,monkeypatch):
    original_option=st.get_option
    monkeypatch.setattr(st,'get_option',lambda key:5 if key=='server.maxUploadSize' else original_option(key))
    monkeypatch.setenv('BANCINC_RUNTIME','CLOUD');monkeypatch.setenv('BANCINC_PHASE9_STORAGE',str(tmp_path/'private'))
    a=AppTest.from_file(str(ROOT/'phase9_app.py')).run()
    assert any('local runtime only' in e.value for e in a.error)
    assert not (tmp_path/'private').exists()


def test_real_uploader_api_renders_with_transport_limit(tmp_path,monkeypatch):
    monkeypatch.setenv('BANCINC_RUNTIME','LOCAL');monkeypatch.setenv('BANCINC_PHASE9_STORAGE',str(tmp_path/'private'))
    original=st.get_option
    monkeypatch.setattr(st,'get_option',lambda key:5 if key=='server.maxUploadSize' else original(key))
    a=AppTest.from_file(str(ROOT/'phase9_app.py'),default_timeout=120).run()
    assert not a.exception and a.title[0].value=='Dataset Ingestion & Refresh'
    assert a.button(key='p9_process').disabled


def test_missing_transport_limit_refuses_upload_interface(tmp_path,monkeypatch):
    monkeypatch.setenv('BANCINC_RUNTIME','LOCAL');monkeypatch.setenv('BANCINC_PHASE9_STORAGE',str(tmp_path/'private'))
    original=st.get_option
    monkeypatch.setattr(st,'get_option',lambda key:200 if key=='server.maxUploadSize' else original(key))
    a=AppTest.from_file(str(ROOT/'phase9_app.py')).run()
    assert not a.exception and any('--server.maxUploadSize 5' in e.value for e in a.error)
    assert not (tmp_path/'private').exists()
