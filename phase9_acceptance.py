"""Additive Phase 9 acceptance: retain all 504 Phase 8B cases and original source bytes."""
from pathlib import Path
import argparse,json,subprocess,sys
from xml.etree import ElementTree as E
from acceptance_checks import source_snapshot,sha256,verify_local_baseline,verify_run_manifest
from phase9_ingestion import digest

ROOT=Path(__file__).resolve().parent

def verify_phase9(run_dir):
    out=Path(run_dir);checkpoint=json.loads((ROOT/'outputs/phase9/checkpoint.json').read_text())
    original=ROOT/'outputs/final_acceptance/phase-8b-final/tests.xml'
    assert sha256(original)==checkpoint['prior_junit_sha256'],'Accepted prior JUnit changed.'
    prior={(t.get('classname'),t.get('name')) for t in E.parse(original).iter('testcase')};assert len(prior)==504
    current={(t.get('classname'),t.get('name')) for t in E.parse(out/'tests.xml').iter('testcase')};assert prior<=current,'A protected Phase 8B test case is missing.'
    accepted=json.loads((out/'acceptance.json').read_text());assert accepted['status']=='PASS' and accepted['passed']==len(current)
    proof=verify_run_manifest(out/'tests.xml',out/'run_manifest.json');source=source_snapshot()
    assert all(source.get(f)==h for f,h in checkpoint['source_hashes'].items()),'Accepted Phase 8B source changed.'
    preserved={key:{f:digest(ROOT/f)==h for f,h in checkpoint[key].items()} for key in ('protected_hashes','existing_database_hashes')}
    assert all(all(items.values()) for items in preserved.values()),'Protected artifacts or prior database histories changed.'
    baseline=verify_local_baseline()
    result={'status':'PASS','retained_phase8b_cases':len(prior),'new_cases':len(current-prior),'total_passed':len(current),'accepted_source_files_unchanged':len(checkpoint['source_hashes']),'source_run_verification':proof,'preservation':preserved,'baseline':baseline,'feature_contract_columns':16,'scope':'controlled local demonstration; companion-only activation; no production authorization or data release'}
    report=out/'phase9_acceptance.json'
    with report.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='preservation'},indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out-dir',required=True);p.add_argument('--verify-only',action='store_true');args=p.parse_args();out=Path(args.out_dir).resolve()
    if not args.verify_only:
        subprocess.run([sys.executable,str(ROOT/'scripts/run_final_regression.py'),'--out-dir',str(out)],cwd=ROOT,check=True)
    verify_phase9(out)
