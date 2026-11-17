"""Managed, disposable presentation generations; reset retains every prior database."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,uuid
from audit_store import AuditStore
from data_access import load_index,alias_key,policy_fingerprint
from historical_evaluation import digest

ROOT=Path(__file__).resolve().parent
MARKER='bancinc-managed-demo-v1'

def read_config(root):
 root=Path(root).resolve();p=root/'demo.json'
 data=json.loads(p.read_text())
 if data.get('marker')!=MARKER:raise ValueError('Not a managed BancInc demonstration')
 db=root/data['database']
 if db.parent!=root or not db.name.startswith('demo-') or db.suffix!='.sqlite3':raise ValueError('Unsafe demonstration database path')
 return data,db

def initialize(root,features=ROOT/'outputs/customer_features.csv',reset=False):
 root=Path(root).resolve();features=Path(features).resolve();previous=None
 if (root/'demo.json').exists():
  if not reset:raise FileExistsError('Demo exists. Use status/start or explicit reset; prior history is retained.')
  previous,db=read_config(root)
 elif root.exists() and any(root.iterdir()):raise ValueError('Refusing an unmanaged nonempty directory')
 root.mkdir(parents=True,exist_ok=True)
 index=load_index(features)
 if index.lineage_issues:raise ValueError('Verified source provenance required')
 selected={rating:next((r.alias for r in index.records if r.rating==rating),None) for rating in ['SUPPORTED','CAUTION','ABSTAIN']}
 if not selected['SUPPORTED'] or not (selected['CAUTION'] or selected['ABSTAIN']):raise ValueError('Real supported and investigation examples required')
 generation=uuid.uuid4().hex;name='demo-'+generation+'.sqlite3'
 backup=None
 if previous:
  backup='archive-'+generation+'.sqlite3';AuditStore(db).backup(root/backup)
 store=AuditStore(root/name)
 from hashlib import sha256
 data={'marker':MARKER,'created_utc':datetime.now(timezone.utc).isoformat(),'generation':generation,'database':name,'features':str(features),'feature_sha256':index.dataset_hash,'policy_sha256':index.policy_hash,'alias_key_sha256':sha256(alias_key()).hexdigest(),'cutoff':index.cutoff,'aliases':selected,'counts':index.counts,'previous_database':previous['database'] if previous else None,'previous_backup':backup,'reviewer_attribution':'DEMO_UNVERIFIED','bank_authorization':False,'automatic_outreach':False,'reset_semantics':'new empty database generation; previous history and backup retained'}
 temp=root/('config-'+generation+'.tmp');temp.write_text(json.dumps(data,indent=2));os.chmod(temp,0o600);os.replace(temp,root/'demo.json')
 return data

def environment(root):
 data,db=read_config(root)
 from hashlib import sha256
 if digest(data['features'])!=data['feature_sha256'] or policy_fingerprint()!=data['policy_sha256'] or sha256(alias_key()).hexdigest()!=data['alias_key_sha256']:raise ValueError('Presentation evidence/key/policy changed; inspect and reset to a new generation')
 index=load_index(Path(data['features']))
 if index.lineage_issues:raise ValueError('Presentation source provenance no longer valid')
 env=os.environ.copy();env.update(BANCINC_AUDIT_DB=str(db),BANCINC_FEATURES_PATH=data['features']);return env
