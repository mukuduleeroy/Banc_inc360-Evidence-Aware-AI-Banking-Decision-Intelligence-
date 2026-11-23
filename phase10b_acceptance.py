"""Additive full acceptance retaining every Phase 9 case and protected source/state byte."""
from pathlib import Path
import argparse,json,subprocess,sys
from xml.etree import ElementTree as E
from acceptance_checks import source_snapshot,sha256,verify_run_manifest,decision_fingerprint
from phase10b_value import load_accepted_index,value_reconciliation
from phase10b_upsell import demo_summary
ROOT=Path(__file__).resolve().parent

def verify_phase10b(out):
    out=Path(out);checkpoint=json.loads((ROOT/'outputs/phase10b/checkpoint.json').read_text());original=ROOT/'outputs/final_acceptance/phase-9-final/tests.xml'
    assert sha256(original)==checkpoint['prior_junit_sha256'],'Prior accepted 574-case evidence changed.'
    prior={(t.get('classname'),t.get('name')) for t in E.parse(original).iter('testcase')};assert len(prior)==574
    current={(t.get('classname'),t.get('name')) for t in E.parse(out/'tests.xml').iter('testcase')};assert prior<=current,'A protected Phase 9 test identifier is missing.'
    accepted=json.loads((out/'phase9_acceptance.json').read_text());assert accepted['status']=='PASS' and accepted['total_passed']==len(current)
    proof=verify_run_manifest(out/'tests.xml',out/'run_manifest.json');source=source_snapshot();assert all(source.get(f)==h for f,h in checkpoint['source_hashes'].items()),'Accepted application source changed.'
    preserved={f:sha256(ROOT/f)==h for f,h in checkpoint['protected_hashes'].items()};assert all(preserved.values()),'Protected data/report/evaluation/registry/snapshot/history changed.'
    index=load_accepted_index();proxy=value_reconciliation(index);assert proxy['reconciled'] and proxy['classifications']['High Relationship Activity — Potential Value Review']==proxy['existing_higher_activity_band'] and proxy['unavailable_evidence']==0
    report={'status':'PASS','retained_phase9_cases':len(prior),'new_cases':len(current-prior),'total_passed':len(current),'accepted_source_files_unchanged':len(checkpoint['source_hashes']),'source_run_verification':proof,'protected_artifacts_unchanged':preserved,'original_counts':index.counts,'original_customers':len(index.records),'original_decision_digest':decision_fingerprint(index),'proxy_reconciliation':proxy,'synthetic_upsell_population':demo_summary(),'operational_upgrade_authorization':False,'bank_approved_product_specification':False,'scope':'controlled local synthetic upselling and original source-derived activity proxy only'}
    with (out/'phase10b_acceptance.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!='protected_artifacts_unchanged'},indent=2));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out-dir',required=True);parser.add_argument('--verify-only',action='store_true');args=parser.parse_args();out=Path(args.out_dir).resolve()
    if not args.verify_only:subprocess.run([sys.executable,str(ROOT/'phase9_acceptance.py'),'--out-dir',str(out)],cwd=ROOT,check=True)
    verify_phase10b(out)
