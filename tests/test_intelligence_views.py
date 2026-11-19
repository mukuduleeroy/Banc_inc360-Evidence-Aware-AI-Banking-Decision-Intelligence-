"""Phase 8B read-only interactions against the local validated source."""
from pathlib import Path
import hashlib
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from data_access import load_index
from analytics import portfolio_frame
from segment_context import banking_segment_frame, filter_banking_segment
from experimental_evidence import HistoricalComparison
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def app(tmp_path,monkeypatch):
    monkeypatch.setenv('DATA_MODE','LOCAL')
    monkeypatch.setenv('BANCINC_RUNTIME','LOCAL')
    monkeypatch.setenv('BANCINC_AUDIT_DB',str(tmp_path/'isolated.sqlite3'))
    value=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    assert not value.exception
    return value

def table(app):
    return next(t.value for t in app.dataframe if 'customer' in t.value.columns)

def index():return load_index(ROOT/'outputs/customer_features.csv')

@pytest.mark.parametrize('page,prefix,sort',[
    ('inactivity_intelligence','inactivity','recency_days'),
    ('relationship_value','relationship','relationship_activity_percentile'),
])
def test_all_default_then_segment_pagination_and_customer_continuity(app,page,prefix,sort):
    ix=index();source=portfolio_frame(ix)
    app.switch_page('views/'+page+'.py').run()
    expected=source.sort_values([sort,'customer'],ascending=[False,True],kind='stable')
    pd.testing.assert_frame_equal(table(app),expected.iloc[:25][table(app).columns])
    alias=app.session_state['selected_alias']
    app.number_input(key=prefix+'_page').set_value(2).run()
    assert app.number_input(key=prefix+'_page').value==2
    app.selectbox(key=prefix+'_banking_segment').select('SME').run()
    assert not app.exception and app.number_input(key=prefix+'_page').value==1
    expected=filter_banking_segment(expected,banking_segment_frame(ix),'SME')
    pd.testing.assert_frame_equal(table(app),expected.iloc[:25][table(app).columns])
    assert app.session_state['selected_alias']==alias
    app.selectbox(key=prefix+'_banking_segment').select('Unknown').run()
    assert table(app).empty
    assert any('No cases match' in t.value for t in app.info)
    assert app.session_state['selected_alias']==alias


def test_relationship_activity_and_global_outcome_intersect_without_reranking(app):
    ix=index();frame=portfolio_frame(ix)
    app.switch_page('views/relationship_value.py').run()
    assert app.selectbox(key='activity_segment').label=='Observed activity band'
    app.selectbox(key='relationship_banking_segment').select('Corporate').run()
    app.selectbox(key='activity_segment').select('Higher activity (80th+)').run()
    # Sidebar outcome filter retains its existing key and semantics.
    app.selectbox(key='analytics_lane').select('ABSTAIN').run()
    expected=filter_banking_segment(frame,banking_segment_frame(ix),'Corporate')
    expected=expected[(expected.activity_band=='Higher activity (80th+)')&(expected.rating=='ABSTAIN')]
    expected=expected.sort_values(['relationship_activity_percentile','customer'],ascending=[False,True],kind='stable')
    assert not app.exception
    pd.testing.assert_frame_equal(table(app),expected.iloc[:25][table(app).columns])


def test_product_global_kpis_context_and_selection_are_read_only(app):
    ix=index();canonical=ROOT/'outputs/customer_features.csv';before=hashlib.sha256(canonical.read_bytes()).hexdigest()
    original=ix.table().copy(deep=True)
    app.switch_page('views/product_opportunities.py').run()
    metrics={m.label:m.value for m in app.metric}
    alias=app.session_state['selected_alias']
    assert any('prototype Savings discussion' in w.value for w in app.warning)
    gates=next(t.value for t in app.dataframe if 'gate' in t.value.columns)
    assert list(gates.gate)==[g['gate'] for g in ix.passport(alias)['gates'] if g['gate'].startswith(('G4','G5'))]
    app.selectbox(key='opportunities_banking_segment').select('Trust').run()
    assert {m.label:m.value for m in app.metric}==metrics
    assert app.session_state['selected_alias']==alias
    app.selectbox(key='opportunity_context').select('Already-held suppression').run()
    expected=filter_banking_segment(portfolio_frame(ix),banking_segment_frame(ix),'Trust')
    expected=expected[expected.savings_gap=='Already held']
    pd.testing.assert_frame_equal(table(app),expected.iloc[:25][table(app).columns])
    assert 'SUPPORTED' not in set(table(app).rating)
    app.selectbox(key='opportunities_banking_segment').select('Unknown').run()
    assert table(app).empty and app.session_state['selected_alias']==alias
    assert not any(b.key in ('save_durable_review','record_decision') for b in app.button)
    pd.testing.assert_frame_equal(ix.table(),original)
    assert hashlib.sha256(canonical.read_bytes()).hexdigest()==before


def test_customer_segment_card_and_verified_history_are_safe(app):
    app.switch_page('views/customer_360.py').run()
    assert any('Banking segment — source-provided snapshot' in m.value for m in app.markdown)
    assert any('Effective date: unknown' in c.value for c in app.caption)
    app.switch_page('views/inactivity_intelligence.py').run()
    result=next(t.value for t in app.dataframe if 'ROC-AUC' in t.value.columns)
    assert len(result)==3 and list(result.columns)==['Model','ROC-AUC','Average Precision','Precision@500','Lift@500']
    assert not any('probability' in str(c).lower() for t in app.dataframe for c in t.value.columns)
    assert any('fitted preprocessing and model artifacts have not been saved' in m.value for m in app.markdown)
    assert not app.exception

@pytest.mark.parametrize('status',['Unavailable','Stale'])
def test_missing_stale_history_never_creates_metrics_or_demo(app,monkeypatch,status):
    import experimental_evidence
    monkeypatch.setattr(experimental_evidence,'load_historical_comparison',lambda *a,**kw:HistoricalComparison(status,'TEST_STATE','Trusted artifact requires verification.'))
    alias=app.session_state['selected_alias'];mode=app.session_state['data_mode'] if 'data_mode' in app.session_state else None
    app.switch_page('views/inactivity_intelligence.py').run()
    assert not app.exception
    assert any(status+' — ' in w.value for w in app.warning)
    assert not any('ROC-AUC' in t.value.columns for t in app.dataframe)
    assert app.session_state['selected_alias']==alias
    assert (app.session_state['data_mode'] if 'data_mode' in app.session_state else None)==mode


def test_inactivity_segment_coverage_recency_and_outcome_intersection(app):
    ix=index();frame=portfolio_frame(ix)
    app.switch_page('views/inactivity_intelligence.py').run()
    app.selectbox(key='inactivity_banking_segment').select('Retail').run()
    app.selectbox(key='recency_filter').select('>90 days').run()
    app.selectbox(key='coverage_filter').select('4+ events').run()
    app.selectbox(key='analytics_lane').select('ABSTAIN').run()
    expected=filter_banking_segment(frame,banking_segment_frame(ix),'Retail')
    expected=expected[(expected.recency_band=='>90 days')&(expected.frequency_band=='4+ events')&(expected.rating=='ABSTAIN')]
    expected=expected.sort_values(['recency_days','customer'],ascending=[False,True],kind='stable')
    pd.testing.assert_frame_equal(table(app),expected.iloc[:25][table(app).columns])
    assert not app.exception
