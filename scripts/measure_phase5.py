"""Local timings; warm AppTest reruns are not browser round trips or an SLA."""
from pathlib import Path
import sys,time,json,tempfile,os,statistics
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd
from data_access import load_index
from audit_store import AuditStore
from review_service import ReviewService
from streamlit.testing.v1 import AppTest

def timed(fn,n=1):
 values=[];result=None
 for _ in range(n):
  t=time.perf_counter();result=fn();values.append(time.perf_counter()-t)
 return result,{'samples_seconds':values,'median_seconds':statistics.median(values)}

if __name__=='__main__':
 source=ROOT/'outputs/customer_features.csv';frame,read=timed(lambda:pd.read_csv(source));index,cold=timed(lambda:load_index(source));_,warm=timed(lambda:load_index(source),5)
 with tempfile.TemporaryDirectory(prefix='bancinc-perf-') as d:
  os.environ['BANCINC_AUDIT_DB']=str(Path(d)/'perf.sqlite3');app,first=timed(lambda:AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run());assert not app.exception
  _,overview=timed(lambda:app.switch_page('views/executive_overview.py').run(),3);assert not app.exception
  _,queue=timed(lambda:index.page(2),10);_,filtering=timed(lambda:index.page(1,search='C-',rating='SUPPORTED'),10)
  app.switch_page('views/manager_work_queue.py').run()
  _,queue_ui=timed(lambda:app.number_input(key='queue_page').set_value(2).run(),3)
  _,filter_ui=timed(lambda:app.text_input(key='alias_filter').set_value('C-').run(),3)
  assert not app.exception
  _,customer_ui=timed(lambda:app.switch_page('views/customer_360.py').run(),3);assert not app.exception
  alias=next(r.alias for r in index.records if r.rating=='SUPPORTED');_,drill=timed(lambda:index.passport(alias),10)
  service=ReviewService(AuditStore(Path(d)/'review.sqlite3'),features_path=source);case,opening=timed(lambda:service.open_case(alias,'DEMO-RM-01','perf-open'));_,writing=timed(lambda:service.record_review(case['case_id'],'DEMO-RM-01','APPROVE','Measured local prototype review only.',case['revision'],case['current_snapshot_id'],'perf-review',True))
  result={'method':'single local fresh Python process; CSV read and index measured separately; AppTest after warm index; no SLA','csv_loading':read,'cold_decision_index':cold,'warm_index_load':warm,'first_AppTest_overview':first,'warm_overview_AppTest':overview,'queue_filtering':filtering,'queue_pagination':queue,'customer_passport_drilldown':drill,'queue_pagination_AppTest':queue_ui,'queue_filter_AppTest':filter_ui,'customer_360_AppTest':customer_ui,'case_open':opening,'review_revalidate_and_write':writing,'database_isolation':'temporary; never presentation.sqlite3','data_rows':len(frame)}
 Path('outputs/phase5/performance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
