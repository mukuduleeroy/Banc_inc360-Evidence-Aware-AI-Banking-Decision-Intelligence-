"""Actual server/browser acceptance in a separate managed DB, including process restart."""
from pathlib import Path
import sys,subprocess,json,time,urllib.request,tempfile,os,argparse,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from presentation import initialize,environment,read_config
from audit_store import AuditStore
from historical_evaluation import digest

def wait_url(url,process,timeout=90):
 t=time.perf_counter()
 while time.perf_counter()-t<timeout:
  if process.poll() is not None:raise RuntimeError('Process exited before readiness')
  try:
   with urllib.request.urlopen(url,timeout=1) as response:
    if response.status==200:return time.perf_counter()-t
  except Exception:time.sleep(.15)
 raise TimeoutError('Local readiness timed out')

def stop(process):
 if process and process.poll() is None:
  process.terminate()
  try:process.wait(timeout=10)
  except subprocess.TimeoutExpired:process.kill();process.wait()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default='outputs/phase5/acceptance');p.add_argument('--port',type=int,default=8506);p.add_argument('--cdp-port',type=int,default=9223);a=p.parse_args();out=Path(a.out).resolve()
 if out.exists():raise FileExistsError('Use an unused acceptance directory')
 out.mkdir(parents=True);config=initialize(out/'demo');env=environment(out/'demo');env.update(BANCINC_PREVIEW_URL=f'http://127.0.0.1:{a.port}',BANCINC_CDP_URL=f'http://127.0.0.1:{a.cdp_port}',BANCINC_BROWSER_OUT=str(out))
 protected={s:AuditStore(ROOT/s).summary() for s in ['outputs/phase4/presentation.sqlite3','outputs/phase4/process_rehearsal.sqlite3']};csv_before=digest(ROOT/'outputs/customer_features.csv');server=chrome=None
 def launch(log):
  return subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.address','127.0.0.1','--server.port',str(a.port),'--server.headless','true','--browser.gatherUsageStats','false'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 def browser(script,*args):
  with (out/(Path(script).stem+('-'+args[0] if args else '')+'.log')).open('w') as log:subprocess.run(['node',script,*args],env=env,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=300)
 try:
  with tempfile.TemporaryDirectory(prefix='bancinc-phase5-chrome-') as profile,(out/'server.log').open('w') as log,(out/'chrome.log').open('w') as clog:
   start=time.perf_counter();server=launch(log);wait_url(env['BANCINC_PREVIEW_URL']+'/_stcore/health',server);cold=time.perf_counter()-start
   chrome=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--remote-debugging-address=127.0.0.1','--remote-debugging-port='+str(a.cdp_port),'--user-data-dir='+profile,'--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','about:blank'],stdout=clog,stderr=subprocess.STDOUT)
   wait_url(env['BANCINC_CDP_URL']+'/json/list',chrome)
   browser('scripts/verify_browser.mjs');browser('scripts/verify_phase4_browser.mjs','create');stop(server)
   start=time.perf_counter();server=launch(log);wait_url(env['BANCINC_PREVIEW_URL']+'/_stcore/health',server);restart=time.perf_counter()-start;browser('scripts/verify_phase4_browser.mjs','reopen')
   _,db=read_config(out/'demo');summary=AuditStore(db).summary();assert summary['events']==2
   assert protected=={s:AuditStore(ROOT/s).summary() for s in protected};assert digest(ROOT/'outputs/customer_features.csv')==csv_before
   result={'passed':True,'native_views':9,'cold_server_health_seconds':cold,'restart_server_health_seconds':restart,'server_health_note':'process spawn to HTTP health, not first fully rendered browser page','audit_after_restart':summary,'canonical_unchanged':True,'prior_phase4_databases_unchanged':True,'acceptance_database_isolated':True,'bank_authorization':False,'automatic_outreach':False,'screenshot_directory':str(out/'screenshots'),'aliases':config['aliases']};(out/'acceptance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 finally:stop(server);stop(chrome)
