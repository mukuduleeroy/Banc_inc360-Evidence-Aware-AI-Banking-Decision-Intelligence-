"""Offline historical evaluation only. Never imported by the banking decision engine."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, time, zipfile, platform, importlib.metadata
import numpy as np
import pandas as pd

VERSION = 'historical-inactivity-v1'
FEATURES = ('recency_days','qualifying_events_180d','events_90d','transaction_volume_180d_usd','deposit_events_180d')
DEFINITIONS = {
 'recency_days':'Floor days since latest qualifying event strictly before cutoff; earlier than window allowed.',
 'qualifying_events_180d':'Qualifying events in [cutoff-180 days, cutoff).',
 'events_90d':'Qualifying events in [cutoff-90 days, cutoff).',
 'transaction_volume_180d_usd':'Sum absolute finite USD amounts in observation window; not revenue or profit.',
 'deposit_events_180d':'CASH_DEPOSIT events in observation window.',
}
CONFIG = {'train_cutoff':'2026-01-01','holdout_cutoff':'2026-07-01','observation_days':180,'target_days':90,'minimum_events':2,'seed':42,'top_k':500}
KNOWN = {'SERVICE FEE','CASH_DEPOSIT','FOREX_PURCHASE','POS_PURCHASE','ATM_WITHDRAWAL','BILL_PAYMENT'}

def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()

def fingerprint(frame):
 return hashlib.sha256(frame.to_csv(index=True,float_format='%.12g').encode()).hexdigest()

def audit_source(path):
 """Audit required fields before eligibility/label construction; output aggregate metadata only."""
 fields=['Customer ID','Account ID','account_customer_id','Transaction ID','transaction_date','Type','Amount (USD)','Date','onboarding_date','account_opened_date']
 with zipfile.ZipFile(path) as z:
  names=[n for n in z.namelist() if n.lower().endswith('.csv')]
  if len(names)!=1: raise ValueError('Exactly one source CSV required')
  f=pd.read_csv(z.open(names[0]),usecols=fields,dtype=str)
 dt=pd.to_datetime(f.transaction_date,format='mixed',dayfirst=True,errors='coerce')
 amount=pd.to_numeric(f['Amount (USD)'],errors='coerce')
 ids=['Customer ID','Account ID','account_customer_id','Transaction ID']
 missing=sum(int((f[c].isna()|f[c].str.strip().eq('')).sum()) for c in ids)
 ownership=int(f.groupby('Account ID')['Customer ID'].nunique().gt(1).sum())
 diagnostics={'rows':len(f),'customers':int(f['Customer ID'].nunique()),'accounts':int(f['Account ID'].nunique()),'invalid_identifiers':missing,'invalid_dates':int(dt.isna().sum()),'invalid_amounts':int((~np.isfinite(amount)).sum()),'duplicate_transaction_ids':int(f['Transaction ID'].duplicated().sum()),'ownership_mismatches':int(f['Customer ID'].ne(f.account_customer_id).sum()),'ownership_conflict_accounts':ownership,'unknown_types':int((~f.Type.isin(KNOWN)).sum()),'event_start':str(dt.min()),'event_end':str(dt.max()),'transaction_types':{str(k):int(v) for k,v in f.Type.value_counts().items()},'transactions_per_customer':{str(k):int(v) for k,v in f.groupby('Customer ID').size().value_counts().sort_index().items()},'source_sha256':digest(path),'timestamps':{'historical':'transaction_date, day-first, timezone-naive; event time not ingestion time','unknown':'source timezone, ingestion availability and completeness attestation','snapshots':'KYC/status/holdings/income/balances/last-transaction are not historical predictors'}}
 for c in ['Date','onboarding_date','account_opened_date']:
  parsed=pd.to_datetime(f[c],format='mixed',dayfirst=True,errors='coerce')
  diagnostics[c]={'invalid':int(parsed.isna().sum()),'after_transaction':int(parsed.gt(dt).sum())}
 errors=[k for k in ('invalid_identifiers','invalid_dates','invalid_amounts','duplicate_transaction_ids','ownership_mismatches','ownership_conflict_accounts','unknown_types') if diagnostics[k]]
 diagnostics['prerequisites_verified']=not errors
 if errors: raise ValueError('Historical source audit failed: '+','.join(errors))
 events=pd.DataFrame({'customer_id':f['Customer ID'],'account_id':f['Account ID'],'event_id':f['Transaction ID'],'timestamp':dt,'kind':f.Type,'amount':amount})
 return events,diagnostics

def cohort(events,cutoff,observation_days=180,target_days=90,minimum_events=2):
 """Future rows affect only labels. Customer eligibility uses pre-cutoff history only."""
 cutoff=pd.Timestamp(cutoff)
 if pd.isna(cutoff) or cutoff.tz is not None or cutoff!=cutoff.normalize():raise ValueError('Midnight naive cutoff required')
 q=events.loc[events.kind.ne('SERVICE FEE')]
 history=q.loc[q.timestamp.lt(cutoff)]
 window=history.loc[history.timestamp.ge(cutoff-pd.Timedelta(days=observation_days))]
 g=window.groupby('customer_id',sort=True)
 frame=pd.DataFrame({'qualifying_events_180d':g.size(),'events_90d':window.loc[window.timestamp.ge(cutoff-pd.Timedelta(days=90))].groupby('customer_id').size(),'transaction_volume_180d_usd':window.assign(volume=window.amount.abs()).groupby('customer_id').volume.sum(),'deposit_events_180d':window.loc[window.kind.eq('CASH_DEPOSIT')].groupby('customer_id').size()}).fillna(0)
 last=history.groupby('customer_id').timestamp.max(); frame['recency_days']=(cutoff-last).dt.days
 frame=frame.loc[frame.qualifying_events_180d.ge(minimum_events),list(FEATURES)].sort_index()
 future=q.loc[q.timestamp.ge(cutoff)&q.timestamp.lt(cutoff+pd.Timedelta(days=target_days))].groupby('customer_id').size()
 target=(future.reindex(frame.index,fill_value=0)==0).astype(int).rename('inactive_next_90d')
 return frame,target

def validate_temporal_coverage(events,config):
 end=events.timestamp.max()
 for name in ('train_cutoff','holdout_cutoff'):
  cutoff=pd.Timestamp(config[name])
  if events.timestamp.min()>cutoff-pd.Timedelta(days=config['observation_days']) or end<cutoff+pd.Timedelta(days=config['target_days']):raise ValueError('Insufficient source coverage for '+name)
 if pd.Timestamp(config['train_cutoff'])+pd.Timedelta(days=config['target_days'])>pd.Timestamp(config['holdout_cutoff']):raise ValueError('Training target overlaps holdout observation date')

def metrics(y,score,tie_keys,k=500):
 """PR-AUC is average precision (step integral); also expose trapezoidal area."""
 from sklearn.metrics import roc_auc_score,average_precision_score,precision_recall_curve,auc
 y=np.asarray(y,dtype=int);score=np.asarray(score,dtype=float)
 if y.ndim!=1 or len(y)!=len(score) or len(tie_keys)!=len(y) or not np.isfinite(score).all() or set(np.unique(y))!={0,1} or k<1:raise ValueError('Finite aligned binary evaluation with both classes required')
 order=np.lexsort((np.asarray(tie_keys,dtype=str),-score)); n=min(k,len(y));precision=float(y[order[:n]].mean()); prevalence=float(y.mean());p,r,_=precision_recall_curve(y,score)
 return {'roc_auc':float(roc_auc_score(y,score)),'pr_auc_average_precision':float(average_precision_score(y,score)),'pr_auc_trapezoidal':float(auc(r,p)),'precision_at_k':precision,'lift_at_k':precision/prevalence,'requested_k':k,'effective_k':n,'cohort_size':len(y),'target_prevalence':prevalence}

def evaluate(train_x,train_y,test_x,test_y,tie_keys,seed=42,k=500):
 from sklearn.preprocessing import StandardScaler
 from sklearn.pipeline import make_pipeline
 from sklearn.linear_model import LogisticRegression
 from sklearn.ensemble import HistGradientBoostingClassifier
 from threadpoolctl import threadpool_limits
 if tuple(train_x.columns)!=FEATURES or tuple(test_x.columns)!=FEATURES: raise ValueError('Only approved historical features allowed')
 if set(np.unique(train_y))!={0,1}:raise ValueError('Training requires both target classes')
 if not np.isfinite(train_x.to_numpy()).all() or not np.isfinite(test_x.to_numpy()).all() or (train_x.to_numpy()<0).any() or (test_x.to_numpy()<0).any():raise ValueError('Invalid historical predictors')
 models={'recency_only':None,'logistic_regression':make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=1000,solver='lbfgs',random_state=seed)),'histogram_gradient_boosting':HistGradientBoostingClassifier(max_iter=150,learning_rate=.08,max_leaf_nodes=15,min_samples_leaf=30,l2_regularization=1.0,early_stopping=False,random_state=seed)}
 results={};scores={}
 with threadpool_limits(limits=1):
  for name,model in models.items():
   start=time.perf_counter();training_utc=datetime.now(timezone.utc).isoformat()
   if model is None:fit_time=0.;score=test_x.recency_days.to_numpy()
   else:
    model.fit(np.log1p(train_x),train_y);fit_time=time.perf_counter()-start;score=model.predict_proba(np.log1p(test_x))[:,1]
   result=metrics(test_y,score,tie_keys,k);result.update(training_timestamp_utc=training_utc,score_sha256=hashlib.sha256(np.asarray(score,dtype='<f8').tobytes()).hexdigest(),training_seconds=fit_time,total_evaluation_seconds=time.perf_counter()-start,hyperparameters={} if model is None else ({'preprocessing':'log1p all five features; StandardScaler fitted only on training','C':1.0,'max_iter':1000,'solver':'lbfgs','class_weight':None,'random_state':seed} if name=='logistic_regression' else model.get_params()))
   results[name]=result;scores[name]=np.asarray(score)
 return results,scores

def bootstrap(y,scores,tie_keys,repeats=200,seed=42,k=500):
 """Paired customer bootstrap of frozen predictions; does not cover source/model selection uncertainty."""
 rng=np.random.default_rng(seed);y=np.asarray(y);keys=np.asarray(tie_keys);rows={n:[] for n in scores};diff=[]
 for _ in range(repeats):
  ix=rng.integers(0,len(y),len(y))
  if len(np.unique(y[ix]))<2:continue
  values={n:metrics(y[ix],s[ix],keys[ix],k) for n,s in scores.items()}
  for n,v in values.items():rows[n].append([v['roc_auc'],v['pr_auc_average_precision']])
  diff.append(values['recency_only']['roc_auc']-values['histogram_gradient_boosting']['roc_auc'])
 return {'method':'paired customer percentile bootstrap; fixed fitted models; conditional on one supplied extract','repeats':repeats,'seed':seed,'models':{n:{m:list(np.quantile(np.asarray(v)[:,i],[.025,.975])) for i,m in enumerate(['roc_auc','pr_auc_average_precision'])} for n,v in rows.items()},'recency_minus_hgb_roc_auc_95pct':list(np.quantile(diff,[.025,.975]))} if diff else {'repeats':0}

def run(source,out,audit_only=False,bootstrap_repeats=200):
 out=Path(out)
 if out.exists():raise FileExistsError('Choose a new evaluation directory; never overwrite prior evidence')
 out.mkdir(parents=True);started=time.perf_counter();events,audit=audit_source(source);validate_temporal_coverage(events,CONFIG);(out/'historical_data_audit.json').write_text(json.dumps(audit,indent=2))
 if audit_only:return audit
 from data_access import alias_key,presentation_alias
 train_x,train_y=cohort(events,CONFIG['train_cutoff']);test_x,test_y=cohort(events,CONFIG['holdout_cutoff']);key=alias_key();aliases=[presentation_alias(c,key) for c in test_x.index]
 if len(set(aliases))!=len(aliases):raise ValueError('Alias collision')
 # Reconcile the independently reconstructed July predictors to the existing artifact.
 canonical=pd.read_csv('outputs/customer_features.csv',dtype={'customer_id':str}).set_index('customer_id')
 comparisons={c:int((canonical.loc[test_x.index,c].round(2 if c=='transaction_volume_180d_usd' else 8)!=test_x[c].round(2 if c=='transaction_volume_180d_usd' else 8)).sum()) for c in FEATURES}
 if any(comparisons.values()):raise ValueError('Historical reconstruction differs from canonical predictors')
 results,scores=evaluate(train_x,train_y,test_x,test_y,aliases,CONFIG['seed'],CONFIG['top_k'])
 uncertainty=bootstrap(test_y,scores,aliases,bootstrap_repeats,CONFIG['seed'],CONFIG['top_k'])
 versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','scikit-learn','scipy','threadpoolctl','joblib']}
 report={'artifact_version':VERSION,'experimental_only':True,'approved_decision_method':'unchanged six-gate deterministic rules; no experimental model deployed','training_timestamp_utc':datetime.now(timezone.utc).isoformat(),'source_sha256':audit['source_sha256'],'evaluation_code_sha256':digest(__file__),'canonical_feature_sha256':digest('outputs/customer_features.csv'),'configuration':CONFIG,'target_definition':'1 iff zero known valid non-SERVICE FEE events in [cutoff,cutoff+90 days); observed inactivity, not churn/account closure','eligibility':'at least two qualifying events in [cutoff-180 days,cutoff); one row/customer/cutoff','features':DEFINITIONS,'feature_preprocessing':'log1p five historical features for fitted models; recency baseline untransformed higher recency means higher inactivity score','excluded_predictors':['current KYC','customer/account status','product holdings','account count','segment','service issue','balances','income','last transaction snapshot'],'train':{'cutoff':CONFIG['train_cutoff'],'customers':len(train_y),'positives':int(train_y.sum()),'prevalence':float(train_y.mean()),'features_sha256':fingerprint(train_x),'labels_sha256':fingerprint(train_y.to_frame())},'holdout':{'cutoff':CONFIG['holdout_cutoff'],'customers':len(test_y),'positives':int(test_y.sum()),'prevalence':float(test_y.mean()),'features_sha256':fingerprint(test_x),'labels_sha256':fingerprint(test_y.to_frame())},'canonical_holdout_predictor_differences':comparisons,'shared_customers':len(set(train_x.index)&set(test_x.index)),'split':'chronological repeated-customer evaluation; not unseen-customer generalization; no random row split','tie_break':'score descending, stable keyed presentation alias ascending','alias_key_sha256':hashlib.sha256(key).hexdigest(),'models':results,'uncertainty':uncertainty,'dependencies':versions,'python':platform.python_version(),'reproduction_command':'.venv/bin/python scripts/evaluate_history.py --zip /Users/user/Downloads/2026_BancABC_Hackathon_Dataset.zip --out outputs/phase5/evaluation-new','total_runtime_seconds':time.perf_counter()-started,'limitations':['synthetic-looking fixed 20/21 transaction counts','single chronological holdout; no production external validity','assumed complete extraction through future window; ingestion dates unavailable','bootstrap excludes refitting, tuning and source uncertainty','current snapshot effective dates and source timezone unknown','PR-AUC definition may differ from original reported paper']}
 (out/'evaluation.json').write_text(json.dumps(report,indent=2));pd.DataFrame([dict(model=n,**{k:v for k,v in m.items() if k!='hyperparameters'}) for n,m in results.items()]).to_csv(out/'metrics.csv',index=False)
 print(json.dumps(report,indent=2));return report
