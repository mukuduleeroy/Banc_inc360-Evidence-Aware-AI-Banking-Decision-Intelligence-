"""Controlled deployment fixtures and local-only parity; no data publication."""
from pathlib import Path
from dataclasses import replace
import hashlib,json
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from deployment_data import configuration,load_dataset,portable_path,setting,audit_configuration,DeploymentError
from data_access import load_index,manifest_path,alias_key
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def release(tmp_path,feature_row,write_features):
 path=write_features(pd.DataFrame([feature_row]));m=json.loads(manifest_path(path).read_text());m['dataset_version']='synthetic-release-v1';manifest_path(path).write_text(json.dumps(m))
 env={'DATA_MODE':'DEPLOYED','BANCINC_RUNTIME':'CLOUD','BANCINC_FEATURES_PATH':path.name,'DATA_SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'DATA_VERSION':'synthetic-release-v1','DATA_RELEASE_APPROVAL_REFERENCE':'SYNTHETIC TEST AUTHORIZATION ONLY','DATA_ACCESS_SCOPE':'PRIVATE_HOST','BANCINC_ALIAS_KEY_HEX':'12'*32}
 return tmp_path,path,env

def test_missing_deployed_artifact_is_error(release):
 root,path,env=release;path.unlink()
 with pytest.raises(DeploymentError,match='No demo fallback'):load_dataset(configuration(root,environ=env,secrets={}),root)

def test_explicit_demo_needs_no_data_or_permission(tmp_path):
 c=configuration(tmp_path,environ={'DATA_MODE':'DEMO','BANCINC_RUNTIME':'CLOUD'},secrets={});assert load_dataset(c,tmp_path) is None

def test_missing_local_no_silent_demo(tmp_path):
 c=configuration(tmp_path,environ={},secrets={})
 with pytest.raises(DeploymentError,match='No demo fallback'):load_dataset(c,tmp_path)

def test_schema_mismatch(release):
 root,path,env=release;f=pd.read_csv(path);f['legal_name']='SYNTHETIC NAME';f.to_csv(path,index=False);env['DATA_SHA256']=hashlib.sha256(path.read_bytes()).hexdigest()
 with pytest.raises(DeploymentError,match='exactly'):load_dataset(configuration(root,environ=env,secrets={}),root)

def test_fingerprint_mismatch(release):
 root,path,env=release;env['DATA_SHA256']='a'*64
 with pytest.raises(DeploymentError,match='fingerprint'):load_dataset(configuration(root,environ=env,secrets={}),root)

def test_version_mismatch(release):
 root,path,env=release;env['DATA_VERSION']='different'
 with pytest.raises(DeploymentError,match='dataset_version'):load_dataset(configuration(root,environ=env,secrets={}),root)

def test_missing_manifest(release):
 root,path,env=release;manifest_path(path).unlink()
 with pytest.raises(DeploymentError,match='adjacent'):load_dataset(configuration(root,environ=env,secrets={}),root)

@pytest.mark.parametrize('field,value,code',[('DATA_RELEASE_APPROVAL_REFERENCE','','DATA_RELEASE_NOT_APPROVED'),('DATA_RELEASE_APPROVAL_REFERENCE','PENDING','DATA_RELEASE_NOT_APPROVED'),('DATA_SHA256','','EXPECTED_FINGERPRINT_REQUIRED'),('DATA_VERSION','','EXPECTED_VERSION_REQUIRED'),('BANCINC_ALIAS_KEY_HEX','bad','ALIAS_SECRET_REQUIRED'),('DATA_ACCESS_SCOPE','','DATA_ACCESS_SCOPE_REQUIRED'),('DATA_MODE','unknown','INVALID_DATA_MODE'),('BANCINC_RUNTIME','unknown','INVALID_RUNTIME')])
def test_deployment_configuration_fail_closed(release,field,value,code):
 root,path,env=release;env[field]=value
 with pytest.raises(DeploymentError) as exc:configuration(root,environ=env,secrets={})
 assert exc.value.code==code

@pytest.mark.parametrize('path',['/Users/example/features.csv','../features.csv'])
def test_deployed_absolute_or_parent_paths_rejected(tmp_path,path):
 with pytest.raises(DeploymentError):portable_path(path,tmp_path,True)

def test_portable_paths_independent_of_working_directory(tmp_path,monkeypatch):
 monkeypatch.chdir('/');assert portable_path('private_data/customer_features.csv',tmp_path)==tmp_path/'private_data/customer_features.csv'

def test_environment_precedes_secret_without_exposing_values():
 assert setting('DATA_MODE',secrets={'DATA_MODE':'DEMO'},environ={'DATA_MODE':'LOCAL'})=='LOCAL'
 assert setting('DATA_MODE',secrets={'DATA_MODE':'DEMO'},environ={})=='DEMO'

def test_cloud_requires_explicit_mode(tmp_path):
 with pytest.raises(DeploymentError,match='explicit'):configuration(tmp_path,environ={'BANCINC_RUNTIME':'CLOUD'},secrets={})

def test_ephemeral_cloud_audit_initializes_empty(tmp_path):
 from audit_store import AuditStore
 p,cloud=audit_configuration(tmp_path,environ={'DATA_MODE':'DEMO','BANCINC_RUNTIME':'CLOUD'},secrets={});assert cloud and p==tmp_path/'outputs/cloud_review.sqlite3';assert AuditStore(p).summary()['events']==0
 local,cloud=audit_configuration(tmp_path,environ={},secrets={});assert not cloud and local==tmp_path/'outputs/review_audit.sqlite3'

def test_alias_secret_conflict_never_rotates(release):
 root,path,env=release;c=configuration(root,environ=env,secrets={});load_dataset(c,root);key=root/'outputs/.presentation_alias_key';before=key.read_bytes()
 with pytest.raises(DeploymentError,match='conflicts'):load_dataset(replace(c,alias_hex='34'*32),root)
 assert key.read_bytes()==before

def test_manifest_and_policy_cache_invalidation(release):
 root,path,env=release;c=configuration(root,environ=env,secrets={});i=load_dataset(c,root);m=json.loads(manifest_path(path).read_text());m['feature_sha256']='0'*64;manifest_path(path).write_text(json.dumps(m))
 with pytest.raises(DeploymentError,match='manifest validation'):load_dataset(c,root)
 # Existing content/policy cache still invalidates on a new policy version.
 assert load_index(path,key=bytes.fromhex(c.alias_hex),policy_version='synthetic-new-policy').policy_hash!=i.policy_hash

def test_local_deployed_fixture_parity_privacy_and_no_outreach(release):
 root,path,env=release;c=configuration(root,environ=env,secrets={});deployed=load_dataset(c,root);local=load_index(path,key=bytes.fromhex(c.alias_hex));assert deployed.counts==local.counts;assert deployed.table().equals(local.table())
 for r in deployed.records:
  p=deployed.passport(r.alias);assert p['customer_id'].startswith('C-');assert 'SYNTHETIC-1' not in json.dumps(p);assert len(p['gates'])==6;assert p['human_review_required'] is True

def test_missing_data_ui_stops_without_synthetic_content(tmp_path,monkeypatch):
 monkeypatch.setenv('DATA_MODE','LOCAL');monkeypatch.setenv('BANCINC_FEATURES_PATH',str(tmp_path/'missing.csv'))
 app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();assert not app.exception;assert any('DATASET_UNAVAILABLE' in e.value for e in app.error);assert not any('SYNTHETIC' in i.value for i in app.info);assert not app.metric

def test_demo_ui_is_explicit_and_has_no_real_population(tmp_path,monkeypatch):
 monkeypatch.setenv('DATA_MODE','DEMO');monkeypatch.setenv('BANCINC_RUNTIME','CLOUD')
 app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();assert not app.exception;assert app.radio(key='data_source').value=='Synthetic gate demonstrations';assert any('SYNTHETIC' in i.value for i in app.info);assert not any(m.label=='Total evaluated customers' for m in app.metric)

def test_all_nine_deployed_views_and_cloud_notice(release,monkeypatch):
 from ui_shell import PAGES
 import tempfile,shutil
 root,path,env=release
 with tempfile.TemporaryDirectory(prefix='cloud-fixture-',dir=ROOT/'outputs') as d:
  folder=Path(d);target=folder/path.name;shutil.copyfile(path,target);shutil.copyfile(manifest_path(path),manifest_path(target))
  env.update(BANCINC_RUNTIME='CLOUD',BANCINC_FEATURES_PATH=str(target.relative_to(ROOT)),BANCINC_ALIAS_KEY_HEX=alias_key().hex(),BANCINC_AUDIT_DB=str((folder/'ui.sqlite3').relative_to(ROOT)))
  for k,v in env.items():monkeypatch.setenv(k,v)
  app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();assert not app.exception
  for slug,title,_ in PAGES:
   app.switch_page('views/'+slug+'.py').run();assert not app.exception and app.title[0].value==title
   if slug in {'manager_work_queue','audit_validation'}:assert any('EPHEMERAL CLOUD' in w.value for w in app.warning)
   for t in app.dataframe:assert 'SYNTHETIC-1' not in t.value.to_json()


def test_real_authorized_local_parity_only(tmp_path):
 # Read already-authorized local artifact in place. No cloud upload or public release.
 source=ROOT/'outputs/customer_features.csv';m=json.loads(manifest_path(source).read_text());m['dataset_version']='LOCAL-ONLY-PARITY-NOT-A-RELEASE'
 import shutil
 path=tmp_path/'customer_features.csv';shutil.copyfile(source,path);manifest_path(path).write_text(json.dumps(m))
 env={'DATA_MODE':'DEPLOYED','BANCINC_FEATURES_PATH':path.name,'DATA_SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'DATA_VERSION':m['dataset_version'],'DATA_RELEASE_APPROVAL_REFERENCE':'LOCAL VALIDATION ONLY; NO HOSTING AUTHORIZATION','DATA_ACCESS_SCOPE':'PRIVATE_HOST','BANCINC_ALIAS_KEY_HEX':alias_key().hex()}
 c=configuration(tmp_path,environ=env,secrets={});a=load_dataset(c,tmp_path);b=load_index(source);assert len(a.records)==len(b.records);assert a.counts==b.counts;assert a.table().equals(b.table())

def test_streamlit_secret_files_and_data_are_not_tracked():
 import subprocess
 tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines();assert '.streamlit/secrets.toml' not in tracked;assert not any(p.endswith(('.csv','.zip','.sqlite3')) for p in tracked)


def test_manifest_replacement_during_load_is_rejected(release,monkeypatch):
 import deployment_data
 root,path,env=release;c=configuration(root,environ=env,secrets={});original=deployment_data.load_index
 def changed(*args,**kwargs):
  result=original(*args,**kwargs);m=json.loads(manifest_path(path).read_text());m['dataset_version']='changed-during-load';manifest_path(path).write_text(json.dumps(m));return result
 monkeypatch.setattr(deployment_data,'load_index',changed)
 with pytest.raises(DeploymentError,match='changed during'):load_dataset(c,root)
