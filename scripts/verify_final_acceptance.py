"""Fail-closed local acceptance gate: no failed/skipped tests, decision drift or unverified inference."""
from pathlib import Path
import sys,argparse,json,hashlib,math
from datetime import datetime,timezone
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from acceptance_checks import verify_local_baseline,sha256,verify_run_manifest


def inspect_junit(path):
 root=E.parse(path).getroot();suites=[root] if root.tag=='testsuite' else list(root.findall('testsuite'));cases=list(root.iter('testcase'))
 if not suites or not cases:raise AssertionError('Missing or empty regression evidence.')
 totals={k:sum(int(s.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
 assert totals['tests']==len(cases),'JUnit collection totals inconsistent.'
 unresolved=[{'module':t.get('classname'),'test':t.get('name'),'result':child.tag,'message':child.get('message','')} for t in cases for child in t if child.tag in {'failure','error','skipped'}]
 assert not unresolved and not any(totals[k] for k in ('failures','errors','skipped')),'Regression failures/errors/skips remain; acceptance is not granted.'
 return totals,{(t.get('classname'),t.get('name')) for t in cases}


REQUIRED_INVENTORY=ROOT/'tests/fixtures/required_test_inventory.json'

def load_required_inventory(baseline_junit=None):
 inventory=json.loads(REQUIRED_INVENTORY.read_text())
 assert inventory.get('schema_version')==1,'Unsupported required-test inventory.'
 required={tuple(item) for item in inventory.get('required_test_ids',[])}
 assert required and len(required)==inventory.get('required_count')==len(inventory['required_test_ids']),'Invalid required-test inventory.'
 baseline=Path(baseline_junit) if baseline_junit else ROOT/inventory['baseline_junit']
 assert sha256(baseline)==inventory['baseline_junit_sha256'],'Prior JUnit is not the reviewed hash-pinned baseline.'
 _,prior_ids=inspect_junit(baseline)
 assert prior_ids==required,'Required inventory differs from its reviewed prior JUnit.'
 return inventory,required,baseline

def verify_test_retention(ids,junit,baseline_junit=None):
 inventory,required,baseline=load_required_inventory(baseline_junit)
 assert Path(junit).resolve()!=baseline.resolve() and sha256(junit)!=inventory['baseline_junit_sha256'],'Current run cannot be its own prior retention reference.'
 assert required<=ids,'Existing protected test identifiers were removed.'
 return inventory,required


def verify_models():
 a=json.loads((ROOT/'outputs/phase5/evaluation/evaluation.json').read_text());b=json.loads((ROOT/'outputs/phase5/evaluation_repeat/evaluation.json').read_text())
 assert a['experimental_only'] is True and b['experimental_only'] is True
 assert a['evaluation_code_sha256']==b['evaluation_code_sha256']==sha256(ROOT/'historical_evaluation.py')
 assert a['canonical_feature_sha256']==b['canonical_feature_sha256']==sha256(ROOT/'outputs/customer_features.csv')
 assert a['configuration']==b['configuration'] and a['train']==b['train'] and a['holdout']==b['holdout']
 assert set(a['models'])==set(b['models'])=={'recency_only','logistic_regression','histogram_gradient_boosting'}
 fields=['roc_auc','pr_auc_average_precision','pr_auc_trapezoidal','precision_at_k','lift_at_k','score_sha256']
 for model in a['models']:
  for key in fields:assert a['models'][model][key]==b['models'][model][key], 'Experimental reproduction mismatch.'
  for key in fields[:-1]:assert math.isfinite(a['models'][model][key]),'Nonfinite experimental output.'
 return {'scope':'previously executed two real-source historical runs; artifacts reverified now, no new model training in this acceptance run','models':list(a['models']),'metrics_and_prediction_fingerprints_identical':True,'provenance_code_and_dataset_match':True,'operational_deployment':False,'limits':'one chronological repeated-customer holdout on competition extract; no production validity, calibration or intervention benefit claim'}


def verify(junit,out,baseline_junit=None,run_manifest=None):
 out=Path(out)
 if out.exists():raise FileExistsError('Use a fresh final acceptance report path; never overwrite past results.')
 run_evidence=verify_run_manifest(junit,run_manifest or Path(junit).with_name('run_manifest.json'))
 totals,ids=inspect_junit(junit);inventory,old=verify_test_retention(ids,junit,baseline_junit)
 assert any(module=='tests.test_gate_protection' for module,_ in ids),'Mandatory combination/anti-bypass tests not included.'
 baseline=verify_local_baseline();models=verify_models()
 before=json.loads((ROOT/'outputs/final_acceptance/before_hashes.json').read_text());before.update(inventory.get('protected_artifact_hashes',{}));preserved={f:sha256(ROOT/f)==h for f,h in before.items()};assert all(preserved.values()),'Protected application/data/evaluation artifacts changed.'
 report={'status':'PASS','checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'local final-presentation technical acceptance; no bank authorization or external data-release permission','tests':totals,'passed':totals['tests'],'prior_test_ids_retained':len(old),'new_test_ids':len(ids-old),'junit_sha256':sha256(junit),'retention_baseline_sha256':inventory['baseline_junit_sha256'],'source_run_verification':run_evidence,'local_baseline':baseline,'protected_artifacts_unchanged':preserved,'experimental_outputs':models,'operational_method':'unchanged deterministic six-gate rules','gate_combination_cases':sum(module=='tests.test_gate_protection' and name.startswith('test_all_gate_combinations') for module,name in ids),'production_authorization':False,'automatic_outreach':False,'data_publication':False,'limitations':['live cloud real-data parity remains unverified and permission-gated','cloud SQLite is ephemeral; local SQLite is owner-trusted and unencrypted','current snapshot effective dates unknown; source-event mapping remains feature-level','historical reported concept figures must not be represented as newly verified operational predictions']}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--junit',default=str(ROOT/'outputs/final_acceptance/tests.xml'));p.add_argument('--out',default=str(ROOT/'outputs/final_acceptance/acceptance.json'));p.add_argument('--run-manifest');p.add_argument('--baseline-junit');a=p.parse_args()
 try:verify(Path(a.junit),Path(a.out),a.baseline_junit,a.run_manifest)
 except (AssertionError,OSError,ValueError,E.ParseError) as exc:
  print(json.dumps({'status':'FAIL','reason':str(exc),'acceptance_granted':False}));raise SystemExit(1)
