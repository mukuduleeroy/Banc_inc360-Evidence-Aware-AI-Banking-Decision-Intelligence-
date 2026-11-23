"""Read-only baseline/state and original engine/proxy namespace isolation."""
from pathlib import Path
import ast,hashlib,json
from xml.etree import ElementTree as E
from acceptance_checks import source_snapshot,decision_fingerprint
from phase10b_upsell import demo_scenarios,assess_upsell,demo_summary
from phase10b_value import load_accepted_index,value_frame
ROOT=Path(__file__).resolve().parents[1]

def test_all_87_accepted_sources_and_protected_state_remain_unchanged():
    cp=json.loads((ROOT/'outputs/phase10b/checkpoint.json').read_text());current=source_snapshot();assert len(cp['source_hashes'])==87
    assert all(current.get(f)==h for f,h in cp['source_hashes'].items())
    assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in cp['protected_hashes'].items())


def test_original_decisions_priorities_reasons_and_aliases_never_change():
    ix=load_accepted_index();before=decision_fingerprint(ix);aliases=tuple(r.alias for r in ix.records);values=tuple((r.rating,r.priority,r.reason_codes,r.values) for r in ix.records)
    for _,c,s in demo_scenarios():assess_upsell(c,s)
    value_frame(ix)
    assert decision_fingerprint(ix)==before and tuple(r.alias for r in ix.records)==aliases
    assert tuple((r.rating,r.priority,r.reason_codes,r.values) for r in ix.records)==values
    assert set(demo_summary()['counts']).isdisjoint(ix.counts)


def test_prior_574_inventory_in_full_regression(request):
    cp=json.loads((ROOT/'outputs/phase10b/checkpoint.json').read_text());p=ROOT/'outputs/final_acceptance/phase-9-final/tests.xml'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==cp['prior_junit_sha256']
    prior={(t.get('classname'),t.get('name')) for t in E.parse(p).iter('testcase')};assert len(prior)==574
    if len(request.session.items)>=574:
        collected={('tests.'+Path(i.nodeid.split('::')[0]).stem,i.nodeid.split('::')[-1]) for i in request.session.items}
        assert prior<=collected


def test_no_write_registry_review_network_or_live_model_runtime_dependency():
    prohibited={'phase9_ingestion','audit_store','review_service','sqlite3','pickle','joblib','sklearn','historical_evaluation','requests','httpx','urllib','socket'}
    for filename in ('phase10b_upsell.py','phase10b_value.py','phase10b_app.py'):
        tree=ast.parse((ROOT/filename).read_text())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):assert all(a.name.split('.')[0] not in prohibited for a in n.names)
            if isinstance(n,ast.ImportFrom):assert n.module.split('.')[0] not in prohibited
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):assert n.func.attr not in ('fit','predict','predict_proba','write_text','write_bytes','to_csv','activate','record_review')
    assert set(demo_summary()['counts']).isdisjoint({'SUPPORTED','CAUTION','ABSTAIN'})
