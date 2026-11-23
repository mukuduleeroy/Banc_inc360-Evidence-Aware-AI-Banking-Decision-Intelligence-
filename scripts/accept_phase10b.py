"""Local actual business demo in separate servers; no accepted storage or policy changes."""
from pathlib import Path
import sys,subprocess,os,tempfile,json,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.accept_phase5 import wait_url,stop
from phase10b_value import load_accepted_index
from acceptance_checks import decision_fingerprint
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--main-port',type=int,default=8514);p.add_argument('--port',type=int,default=8515);p.add_argument('--cdp-port',type=int,default=9232);a=p.parse_args();out=Path(a.out).resolve()
 if out.exists():raise FileExistsError('Use a fresh browser evidence directory.')
 out.mkdir(parents=True);before=decision_fingerprint(load_accepted_index());env=os.environ.copy();env.update(DATA_MODE='LOCAL',BANCINC_RUNTIME='LOCAL',BANCINC_AUDIT_DB=str(out/'isolated-original-review.sqlite3'),BANCINC_MAIN_URL=f'http://127.0.0.1:{a.main_port}',BANCINC_PREVIEW_URL=f'http://127.0.0.1:{a.port}',BANCINC_CDP_URL=f'http://127.0.0.1:{a.cdp_port}',BANCINC_BROWSER_OUT=str(out));servers=[];chrome=None
 try:
  with tempfile.TemporaryDirectory(prefix='bancinc-10b-chrome-') as profile,(out/'servers.log').open('w') as log,(out/'chrome.log').open('w') as clog:
   for file,port in [('app.py',a.main_port),('phase10b_app.py',a.port)]:
    server=subprocess.Popen([sys.executable,'-m','streamlit','run',file,'--server.address','127.0.0.1','--server.port',str(port),'--server.headless','true','--browser.gatherUsageStats','false'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT);servers.append(server);wait_url(f'http://127.0.0.1:{port}/_stcore/health',server)
   chrome=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--remote-debugging-address=127.0.0.1','--remote-debugging-port='+str(a.cdp_port),'--user-data-dir='+profile,'--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','about:blank'],stdout=clog,stderr=subprocess.STDOUT);wait_url(env['BANCINC_CDP_URL']+'/json/list',chrome)
   with (out/'browser.log').open('w') as b:subprocess.run(['node','scripts/verify_phase10b_browser.mjs'],cwd=ROOT,env=env,check=True,stdout=b,stderr=subprocess.STDOUT,timeout=480)
   assert decision_fingerprint(load_accepted_index())==before
   result={'status':'PASS','sequence':'existing Savings cross-sell → synthetic upgrade and withholding → source-derived activity proxy/segment → original baseline','source_decision_digest_unchanged':True,'responsive_checks':12,'bank_product_upgrade_authorization':False,'network_scope':'loopback only','original_storage_isolated':True}
   (out/'acceptance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 finally:
  for server in servers:stop(server)
  stop(chrome)
