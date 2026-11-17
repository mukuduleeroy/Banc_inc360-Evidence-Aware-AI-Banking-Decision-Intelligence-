"""Local audit administration: inspect metadata or back up, never delete history."""
from pathlib import Path
import argparse,json,os,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from audit_store import AuditStore,AuditError

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['status','backup']);p.add_argument('--db',default=os.environ.get('BANCINC_AUDIT_DB',str(ROOT/'outputs/review_audit.sqlite3')));p.add_argument('--out');a=p.parse_args()
    try:
        store=AuditStore(a.db)
        if a.command=='backup':
            if not a.out:p.error('--out is required for backup')
            store.backup(a.out);print(json.dumps({'backup_created':True,'schema_version':store.summary()['schema_version']}))
        else:print(json.dumps(store.summary(),indent=2))
    except (AuditError,OSError) as exc:
        print(json.dumps({'error':getattr(exc,'code','STORAGE_UNAVAILABLE'),'message':str(exc)}));sys.exit(1)
