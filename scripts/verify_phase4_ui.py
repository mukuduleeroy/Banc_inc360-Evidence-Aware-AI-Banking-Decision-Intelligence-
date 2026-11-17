"""Read-only assurance of the live nine-view shape and isolated durable UI flow.
Uses a temporary database, leaving real demonstration history unchanged.
"""
from pathlib import Path
import sys,tempfile,os,json
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ui_shell import PAGES
from audit_store import AuditStore

previous=os.environ.get('BANCINC_AUDIT_DB')
try:
    with tempfile.TemporaryDirectory(prefix='bancinc-phase4-ui-') as folder:
        db=Path(folder)/'audit.sqlite3';os.environ['BANCINC_AUDIT_DB']=str(db)
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
        for slug,title,_ in PAGES:
            app.switch_page('views/'+slug+'.py').run();assert not app.exception and app.title[0].value==title
        app.switch_page('views/manager_work_queue.py').run()
        assert not app.exception and not app.dataframe[0].value.empty and set(app.dataframe[0].value.rating)=={'SUPPORTED'}
        assert app.selectbox(key='durable_reviewer').value is None
        app.selectbox(key='durable_reviewer').select('DEMO-RM-01').run()
        app.button(key='open_review_case').click().run();assert not app.exception
        app.text_area(key='durable_reason').set_value('Controlled assurance of local prototype review; no banking action.')
        app.checkbox(key='durable_ack').set_value(True)
        app.button(key='save_durable_review').click().run();assert not app.exception
        assert AuditStore(db).cases()[0]['state']=='APPROVED_LOCAL'
        fresh=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
        fresh.switch_page('views/audit_validation.py').run();assert not fresh.exception
        history=next(t.value for t in fresh.dataframe if 'event_sequence' in t.value.columns)
        assert list(history.action)==['OPEN','APPROVE']
        result={'native_views_verified':9,'explicit_reviewer_required':True,'supported_local_review_committed':True,'fresh_session_reads_persisted_history':True,'outreach_or_bank_authorization':False}
        (ROOT/'outputs/phase4/ui_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:
    if previous is None:os.environ.pop('BANCINC_AUDIT_DB',None)
    else:os.environ['BANCINC_AUDIT_DB']=previous
