"""Aggregate before/after comparison against the audited local Git baseline; no raw IDs logged."""
from pathlib import Path
import argparse,sys,types,subprocess,collections,json,time,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from data_access import load_index, FEATURE_COLUMNS, row_case
from evidence import holdings


def compare(features,out,baseline_ref):
    source=subprocess.check_output(['git','show',baseline_ref+':engine.py'],cwd=ROOT,text=True)
    legacy=types.ModuleType('phase1_baseline_engine');sys.modules[legacy.__name__]=legacy
    exec(compile(source,'phase1_baseline_engine.py','exec'),legacy.__dict__)
    frame=pd.read_csv(features,dtype={'customer_id':str}).fillna({'recency_days':999,'behavioural_reason':''})
    old={}
    for values in frame[list(FEATURE_COLUMNS)].itertuples(index=False,name=None):
        row=dict(zip(FEATURE_COLUMNS,values))
        case=legacy.Case(customer_id=row['customer_id'],qualifying_events_180d=int(row['qualifying_events_180d']),recency_days=int(row['recency_days']),relationship_activity_percentile=float(row['relationship_activity_percentile']),service_issue=bool(row['service_issue']),products_held=holdings(row['products_held']),behavioural_reason=row['behavioural_reason'],customer_status=row['customer_status'],account_status=row['account_status'],kyc_status=row['kyc_status'])
        old[row['customer_id']]=legacy.evaluate(case)['rating']
    start=time.perf_counter();index=load_index(features);cold=time.perf_counter()-start
    start=time.perf_counter();again=load_index(features);warm=time.perf_counter()-start
    frame['priority_sort']=.45*(frame.recency_days/90).clip(0,1)+.35*frame.relationship_activity_percentile+.2*frame.service_issue.astype(int)
    top=frame.sort_values('priority_sort',ascending=False).head(1500)
    changed=sum(old[r.values[0]]!=r.rating for r in index.records)
    result={'baseline_git_ref':baseline_ref,'input_rows':index.input_rows,'evaluated_customers':len(index.records),'excluded_identity_rows':len(index.exclusions),'invalid_evidence_records':index.invalid_records,'before_permission_counts':dict(collections.Counter(old.values())),'after_permission_counts':index.counts,'changed_permission_outcomes':changed,'before_top1500_supported':sum(old[cid]=='SUPPORTED' for cid in top.customer_id),'after_actionable_queue_count':len(index.table('SUPPORTED')),'default_visible_page':len(index.page()),'default_page_size':25,'supported_page_count':(index.counts['SUPPORTED']+24)//25,'unique_aliases':len({r.alias for r in index.records}),'canonical_sha256':hashlib.sha256(Path(features).read_bytes()).hexdigest(),'policy_sha256':index.policy_hash,'cold_index_seconds':round(cold,3),'warm_index_seconds':round(warm,3),'warm_cache_identity_reused':again is index}
    expected=json.loads((ROOT/'outputs/phase1_audit/preservation.json').read_text())['before']['outputs/customer_features.csv']
    result['canonical_matches_phase1_sha256']=result['canonical_sha256']==expected
    assert result['canonical_matches_phase1_sha256']
    Path(out).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--features',default='outputs/customer_features.csv');p.add_argument('--out',default='outputs/phase2/queue_comparison.json');p.add_argument('--baseline-ref',default='01b2729');a=p.parse_args();compare(a.features,a.out,a.baseline_ref)
