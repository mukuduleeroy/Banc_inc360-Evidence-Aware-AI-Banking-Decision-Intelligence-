"""Reproducible point-in-time feature extraction. Run with --zip path/to/dataset.zip."""
import argparse,zipfile,json
from pathlib import Path
import pandas as pd

def run(path,out='outputs',cutoff='2026-07-01'):
    path=Path(path).expanduser()
    if not path.is_file():
        raise FileNotFoundError('Dataset ZIP not found. Supply an existing local file using --zip.')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fields=['Customer ID','Account ID','account_customer_id','Transaction ID','transaction_date','Type','Amount (USD)','dr_cr_indicator','products_held','customer_status','account_status','kyc_status','service_reasons','customer_segment']
    cutoff=pd.Timestamp(cutoff)
    state={}; total=0; bad_links=0;bad_dates=0;dups=0;ids=set()
    with zipfile.ZipFile(path) as z:
        name=next(n for n in z.namelist() if n.lower().endswith('.csv'))
        for chunk in pd.read_csv(z.open(name),usecols=fields,chunksize=35000,dtype=str,low_memory=False):
            total+=len(chunk)
            chunk['dt']=pd.to_datetime(chunk['transaction_date'],dayfirst=True,errors='coerce')
            bad_dates+=int(chunk['dt'].isna().sum())
            bad_links+=int((chunk['Customer ID']!=chunk['account_customer_id']).sum())
            for row in chunk.itertuples(index=False,name=None):
                d=dict(zip(chunk.columns,row)); cid=str(d['Customer ID']); tid=str(d['Transaction ID'])
                duplicate = tid in ids
                if duplicate: dups+=1
                ids.add(tid)
                if duplicate or pd.isna(d['Customer ID']) or pd.isna(d['Account ID']) or pd.isna(d['Transaction ID']) or d['Customer ID'] != d['account_customer_id'] or pd.isna(d['dt']):
                    continue
                s=state.setdefault(cid,{'id':cid,'account_ids':set(),'events':[],'products':set(),'customer_status':'','account_status':'','kyc_status':'','service_reasons':'','segment':''})
                s['account_ids'].add(str(d['Account ID']))
                s['products'].update(x.strip() for x in str(d['products_held'] or '').split('|') if x.strip() and x.strip()!='nan')
                for k,col in [('customer_status','customer_status'),('account_status','account_status'),('kyc_status','kyc_status'),('service_reasons','service_reasons'),('segment','customer_segment')]:
                    value=str(d[col] or '')
                    if not s[k] or (k == 'customer_status' and value != 'Active') or (k == 'account_status' and value in ('Frozen','Dormant')) or (k == 'kyc_status' and value != 'Verified'):
                        s[k]=value
                dt=d['dt']
                if pd.notna(dt) and dt<cutoff and str(d['Type']).upper()!='SERVICE FEE':
                    try: amt=float(d['Amount (USD)'])
                    except (ValueError,TypeError):amt=0.
                    s['events'].append((dt,amt,str(d['Type'])))
    result=[]
    for s in state.values():
        ev=s['events']; w180=[e for e in ev if e[0]>=cutoff-pd.Timedelta(days=180)];w90=[e for e in ev if e[0]>=cutoff-pd.Timedelta(days=90)]
        recency=(cutoff-max(e[0] for e in ev)).days if ev else None
        deposits=sum(e[2].upper()=='CASH_DEPOSIT' for e in w180)
        products=sorted(s['products']); reason=f'{deposits} observed cash deposits in previous 180 days' if deposits>=2 else ''
        result.append({'customer_id':s['id'],'qualifying_events_180d':len(w180),'events_90d':len(w90),'recency_days':recency,'transaction_volume_180d_usd':round(sum(abs(e[1]) for e in w180),2),'deposit_events_180d':deposits,'product_gap':'Savings Account' not in products,'behavioural_reason':reason,'products_held':products,'customer_status':s['customer_status'],'account_status':s['account_status'],'kyc_status':s['kyc_status'],'service_issue':bool(s['service_reasons'] and s['service_reasons'].lower() not in ('nan','none')),'customer_segment':s['segment'],'account_count':len(s['account_ids'])})
    frame=pd.DataFrame(result)
    frame['relationship_activity_percentile']=frame['transaction_volume_180d_usd'].rank(pct=True).round(4)
    frame.to_csv(out/'customer_features.csv',index=False)
    audit={'cutoff':str(cutoff.date()),'total_transactions':total,'customers':len(frame),'invalid_links':bad_links,'invalid_dates':bad_dates,'duplicate_transaction_ids':dups,'historical_features':['recency_days','qualifying_events_180d','events_90d','transaction_volume_180d_usd','deposit_events_180d'],'snapshot_fields_for_current_gate_only':['products_held','customer_status','account_status','kyc_status'],'note':'All observations dated >= cutoff excluded from historical features; current snapshot fields NOT used for historical model prediction.'}
    (out/'data_audit.json').write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit,indent=2));return audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--out',default='outputs');p.add_argument('--cutoff',default='2026-07-01');a=p.parse_args();run(a.zip,a.out,a.cutoff)
