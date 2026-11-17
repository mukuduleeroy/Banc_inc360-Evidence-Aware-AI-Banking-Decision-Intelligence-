"""Initialize, start, inspect, back up or safely reset a managed local demonstration."""
from pathlib import Path
import argparse,sys,json,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from presentation import initialize,read_config,environment
from audit_store import AuditStore
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['init','reset','start','backup','status']);p.add_argument('--root',default=str(ROOT/'outputs/phase5/demo'));p.add_argument('--features',default=str(ROOT/'outputs/customer_features.csv'));p.add_argument('--port',type=int,default=8505);p.add_argument('--out');a=p.parse_args()
 if a.command in ('init','reset'):print(json.dumps(initialize(a.root,a.features,a.command=='reset'),indent=2))
 elif a.command=='start':
  env=environment(a.root);raise SystemExit(subprocess.call([sys.executable,'-m','streamlit','run',str(ROOT/'app.py'),'--server.address','127.0.0.1','--server.port',str(a.port),'--server.headless','true','--browser.gatherUsageStats','false'],cwd=ROOT,env=env))
 else:
  data,db=read_config(a.root)
  if a.command=='backup':
   if not a.out:p.error('A new --out path is required')
   AuditStore(db).backup(a.out);print('Consistent SQLite backup created; existing files were not overwritten.')
  else: print(json.dumps({'configuration':data,'audit':AuditStore(db).summary()},indent=2))
