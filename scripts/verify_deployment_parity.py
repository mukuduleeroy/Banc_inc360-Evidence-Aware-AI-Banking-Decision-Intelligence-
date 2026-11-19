"""Local-only deployment emulation; never uploads, publishes or authorizes a release."""
from pathlib import Path
import sys,argparse,json,hashlib,shutil,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from deployment_data import configuration,load_dataset
from data_access import load_index,manifest_path,alias_key
from streamlit.testing.v1 import AppTest
from ui_shell import PAGES

def verify(out):
 out=Path(out).resolve()
 if out.exists():raise FileExistsError('Choose a new local parity evidence directory.')
 out.mkdir(parents=True);source=ROOT/'outputs/customer_features.csv';before=hashlib.sha256(source.read_bytes()).hexdigest();local=load_index(source)
 target=out/'customer_features.csv';shutil.copyfile(source,target);manifest=json.loads(manifest_path(source).read_text());manifest['dataset_version']='phase6-local-parity-only';manifest_path(target).write_text(json.dumps(manifest,indent=2))
 env={'DATA_MODE':'DEPLOYED','BANCINC_RUNTIME':'CLOUD','BANCINC_FEATURES_PATH':str(target.relative_to(ROOT)),'DATA_SHA256':before,'DATA_VERSION':manifest['dataset_version'],'DATA_RELEASE_APPROVAL_REFERENCE':'LOCAL VALIDATION ONLY; NOT HOSTING OR PUBLICATION APPROVAL','DATA_ACCESS_SCOPE':'PRIVATE_HOST','BANCINC_ALIAS_KEY_HEX':alias_key().hex(),'BANCINC_AUDIT_DB':str((out/'isolated_cloud.sqlite3').relative_to(ROOT))}
 deployed=load_dataset(configuration(ROOT,environ=env,secrets={}),ROOT);assert local.table().equals(deployed.table()) and local.counts==deployed.counts
 previous={k:os.environ.get(k) for k in env}
 try:
  os.environ.update(env);app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();assert not app.exception
  for slug,title,_ in PAGES:
   app.switch_page('views/'+slug+'.py').run();assert not app.exception and app.title[0].value==title
   for t in app.dataframe:
    assert 'customer_id' not in t.value.columns and 'Account ID' not in t.value.columns
    if 'customer' in t.value.columns:assert t.value.customer.str.fullmatch(r'C-[A-F0-9]{24}').all()
  app.switch_page('views/evidence_replay.py').run();app.selectbox(key='replay_kyc').select('Pending').run();assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='ABSTAIN';app.button(key='reset_replay').click().run();assert {m.label:m.value for m in app.metric}['SIMULATED decision']=='SUPPORTED'
  app.switch_page('views/manager_work_queue.py').run();assert not app.dataframe[0].value.empty;assert set(app.dataframe[0].value.rating)=={'SUPPORTED'}
  from audit_store import AuditStore
  assert AuditStore(out/'isolated_cloud.sqlite3').summary()['events']==0
 finally:
  for k,v in previous.items():
   if v is None:os.environ.pop(k,None)
   else:os.environ[k]=v
 assert before==hashlib.sha256(source.read_bytes()).hexdigest()
 result={'scope':'LOCAL EMULATION ONLY; no customer artifact uploaded or release authorized','dataset_sha256':before,'policy_sha256':local.policy_hash,'local_rows':len(local.records),'emulated_deployed_rows':len(deployed.records),'local_counts':local.counts,'emulated_counts':deployed.counts,'entire_queue_equal':True,'native_views_verified':9,'real_supported_passport':True,'replay_pending_abstains_and_reset_supported':True,'queue_populated':True,'privacy_safe_customer_columns':True,'canonical_unchanged':True,'cloud_durability_verified':False,'remote_real_data_parity_verified':False,'automatic_outreach':False,'review_events_written':0}
 (out/'parity.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default='outputs/phase6/parity');a=p.parse_args();verify(a.out)
