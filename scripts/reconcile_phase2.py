"""Read source, build a separate candidate, compare, and attest identical canonical features.
No canonical CSV is ever replaced. Run with --zip and a new --out directory.
"""
import argparse
from pathlib import Path
import sys,json,time
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_data import run, file_hash
from data_access import load_index, manifest_path


def reconcile(source, canonical, out):
    source, canonical, out = Path(source), Path(canonical), Path(out)
    before = file_hash(canonical)
    audit = run(source, out/'candidate')
    old = pd.read_csv(canonical,dtype={'customer_id':str}).set_index('customer_id').sort_index()
    new = pd.read_csv(out/'candidate/customer_features.csv',dtype={'customer_id':str}).set_index('customer_id').sort_index()
    keys_equal = old.index.equals(new.index)
    differences = {c:int((old[c].fillna('').astype(str)!=new[c].fillna('').astype(str)).sum()) for c in old.columns} if keys_equal else None
    identical = keys_equal and set(old.columns)==set(new.columns) and not any(differences.values())
    result = {'canonical_sha256_before':before,'canonical_sha256_after':file_hash(canonical),'keys_equal':keys_equal,'column_differences':differences,'identical':identical,'builder_audit':audit}
    if identical:
        manifest = json.loads(manifest_path(out/'candidate/customer_features.csv').read_text())
        manifest.update(feature_sha256=before,verification='source_rebuild_compared')
        target = manifest_path(canonical)
        if target.exists() and json.loads(target.read_text()) != manifest:
            raise ValueError('Existing canonical manifest differs; review before replacing it.')
        if not target.exists():target.write_text(json.dumps(manifest,indent=2))
        start=time.perf_counter();index=load_index(canonical)
        result.update(evaluated=len(index.records),input_rows=index.input_rows,excluded_rows=len(index.exclusions),invalid_evidence_records=index.invalid_records,counts=index.counts,actionable_cases=index.counts['SUPPORTED'],alias_count=len({r.alias for r in index.records}),dataset_hash=index.dataset_hash,policy_hash=index.policy_hash,index_seconds=round(time.perf_counter()-start,3),first_page_count=len(index.page()))
    else:
        result['approval_needed_before_canonical_replacement']=True
    assert before==file_hash(canonical)
    (out/'reconciliation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--features',default='outputs/customer_features.csv');p.add_argument('--out',required=True);a=p.parse_args();reconcile(a.zip,a.features,a.out)
