"""Reproducible point-in-time feature extraction. Run with --zip path/to/dataset.zip."""
import argparse,zipfile,json,math,hashlib
from pathlib import Path
import pandas as pd
from evidence import state as normalize_state, identifier, CUSTOMER_STATES, ACCOUNT_STATES, KYC_STATES
from data_access import BUILDER_VERSION, EVENT_DEFINITION, manifest_path

KNOWN_TYPES = {'SERVICE FEE', 'FOREX_PURCHASE', 'CASH_DEPOSIT', 'POS_PURCHASE', 'ATM_WITHDRAWAL', 'BILL_PAYMENT'}

def file_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def run(path,out='outputs',cutoff='2026-07-01'):
    path=Path(path).expanduser()
    if not path.is_file():
        raise FileNotFoundError('Dataset ZIP not found. Supply an existing local file using --zip.')
    out=Path(out)
    if (out/'customer_features.csv').exists():
        raise FileExistsError('Feature output already exists. Use a new output directory; canonical data is never replaced automatically.')
    out.mkdir(parents=True,exist_ok=True)
    fields=['Customer ID','Account ID','account_customer_id','Transaction ID','transaction_date','Type','Amount (USD)','dr_cr_indicator','products_held','customer_status','account_status','kyc_status','service_reasons','customer_segment']
    if cutoff is None:
        raise ValueError('Observation cutoff is required.')
    cutoff=pd.Timestamp(cutoff)
    if pd.isna(cutoff) or cutoff.tz is not None or cutoff != cutoff.normalize():
        raise ValueError('Cutoff must be a valid timezone-naive observation date at midnight.')
    state={}; total=0; bad_links=0;bad_dates=0;dups=0;ids=set();history_ids=set();future_ids=set();invalid_amounts=0;unknown_types=0;invalid_identifiers=0;cohort=set();ownership={};conflicts=set()
    with zipfile.ZipFile(path) as z:
        members=[n for n in z.namelist() if n.lower().endswith('.csv')]
        if len(members)!=1:
            raise ValueError('Dataset ZIP must contain exactly one CSV.')
        name=members[0]
        for chunk in pd.read_csv(z.open(name),usecols=fields,chunksize=35000,dtype=str,low_memory=False):
            total+=len(chunk)
            chunk['dt']=pd.to_datetime(chunk['transaction_date'],format='mixed',dayfirst=True,errors='coerce')
            bad_dates+=int(chunk['dt'].isna().sum())
            bad_links+=int((chunk['Customer ID']!=chunk['account_customer_id']).sum())
            for row in chunk.itertuples(index=False,name=None):
                d=dict(zip(chunk.columns,row)); cid=str(d['Customer ID']); tid=str(d['Transaction ID'])
                if not all(identifier(d[name]) for name in ('Customer ID','Account ID','Transaction ID')):
                    invalid_identifiers+=1;continue
                if d['Customer ID'] != d['account_customer_id'] or pd.isna(d['dt']):
                    continue
                kind=str(d['Type']).upper()
                if kind not in KNOWN_TYPES:
                    unknown_types+=1;continue
                try: amt=float(d['Amount (USD)'])
                except (ValueError,TypeError): amt=float('nan')
                if not math.isfinite(amt):
                    invalid_amounts+=1;continue
                if tid in ids:dups+=1
                ids.add(tid)
                historical=d['dt']<cutoff
                seen=history_ids if historical else future_ids
                if tid in seen:continue
                seen.add(tid)
                if historical:
                    cohort.add(cid)
                    aid=str(d['Account ID'])
                    if aid in ownership and ownership[aid]!=cid:
                        conflicts.update((cid,ownership[aid]))
                    ownership[aid]=cid
                s=state.setdefault(cid,{'id':cid,'account_ids':set(),'events':[],'products':set(),'customer_status':'','account_status':'','kyc_status':'','service_reasons':'','segment':'','holdings_unknown':False})
                s['account_ids'].add(str(d['Account ID']))
                if pd.isna(d['products_held']) or not str(d['products_held']).strip():s['holdings_unknown']=True
                s['products'].update(x.strip() for x in str(d['products_held'] or '').split('|') if x.strip() and x.strip()!='nan')
                for k,col in [('customer_status','customer_status'),('account_status','account_status'),('kyc_status','kyc_status'),('service_reasons','service_reasons'),('segment','customer_segment')]:
                    value=str(d[col] or '')
                    if k in ('customer_status','account_status','kyc_status'):
                        allowed={'customer_status':CUSTOMER_STATES,'account_status':ACCOUNT_STATES,'kyc_status':KYC_STATES}[k]
                        value=normalize_state(d[col],allowed) or 'UNKNOWN'
                    if not s[k] or (k in ('customer_status','account_status') and value != 'Active') or (k == 'kyc_status' and value != 'Verified'):
                        s[k]=value
                dt=d['dt']
                if pd.notna(dt) and dt<cutoff and str(d['Type']).upper()!='SERVICE FEE':
                    s['events'].append((dt,amt,str(d['Type'])))
    result=[]
    for s in state.values():
        if s['id'] not in cohort or s['id'] in conflicts:continue
        ev=s['events']; w180=[e for e in ev if e[0]>=cutoff-pd.Timedelta(days=180)];w90=[e for e in ev if e[0]>=cutoff-pd.Timedelta(days=90)]
        recency=(cutoff-max(e[0] for e in ev)).days if ev else None
        deposits=sum(e[2].upper()=='CASH_DEPOSIT' for e in w180)
        products=sorted(s['products']); reason=f'{deposits} observed cash deposits in previous 180 days' if deposits>=2 else ''
        result.append({'customer_id':s['id'],'qualifying_events_180d':len(w180),'events_90d':len(w90),'recency_days':recency,'transaction_volume_180d_usd':round(sum(abs(e[1]) for e in w180),2),'deposit_events_180d':deposits,'product_gap':None if s['holdings_unknown'] else 'Savings Account' not in products,'behavioural_reason':reason,'products_held':None if s['holdings_unknown'] else products,'customer_status':s['customer_status'],'account_status':s['account_status'],'kyc_status':s['kyc_status'],'service_issue':bool(s['service_reasons'] and s['service_reasons'].lower() not in ('nan','none')),'customer_segment':s['segment'],'account_count':len(s['account_ids'])})
    from data_access import FEATURE_COLUMNS
    frame=pd.DataFrame(result,columns=[c for c in FEATURE_COLUMNS if c!='relationship_activity_percentile'])
    frame['relationship_activity_percentile']=frame['transaction_volume_180d_usd'].rank(pct=True).round(4)
    frame.to_csv(out/'customer_features.csv',index=False)
    audit={'cutoff':str(cutoff.date()),'total_transactions':total,'customers':len(frame),'invalid_links':bad_links,'invalid_dates':bad_dates,'duplicate_transaction_ids':dups,'invalid_amounts':invalid_amounts,'invalid_identifiers':invalid_identifiers,'unknown_transaction_types':unknown_types,'ownership_conflict_customers':len(conflicts),'post_cutoff_only_customers_excluded':len(set(state)-cohort),'historical_cohort':'first valid source transaction strictly before cutoff; ownership conflicts excluded','historical_features':['recency_days','qualifying_events_180d','events_90d','transaction_volume_180d_usd','deposit_events_180d'],'snapshot_fields_for_current_gate_only':['products_held','customer_status','account_status','kyc_status'],'note':'All observations dated >= cutoff excluded from historical features; current snapshot fields NOT used for historical model prediction.'}
    (out/'data_audit.json').write_text(json.dumps(audit,indent=2))
    manifest={'schema_version':1,'builder_version':BUILDER_VERSION,'event_definition':EVENT_DEFINITION,'verification':'source_rebuild','feature_sha256':file_hash(out/'customer_features.csv'),'source_sha256':file_hash(path),'cutoff':str(cutoff.date()),'snapshot_as_of':None,'rows':len(frame),'historical_cohort':audit['historical_cohort']}
    manifest_path(out/'customer_features.csv').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(audit,indent=2));return audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--out',default='outputs');p.add_argument('--cutoff',default='2026-07-01');a=p.parse_args();run(a.zip,a.out,a.cutoff)
