"""Presentation-only contract: accurate product copy, stable routes and context disclosures."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from ui_shell import PAGES
ROOT=Path(__file__).resolve().parents[1]

def visible(app):
    return ' '.join(str(e.value) for group in (app.markdown,app.caption,app.info,app.warning) for e in group)

@pytest.mark.parametrize('entry,title',[('app.py','Executive Overview'),('phase9_app.py','Data Management'),('phase10b_app.py','Business Opportunities')])
def test_consistent_identity_and_disclosures(entry,title,tmp_path,monkeypatch):
    import streamlit as st
    monkeypatch.setenv('DATA_MODE','LOCAL');monkeypatch.setenv('BANCINC_RUNTIME','LOCAL')
    monkeypatch.setenv('BANCINC_AUDIT_DB',str(tmp_path/'reviews.sqlite3'))
    monkeypatch.setenv('BANCINC_PHASE9_STORAGE',str(tmp_path/'ingestion'))
    get=st.get_option;monkeypatch.setattr(st,'get_option',lambda k:5 if k=='server.maxUploadSize' else get(k))
    app=AppTest.from_file(str(ROOT/entry),default_timeout=120).run();assert not app.exception
    assert app.title[0].value==title
    assert any(e.label=='About / System Information' for e in app.expander)
    text=visible(app)
    assert 'not a production banking service' in text and 'not bank approval' in text
    assert 'No customer outreach or financial action is connected' in text
    assert not any('CONTROLLED LOCAL DEMONSTRATION' in w.value for w in app.warning)
    assert not any('PHASE 10B' in str(e) for e in app.get('html'))
    assert not app.error


def test_original_routes_and_professional_groups_unchanged():
    assert [p[0] for p in PAGES]==['executive_overview','customer_360','inactivity_intelligence','relationship_value','product_opportunities','decision_passport','evidence_replay','manager_work_queue','audit_validation']
    assert list(dict.fromkeys(p[2] for p in PAGES))==['OVERVIEW','CUSTOMER INTELLIGENCE','DECISION MANAGEMENT','GOVERNANCE']


def test_companion_links_use_business_labels(tmp_path,monkeypatch):
    monkeypatch.setenv('DATA_MODE','DEMO')
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();assert not app.exception
    links=list(app.get('page_link'))
    assert [(l.proto.label,l.proto.page) for l in links]==[('Data Management','http://127.0.0.1:8511'),('Business Opportunities','http://127.0.0.1:8515')]
