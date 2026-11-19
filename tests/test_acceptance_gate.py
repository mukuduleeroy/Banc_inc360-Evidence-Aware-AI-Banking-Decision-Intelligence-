"""The final-acceptance checker must reject incomplete or failed regression evidence."""
from pathlib import Path
import importlib.util
import pytest
spec=importlib.util.spec_from_file_location('final_acceptance_checker',Path(__file__).resolve().parents[1]/'scripts/verify_final_acceptance.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)

@pytest.mark.parametrize('child,field',[('failure','failures'),('error','errors'),('skipped','skipped')])
def test_acceptance_rejects_unresolved_junit(tmp_path,child,field):
 path=tmp_path/'failed.xml';path.write_text(f'<testsuite tests="1" {field}="1"><testcase name="controlled"><{child} message="SYNTHETIC failure"/></testcase></testsuite>')
 with pytest.raises(AssertionError,match='acceptance is not granted'):checker.inspect_junit(path)

@pytest.mark.parametrize('xml',['<testsuite tests="0"/>','<testsuite tests="2"><testcase name="only-one"/></testsuite>'])
def test_acceptance_rejects_empty_or_inconsistent_collection(tmp_path,xml):
 path=tmp_path/'incomplete.xml';path.write_text(xml)
 with pytest.raises(AssertionError):checker.inspect_junit(path)


def test_acceptance_accepts_only_complete_passing_collection(tmp_path):
 path=tmp_path/'passed.xml';path.write_text('<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase classname="controlled" name="passed"/></testsuite>')
 totals,ids=checker.inspect_junit(path);assert totals==dict(tests=1,failures=0,errors=0,skipped=0);assert ids=={('controlled','passed')}


def make_run(tmp_path):
 import json
 from acceptance_checks import source_snapshot,sha256
 (tmp_path/'app.py').write_text('# Controlled synthetic source snapshot\n')
 junit=tmp_path/'tests.xml';junit.write_text('<testsuite tests="1"><testcase name="controlled"/></testsuite>');snapshot=source_snapshot(tmp_path);manifest=tmp_path/'run_manifest.json';manifest.write_text(json.dumps({'status':'PASS','pytest_exit_code':0,'before_source_hashes':snapshot,'after_source_hashes':snapshot,'junit_sha256':sha256(junit)}));return junit,manifest


def test_acceptance_rejects_post_test_source_edit(tmp_path):
 from acceptance_checks import verify_run_manifest
 junit,manifest=make_run(tmp_path);(tmp_path/'app.py').write_text('# Changed AFTER the passing run\n')
 with pytest.raises(AssertionError,match='Sources changed'):verify_run_manifest(junit,manifest,tmp_path)


def test_acceptance_rejects_altered_junit_bytes(tmp_path):
 from acceptance_checks import verify_run_manifest
 junit,manifest=make_run(tmp_path);junit.write_text('<testsuite tests="0"/>')
 with pytest.raises(AssertionError,match='JUnit evidence differs'):verify_run_manifest(junit,manifest,tmp_path)


def test_acceptance_source_snapshot_excludes_secrets_and_datasets(tmp_path):
 from acceptance_checks import source_snapshot,verify_run_manifest
 junit,manifest=make_run(tmp_path);(tmp_path/'.streamlit').mkdir();(tmp_path/'.streamlit/secrets.toml').write_text('SYNTHETIC_SECRET="DO_NOT_HASH"');(tmp_path/'customer_features.csv').write_text('SYNTHETIC DATA')
 snapshot=source_snapshot(tmp_path);assert set(snapshot)=={'app.py'};assert verify_run_manifest(junit,manifest,tmp_path)['source_files_verified']==1


def test_complete_report_path_requires_and_records_source_run_evidence(tmp_path,monkeypatch):
 import json
 junit=tmp_path/'tests.xml';junit.write_text('<testsuite tests="1"><testcase classname="tests.test_gate_protection" name="test_all_gate_combinations[controlled]"/></testsuite>');before=tmp_path/'outputs/final_acceptance';before.mkdir(parents=True);(before/'before_hashes.json').write_text('{}');calls=[]
 def checked(junit_arg,manifest_arg):
  calls.append((junit_arg,manifest_arg));return {'source_unchanged_during_and_after_run':True}
 monkeypatch.setattr(checker,'ROOT',tmp_path);monkeypatch.setattr(checker,'verify_run_manifest',checked);monkeypatch.setattr(checker,'verify_local_baseline',lambda:{'scope':'SYNTHETIC TEST ONLY'});monkeypatch.setattr(checker,'verify_models',lambda:{'scope':'SYNTHETIC TEST ONLY'})
 prior=tmp_path/'prior.xml';prior.write_text('<testsuite tests="1" timestamp="prior"><testcase classname="tests.test_gate_protection" name="test_all_gate_combinations[controlled]"/></testsuite>')
 inventory=tmp_path/'inventory.json';inventory.write_text(json.dumps({'schema_version':1,'baseline_junit':str(prior),'baseline_junit_sha256':checker.sha256(prior),'required_count':1,'required_test_ids':[['tests.test_gate_protection','test_all_gate_combinations[controlled]']]}));monkeypatch.setattr(checker,'REQUIRED_INVENTORY',inventory)
 out=tmp_path/'acceptance.json';r=checker.verify(junit,out,prior);assert calls==[(junit,tmp_path/'run_manifest.json')];assert r['source_run_verification']['source_unchanged_during_and_after_run'];assert json.loads(out.read_text())['status']=='PASS'


def test_report_cannot_be_generated_without_run_manifest(tmp_path):
 junit=tmp_path/'tests.xml';junit.write_text('<testsuite tests="1"><testcase name="controlled"/></testsuite>');out=tmp_path/'acceptance.json'
 with pytest.raises(FileNotFoundError):checker.verify(junit,out,junit)
 assert not out.exists()


def test_reviewed_inventory_retains_all_443_cases():
 inventory,ids,prior=checker.load_required_inventory();assert len(ids)==443 and inventory['required_count']==443;assert sum(m=='tests.test_gate_protection' and n.startswith('test_all_gate_combinations') for m,n in ids)==96

@pytest.mark.parametrize('prefix',['test_all_gate_combinations','test_forged_supported_rating_cannot_create_review'])
def test_missing_existing_gate_protection_case_fails_acceptance(tmp_path,prefix):
 inventory,required,_=checker.load_required_inventory();deleted=next(t for t in required if t[0]=='tests.test_gate_protection' and t[1].startswith(prefix));current=tmp_path/'current.xml';current.write_text('controlled current-run bytes')
 with pytest.raises(AssertionError,match='protected test identifiers'):checker.verify_test_retention(required-{deleted},current)

def test_current_run_cannot_be_its_own_retention_baseline():
 inventory,ids,prior=checker.load_required_inventory()
 with pytest.raises(AssertionError,match='own prior'):checker.verify_test_retention(ids,prior,prior)

def test_older_308_baseline_cannot_replace_reviewed_443():
 _,ids,_=checker.load_required_inventory()
 with pytest.raises(AssertionError,match='hash-pinned'):checker.verify_test_retention(ids,Path('outputs/final_acceptance/verified_final/tests.xml'),Path('outputs/phase7/tests.xml'))

def test_inventory_cannot_drop_case_while_retaining_prior_hash(tmp_path,monkeypatch):
 import json
 inventory,ids,_=checker.load_required_inventory();inventory['required_test_ids'].pop();inventory['required_count']-=1;path=tmp_path/'tampered.json';path.write_text(json.dumps(inventory));monkeypatch.setattr(checker,'REQUIRED_INVENTORY',path)
 with pytest.raises(AssertionError,match='differs'):checker.load_required_inventory()
