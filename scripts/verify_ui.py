"""Content-based verification of native pages, real evidence, queue and controlled demos."""
from pathlib import Path
import os,sys,tempfile,json,hashlib
from streamlit.testing.v1 import AppTest
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from data_access import load_index
from engine import DEMO_CASES
from ui_shell import PAGES

path=Path(os.environ.get('BANCINC_FEATURES_PATH',str(root/'outputs/customer_features.csv')))
before=hashlib.sha256(path.read_bytes()).hexdigest();index=load_index(path);assert not index.lineage_issues
app=AppTest.from_file(str(root/'app.py'),default_timeout=120).run();assert not app.exception
results={}
for slug,title,_ in PAGES:
    app.switch_page('views/'+slug+'.py').run()
    assert not app.exception and app.title[0].value==title
results['all_nine_native_pages_load']=True
app.switch_page('views/executive_overview.py').run()
values={m.label:m.value for m in app.metric}
assert int(values['Total evaluated customers'])==len(index.records)
for label,count in index.counts.items():assert int(values[label])==count
results['real_population_kpis_reconcile']=True
app.switch_page('views/manager_work_queue.py').run()
assert app.dataframe[0].value[index.page().columns].equals(index.page()) and not app.dataframe[0].value.empty
app.number_input(key='queue_page').set_value(2).run()
assert app.dataframe[0].value[index.page(2).columns].equals(index.page(2))
alias=app.selectbox(key='passport_customer').value
app.button(key='queue_open_passport').click().run()
assert app.session_state['selected_alias']==alias and app.title[0].value=='Decision Passport'
# AppTest does not retain the new URL hash after a button-triggered st.switch_page.
app.switch_page('views/decision_passport.py').run()
assert {m.label:m.value for m in app.metric}['Decision rating']==index.passport(alias)['rating']
app.button(key='record_decision').click().run();assert any('Reason required' in e.value for e in app.error)
app.text_input(key='staff_reason').set_value('Controlled UI verification; no banking action').run()
app.button(key='record_decision').click().run()
assert app.session_state['audit'][-1]['customer']==alias
notes=list(app.session_state['audit'])
results['queue_pagination_passport_and_session_notes']=True
app.switch_page('views/evidence_replay.py').run()
original={m.label:m.value for m in app.metric}
app.selectbox(key='replay_kyc').select('Pending').run()
assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='ABSTAIN'
assert not any(b.key=='record_decision' for b in app.button)
app.button(key='reset_replay').click().run()
assert {m.label:m.value for m in app.metric}['SIMULATED decision']==original['Baseline decision']
assert app.session_state['audit']==notes and before==hashlib.sha256(path.read_bytes()).hexdigest()
results['replay_reset_no_actions_and_canonical_preservation']=True
app.radio(key='data_source').set_value('Synthetic gate demonstrations').run()
assert not app.exception and not any(m.label=='Total evaluated customers' for m in app.metric)
for i in (1,3,5):
    app.selectbox(key='synthetic_case').select(DEMO_CASES[i]).run()
    assert not app.exception and {m.label:m.value for m in app.metric}['Decision rating']=='ABSTAIN'
results['synthetic_scenarios_separately_labeled']=True
previous=os.environ.get('BANCINC_FEATURES_PATH')
try:
    os.environ['BANCINC_FEATURES_PATH']=str(Path(tempfile.gettempdir())/'bancinc-intentionally-missing.csv')
    missing=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    assert not missing.exception and len(missing.warning)==1
finally:
    if previous is None:os.environ.pop('BANCINC_FEATURES_PATH',None)
    else:os.environ['BANCINC_FEATURES_PATH']=previous
results['missing_file_fallback_explicit']=True
(root/'outputs/ui_verification.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
