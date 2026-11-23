"""Native four-view companion regression, no storage/review/activation writes."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from phase10b_upsell import ELIGIBLE,MISSING,INELIGIBLE
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv('BANCINC_RUNTIME','LOCAL');a=AppTest.from_file(str(ROOT/'phase10b_app.py'),default_timeout=120).run();assert not a.exception;return a

def page(app,name):app.radio(key='p10b_view').set_value(name).run();assert not app.exception

def text(app):return ' '.join(m.value for m in app.markdown)+' '.join(c.value for c in app.caption)+' '.join(i.value for i in app.info)+' '.join(w.value for w in app.warning)

@pytest.mark.parametrize('name',['Business Opportunity Overview','Upselling Intelligence','High-Value Customer Intelligence','Evidence and Methodology'])
def test_all_companion_views_and_no_write_actions(app,name):
    if name!='Business Opportunity Overview':page(app,name)
    assert app.header[0].value==name
    assert not app.button and not app.text_input and not app.text_area
    assert not any('profit' in m.label.lower() or 'revenue' in m.label.lower() for m in app.metric)


def test_synthetic_positive_and_all_withholding_explanations(app):
    page(app,'Upselling Intelligence');assert ELIGIBLE in text(app)
    assert 'hypothetical' in text(app).lower() and 'synthetic' in text(app).lower()
    checks=app.dataframe[0].value;assert set(checks.status)=={'PASS'}
    for scenario,status in [('Restricted synthetic customer',INELIGIBLE),('Missing activity evidence',MISSING),('Already holds hypothetical target',INELIGIBLE),('Unverified source ownership',MISSING),('Invalid same-tier product relationship',INELIGIBLE),('Insufficient historical activity',MISSING)]:
        app.selectbox(key='p10b_scenario').select(scenario).run();assert not app.exception
        assert status in text(app) and any(s!='PASS' for s in app.dataframe[0].value.status)
    assert 'G5 has not evaluated' in text(app)


def test_proxy_filters_pagination_empty_and_global_scope(app):
    page(app,'High-Value Customer Intelligence')
    first=app.dataframe[0].value.copy(deep=True);alias=app.selectbox(key='p10b_value_alias').value
    assert len(first)==25 and (first.relationship_activity_percentile>=.8).all()
    assert set(first.activity_band)=={'Higher activity (80th+)'}
    metrics={m.label:m.value for m in app.metric}
    assert metrics['Original global ranking population']=='50000' and metrics['High Relationship Activity']=='10003'
    app.number_input(key='p10b_page').set_value(2).run();assert app.number_input(key='p10b_page').value==2
    app.selectbox(key='p10b_segment').select('SME').run();assert not app.exception
    assert app.number_input(key='p10b_page').value==1 and set(app.dataframe[0].value.banking_segment)=={'SME'}
    assert {m.label:m.value for m in app.metric}==metrics
    app.selectbox(key='p10b_segment').select('Unknown').run();assert app.dataframe[0].value.empty and any('No customers match these filters' in i.value for i in app.info)
    app.selectbox(key='p10b_segment').select('All').run();assert app.selectbox(key='p10b_value_alias').value==alias
    assert app.dataframe[0].value.equals(first)


def test_original_counts_and_synthetic_denominators_are_separate(app):
    values={m.label:m.value for m in app.metric}
    assert values['Accepted customers']=='50000' and values['SUPPORTED']=='2052' and values['CAUTION']=='20' and values['ABSTAIN']=='47928'
    assert values['Independent synthetic upsell scenarios']=='7'
    assert 'not included' in text(app)


def test_source_integrity_failure_has_no_positive_proxy_or_demo_fallback(app,monkeypatch):
    import phase10b_value
    monkeypatch.setattr(phase10b_value,'load_accepted_index',lambda:(_ for _ in ()).throw(ValueError('controlled integrity failure')))
    page(app,'High-Value Customer Intelligence')
    assert any('could not be verified' in e.value for e in app.error) and not app.dataframe


def test_cloud_runtime_refused(monkeypatch):
    monkeypatch.setenv('BANCINC_RUNTIME','CLOUD');a=AppTest.from_file(str(ROOT/'phase10b_app.py')).run()
    assert not a.exception and any('local demonstration only' in e.value for e in a.error)
