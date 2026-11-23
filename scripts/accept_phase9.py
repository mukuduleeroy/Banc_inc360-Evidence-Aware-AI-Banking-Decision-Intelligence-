"""Actual local synthetic CSV upload browser check with isolated Phase 9 storage."""
from pathlib import Path
import sys,subprocess,os,tempfile,json,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.accept_phase5 import wait_url,stop
from acceptance_checks import verify_local_baseline
from phase9_ingestion import SnapshotStore
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--port',type=int,default=8511);p.add_argument('--cdp-port',type=int,default=9230);a=p.parse_args();out=Path(a.out).resolve()
 if out.exists():raise FileExistsError('Choose a fresh browser evidence directory.')
 out.mkdir(parents=True);baseline=verify_local_baseline();env=os.environ.copy();env.update(DATA_MODE='LOCAL',BANCINC_RUNTIME='LOCAL',BANCINC_PHASE9_STORAGE=str(out/'private'),BANCINC_PREVIEW_URL=f'http://127.0.0.1:{a.port}',BANCINC_CDP_URL=f'http://127.0.0.1:{a.cdp_port}',BANCINC_BROWSER_OUT=str(out));server=chrome=None
 try:
  with tempfile.TemporaryDirectory(prefix='bancinc-phase9-browser-') as profile,(out/'server.log').open('w') as log,(out/'chrome.log').open('w') as clog:
   server=subprocess.Popen([sys.executable,'-m','streamlit','run','phase9_app.py','--server.address','127.0.0.1','--server.port',str(a.port),'--server.headless','true','--browser.gatherUsageStats','false','--server.maxUploadSize','5'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT);wait_url(env['BANCINC_PREVIEW_URL']+'/_stcore/health',server)
   chrome=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--remote-debugging-address=127.0.0.1','--remote-debugging-port='+str(a.cdp_port),'--user-data-dir='+profile,'--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','about:blank'],stdout=clog,stderr=subprocess.STDOUT);wait_url(env['BANCINC_CDP_URL']+'/json/list',chrome)
   with (out/'browser.log').open('w') as browserlog:subprocess.run(['node','scripts/verify_phase9_browser.mjs'],cwd=ROOT,env=env,check=True,stdout=browserlog,stderr=subprocess.STDOUT,timeout=300)
   state=SnapshotStore(out/'private').state();assert state['active']=='baseline' and len(state['snapshots'])==1
   assert [e['action'] for e in state['events']]==['CREATE','ACTIVATE','ROLLBACK_BASELINE']
   assert verify_local_baseline()==baseline
   result={'status':'PASS','synthetic_upload_only':True,'registry_events':[e['action'] for e in state['events']],'active_after_demo':state['active'],'accepted_baseline_unchanged':True,'network_scope':'local loopback browser/server only','source_policy_unchanged':True}
   (out/'acceptance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 finally:stop(server);stop(chrome)
