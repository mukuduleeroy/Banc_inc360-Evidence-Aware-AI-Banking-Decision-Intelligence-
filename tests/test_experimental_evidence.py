"""Metadata-only synthetic corruption tests; never fit or load a model."""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,json,math,ast
import pytest
from experimental_evidence import load_historical_comparison,TRUSTED_ARTIFACT_SHA256,LIVE_UNAVAILABLE
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def evidence(tmp_path):
 a=json.loads((ROOT/'outputs/phase5/evaluation/evaluation.json').read_text());m=json.loads((ROOT/'outputs/customer_features.manifest.json').read_text());p=tmp_path/'historical.json';p.write_text(json.dumps(a));f=tmp_path/'features.csv';f.with_suffix('.manifest.json').write_text(json.dumps(m));i=SimpleNamespace(dataset_hash=a['canonical_feature_sha256'],lineage_issues=(),input_rows=m['rows'],records=range(m['rows']),cutoff=m['cutoff']);return a,p,f,i

def read(evidence,change=None):
 a,p,f,i=evidence
 if change:change(a)
 p.write_text(json.dumps(a));return load_historical_comparison(i,artifact_path=p,feature_path=f,expected_sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def test_verified_values_are_read_not_hardcoded(evidence):
 a,p,f,i=evidence;r=read(evidence);assert r.status=='Verified' and len(r.rows)==3;assert r.rows[1][1]==a['models']['logistic_regression']['roc_auc'];assert r.training_customers==a['train']['customers'];assert r.holdout_customers==a['holdout']['customers'];assert r.shared_customers==a['shared_customers'];assert 'Unavailable' in LIVE_UNAVAILABLE

def test_actual_artifact_pin_matches_reviewed_bytes():assert hashlib.sha256((ROOT/'outputs/phase5/evaluation/evaluation.json').read_bytes()).hexdigest()==TRUSTED_ARTIFACT_SHA256

@pytest.mark.parametrize('change',[lambda a:a.update(artifact_version='future'),lambda a:a.update(experimental_only=False),lambda a:a['configuration'].update(target_days=30),lambda a:a.update(target_definition='verified churn'),lambda a:a['features'].update(kyc_status='forbidden'),lambda a:a['train'].update(positives=0),lambda a:a['holdout'].update(prevalence=.1),lambda a:a.update(shared_customers=999999),lambda a:a['models']['recency_only'].update(roc_auc=float('nan')),lambda a:a['models']['recency_only'].update(pr_auc_average_precision=1.1),lambda a:a['models']['recency_only'].pop('pr_auc_average_precision'),lambda a:a['models']['recency_only'].update(lift_at_k=999),lambda a:a['models']['recency_only'].update(cohort_size=5),lambda a:a['models']['recency_only'].update(effective_k=499)],ids=['version','approval','window','target','feature-leakage','cohort','prevalence','shared','nan','range','missing-ap','lift','model-cohort','top-k'])
def test_malformed_inconsistent_metadata_has_no_metrics(evidence,change):
 r=read(evidence,change);assert r.status=='Unavailable' and not r.rows

@pytest.mark.parametrize('field',['canonical_feature_sha256','source_sha256','evaluation_code_sha256'])
def test_stale_fingerprints_have_no_metrics(evidence,field):
 r=read(evidence,lambda a:a.update({field:'0'*64}));assert r.status=='Stale' and not r.rows

def test_unreviewed_metric_edit_fails_content_pin(evidence):
 a,p,f,i=evidence;original=hashlib.sha256(p.read_bytes()).hexdigest();a['models']['recency_only']['roc_auc']=.1;p.write_text(json.dumps(a));r=load_historical_comparison(i,artifact_path=p,feature_path=f,expected_sha256=original);assert r.code=='ARTIFACT_HASH_MISMATCH' and not r.rows

def test_missing_or_bad_json_is_unavailable(evidence):
 a,p,f,i=evidence;p.unlink();assert load_historical_comparison(i,artifact_path=p,feature_path=f).status=='Unavailable';p.write_text('malformed');assert load_historical_comparison(i,artifact_path=p,feature_path=f).status=='Unavailable'

def test_manifest_or_index_mismatch_is_stale(evidence):
 a,p,f,i=evidence;read(evidence);m=json.loads(f.with_suffix('.manifest.json').read_text());m['cutoff']='2026-01-01';f.with_suffix('.manifest.json').write_text(json.dumps(m));assert read(evidence).status=='Stale'

def test_unknown_metadata_never_leaks_to_view(evidence):
 r=read(evidence,lambda a:a.update(customer_id='PRIVATE-ID',private_text='secret'));assert 'PRIVATE-ID' not in repr(r) and 'secret' not in repr(r)

def test_runtime_reader_has_no_fit_inference_or_deserialization():
 tree=ast.parse((ROOT/'experimental_evidence.py').read_text());calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)];assert not any(isinstance(n.func,ast.Attribute) and n.func.attr in {'fit','fit_transform','predict','predict_proba'} for n in calls)
 imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]+[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names];assert not any(m and m.startswith(('sklearn','joblib','pickle','historical_evaluation')) for m in imports)
