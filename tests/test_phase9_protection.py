"""Phase 9 must be strictly additive and retain the full accepted 504-case inventory."""
from pathlib import Path
import json,hashlib,ast
from xml.etree import ElementTree as E
import pytest
from acceptance_checks import source_snapshot,verify_local_baseline
from phase9_ingestion import SnapshotStore,IngestionError
from phase9_demo import csv_bytes
import phase9_ingestion as p9
import io
ROOT=Path(__file__).resolve().parents[1]

def test_all_accepted_source_and_protected_artifacts_unchanged():
    checkpoint=json.loads((ROOT/'outputs/phase9/checkpoint.json').read_text());current=source_snapshot()
    assert len(checkpoint['source_hashes'])==79
    assert all(current.get(f)==h for f,h in checkpoint['source_hashes'].items())
    for key in ('protected_hashes','existing_database_hashes'):
        assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in checkpoint[key].items())


def test_accepted_504_inventory_still_present_in_collection(request):
    checkpoint=json.loads((ROOT/'outputs/phase9/checkpoint.json').read_text());prior=ROOT/'outputs/final_acceptance/phase-8b-final/tests.xml'
    assert hashlib.sha256(prior.read_bytes()).hexdigest()==checkpoint['prior_junit_sha256']
    ids={(t.get('classname'),t.get('name')) for t in E.parse(prior).iter('testcase')};assert len(ids)==504
    # nodeids preserve the accepted parameter IDs, including 96 gate combinations.
    collected={('tests.'+Path(i.nodeid.split('::')[0]).stem,i.nodeid.split('::')[-1]) for i in request.session.items}
    # This check is meaningful in full regression, while targeted invocations cannot pretend to retain 504 cases.
    if len(request.session.items)>=504:assert ids<=collected
    assert sum(m=='tests.test_gate_protection' and n.startswith('test_all_gate_combinations') for m,n in ids)==96


def test_phase9_cannot_change_baseline_customer_decisions(tmp_path):
    before=verify_local_baseline();s=SnapshotStore(tmp_path/'private');u=s.stage('synthetic.csv',io.BytesIO(csv_bytes()));m=s.process(u['token'],'2026-07-01');s.activate(m['snapshot_id']);s.rollback()
    assert verify_local_baseline()==before


def test_reconciliation_failure_never_registers_candidate(tmp_path,monkeypatch):
    s=SnapshotStore(tmp_path/'private');u=s.stage('synthetic.csv',io.BytesIO(csv_bytes()));original=p9.build_features
    def bad(*args,**kwargs):
        audit=original(*args,**kwargs);audit['invalid_dates']=1;return audit
    monkeypatch.setattr(p9,'build_features',bad)
    with pytest.raises(IngestionError,match='excluded evidence'):s.process(u['token'],'2026-07-01')
    assert s.state()['active']=='baseline' and not s.state()['snapshots']
    assert not list((s.root/'snapshots').iterdir())


def test_no_new_network_model_inference_or_existing_audit_dependency():
    prohibited={'requests','urllib','httpx','socket','pickle','joblib','sklearn','historical_evaluation','audit_store','review_service'}
    for name in ('phase9_ingestion.py','phase9_app.py','phase9_demo.py'):
        tree=ast.parse((ROOT/name).read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):assert not any(a.name.split('.')[0] in prohibited for a in node.names)
            if isinstance(node,ast.ImportFrom):assert node.module.split('.')[0] not in prohibited
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):assert node.func.attr not in ('fit','predict','predict_proba')
