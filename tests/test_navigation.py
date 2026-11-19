"""Actual Streamlit native navigation and real competition-data acceptance."""
from pathlib import Path
import hashlib
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from data_access import load_index
from analytics import portfolio_frame,metrics
from ui_shell import PAGES
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def app():
    value=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    assert not value.exception
    return value

@pytest.mark.parametrize('slug,title,group',PAGES)
def test_all_nine_native_pages_load(app,slug,title,group):
    app.switch_page('views/'+slug+'.py').run()
    assert not app.exception
    assert app.title[0].value==title

def test_kpis_are_actual_and_no_performance_is_invented(app):
    index=load_index(ROOT/'outputs/customer_features.csv')
    values={m.label:m.value for m in app.metric}
    assert int(values['Total evaluated customers'])==len(index.records)
    for rating,count in index.counts.items():assert int(values[rating])==count
    assert int(values['Actionable manager-review cases'])==index.counts['SUPPORTED']
    visible=' '.join(e.value for e in app.markdown)+ ' '.join(c.value for c in app.caption)
    assert '0.9406' not in visible and '0.5394' not in visible and 'trained model accuracy' not in visible

def test_alias_search_and_selection_survive_navigation(app):
    index=load_index(ROOT/'outputs/customer_features.csv');alias=index.records[-1].alias
    app.text_input(key='global_alias_search').set_value(alias).run()
    app.selectbox(key='global_customer').select(alias).run()
    assert app.session_state['selected_alias']==alias
    for path in ('views/customer_360.py','views/decision_passport.py','views/evidence_replay.py'):
        app.switch_page(path).run();assert not app.exception
        assert app.session_state['selected_alias']==alias
    app.text_input(key='global_alias_search').set_value('NO-MATCH').run()
    assert app.session_state['selected_alias']==alias
    assert any('No customer alias matches' in i.value for i in app.info)

def test_queue_preserves_complete_pagination_and_passport_navigation(app):
    index=load_index(ROOT/'outputs/customer_features.csv')
    app.switch_page('views/manager_work_queue.py').run()
    first=app.dataframe[0].value
    assert first[index.page().columns].equals(index.page()) and not first.empty
    assert {'case_status','last_demo_reviewer','latest_review_action','review_timestamp_utc'}<=set(first.columns)
    app.number_input(key='queue_page').set_value(2).run()
    assert app.dataframe[0].value[index.page(2).columns].equals(index.page(2))
    alias=app.selectbox(key='passport_customer').value
    app.button(key='queue_open_passport').click().run()
    assert not app.exception and app.title[0].value=='Decision Passport'
    assert app.session_state['selected_alias']==alias
    p=index.passport(alias)
    assert {m.label:m.value for m in app.metric}['Decision rating']==p['rating']
    pd.testing.assert_frame_equal(app.dataframe[0].value,pd.DataFrame(p['gates']))

def test_opportunity_view_contains_only_supported_actionable_rows(app):
    app.switch_page('views/product_opportunities.py').run()
    table=next(t.value for t in app.dataframe if 'customer' in t.value.columns)
    assert not table.empty and set(table.rating)=={'SUPPORTED'}
    assert set(table.savings_gap)=={'Gap recorded'}
    app.selectbox(key='opportunity_context').select('Already-held suppression').run()
    table=next(t.value for t in app.dataframe if 'customer' in t.value.columns)
    assert set(table.savings_gap)=={'Already held'} and 'SUPPORTED' not in set(table.rating)

def test_replay_reset_and_no_customer_action_path(app):
    path=ROOT/'outputs/customer_features.csv';before=hashlib.sha256(path.read_bytes()).hexdigest()
    app.switch_page('views/evidence_replay.py').run()
    baseline={m.label:m.value for m in app.metric}
    assert baseline['Baseline decision']==baseline['SIMULATED decision']=='SUPPORTED'
    notes=list(app.session_state['audit'])
    app.selectbox(key='replay_kyc').select('Pending').run()
    assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='ABSTAIN'
    changed=app.dataframe[0].value
    assert any(g.startswith('G4') for g in changed.Gate)
    assert not any(b.key=='record_decision' for b in app.button)
    app.button(key='reset_replay').click().run()
    assert not app.exception
    assert {m.label:m.value for m in app.metric}['SIMULATED decision']==baseline['Baseline decision']
    assert app.selectbox(key='replay_kyc').value=='Verified'
    assert app.session_state['audit']==notes
    assert before==hashlib.sha256(path.read_bytes()).hexdigest()

def test_visible_tables_expose_only_alias_identity(app):
    for page in ('views/customer_360.py','views/relationship_value.py','views/product_opportunities.py','views/decision_passport.py','views/manager_work_queue.py'):
        app.switch_page(page).run();assert not app.exception
        for table in app.dataframe:
            frame=table.value
            assert 'customer_id' not in frame.columns and 'Account ID' not in frame.columns
            if 'customer' in frame.columns:assert frame.customer.str.fullmatch(r'C-[A-F0-9]{24}').all()

def test_missing_fields_and_source_fallback_are_explicit(tmp_path,monkeypatch):
    missing=tmp_path/'missing.csv';monkeypatch.setenv('BANCINC_FEATURES_PATH',str(missing))
    demo=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    assert not demo.exception
    assert any('DATASET_UNAVAILABLE' in e.value for e in demo.error)
    assert not any('SYNTHETIC' in i.value for i in demo.info)
    assert not any(m.label=='Total evaluated customers' for m in demo.metric)
    missing.write_text('customer_id\nSYNTHETIC\n')
    invalid=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    assert not invalid.exception
    assert any('MISSING_REQUIRED_FIELDS' in error.value for error in invalid.error)

def test_session_notes_survive_navigation_and_reason_resets_for_new_customer(app):
    index=load_index(ROOT/'outputs/customer_features.csv')
    app.switch_page('views/decision_passport.py').run()
    original=app.session_state['selected_alias']
    app.button(key='record_decision').click().run()
    assert any('Reason required' in e.value for e in app.error)
    app.text_input(key='staff_reason').set_value('Controlled test review; no bank action').run()
    app.button(key='record_decision').click().run()
    assert len(app.session_state['audit'])==1
    app.switch_page('views/audit_validation.py').run()
    assert app.session_state['audit'][0]['customer']==original
    new=next(r.alias for r in index.records if r.alias!=original)
    app.text_input(key='global_alias_search').set_value(new).run()
    app.selectbox(key='global_customer').select(new).run()
    app.switch_page('views/decision_passport.py').run()
    assert app.text_input(key='staff_reason').value==''
    assert app.session_state['audit'][0]['customer']==original

def test_replay_overrides_reset_when_starting_customer_changes(app):
    index=load_index(ROOT/'outputs/customer_features.csv')
    app.switch_page('views/evidence_replay.py').run()
    app.selectbox(key='replay_kyc').select('Pending').run()
    new=index.records[0].alias
    app.text_input(key='global_alias_search').set_value(new).run()
    app.selectbox(key='global_customer').select(new).run()
    values={m.label:m.value for m in app.metric}
    assert values['Baseline decision']==values['SIMULATED decision']==index.passport(new)['rating']
    assert 'None — simulation matches baseline' in ' '.join(m.value for m in app.markdown)

def test_navigating_views_does_not_reevaluate_the_whole_portfolio(app,monkeypatch):
    import data_access
    original=data_access.evaluate
    calls=[]
    def counted(case):
        calls.append(1)
        return original(case)
    monkeypatch.setattr(data_access,'evaluate',counted)
    for slug,_,_ in PAGES:
        app.switch_page('views/'+slug+'.py').run()
        assert not app.exception
    # Selected passports may be evaluated; a second 50,000-customer sweep may not.
    assert len(calls)<100
