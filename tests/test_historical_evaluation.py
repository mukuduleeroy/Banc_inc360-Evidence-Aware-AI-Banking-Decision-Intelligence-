"""Synthetic controlled chronology and known-metric tests; not competition metrics."""
import numpy as np
import pandas as pd
import pytest
from historical_evaluation import cohort,FEATURES,CONFIG,metrics,evaluate,validate_temporal_coverage,VERSION,DEFINITIONS


def events(rows):
 return pd.DataFrame([dict(customer_id=c,account_id='TEST-ACCOUNT',event_id=str(i),timestamp=pd.Timestamp(d),kind=k,amount=a) for i,(c,d,k,a) in enumerate(rows)])

@pytest.fixture
def chronology():
 return events([('A','2025-07-05','CASH_DEPOSIT',10),('A','2025-12-31 23:59','POS_PURCHASE',20),('A','2026-01-01','SERVICE FEE',1),('A','2026-04-01','POS_PURCHASE',99),('B','2025-10-01','CASH_DEPOSIT',5),('B','2025-12-10','CASH_DEPOSIT',5),('B','2026-01-01','POS_PURCHASE',7)])

def test_exact_boundaries_and_fee_exclusion(chronology):
 x,y=cohort(chronology,'2026-01-01');assert x.loc['A','qualifying_events_180d']==2;assert x.loc['A','transaction_volume_180d_usd']==30;assert x.loc['A','recency_days']==0;assert y.to_dict()=={'A':1,'B':0}

def test_lower_observation_boundary_inclusive():
 cut=pd.Timestamp('2026-01-01');start=cut-pd.Timedelta(days=180)
 f=events([('A',str(start),'CASH_DEPOSIT',2),('A',str(start-pd.Timedelta(seconds=1)),'CASH_DEPOSIT',3),('A','2025-12-30','POS_PURCHASE',4)])
 x,_=cohort(f,cut);assert x.loc['A','qualifying_events_180d']==2;assert x.loc['A','transaction_volume_180d_usd']==6

def test_future_mutations_change_labels_only(chronology):
 x,y=cohort(chronology,'2026-01-01');after=events([('A','2026-02-01','CASH_DEPOSIT',999999),('FUTURE','2026-02-02','POS_PURCHASE',5)])
 xx,yy=cohort(pd.concat([chronology,after]),'2026-01-01');pd.testing.assert_frame_equal(x,xx);assert yy.A==0 and y.A==1;assert 'FUTURE' not in xx.index

def test_snapshot_columns_never_predict(chronology):
 x,y=cohort(chronology,'2026-01-01');changed=chronology.assign(kyc_status='Pending',products_held='ALL',current_balance=999999)
 xx,yy=cohort(changed,'2026-01-01');pd.testing.assert_frame_equal(x,xx);pd.testing.assert_series_equal(y,yy);assert tuple(xx.columns)==FEATURES

def test_minimum_two_in_window():
 f=events([('A','2024-01-01','CASH_DEPOSIT',2),('A','2025-12-31','POS_PURCHASE',2),('B','2025-12-30','SERVICE FEE',2)])
 x,y=cohort(f,'2026-01-01');assert x.empty and y.empty

def test_grouped_customers_and_order_invariance(chronology):
 x,y=cohort(chronology,'2026-01-01');xx,yy=cohort(chronology.sample(frac=1,random_state=1),'2026-01-01');pd.testing.assert_frame_equal(x,xx);pd.testing.assert_series_equal(y,yy);assert x.index.is_unique

@pytest.mark.parametrize('cutoff',['bad','2026-01-01 12:00','2026-01-01T00:00Z'])
def test_invalid_cutoff(chronology,cutoff):
 with pytest.raises(ValueError):cohort(chronology,cutoff)

def test_temporal_coverage_rejected(chronology):
 with pytest.raises(ValueError):validate_temporal_coverage(chronology,CONFIG)

def test_training_target_cannot_overlap_holdout():
 f=events([('A','2020-01-01','POS_PURCHASE',1),('A','2030-01-01','POS_PURCHASE',1)])
 with pytest.raises(ValueError):validate_temporal_coverage(f,{**CONFIG,'train_cutoff':'2026-06-01'})

def test_known_metrics():
 m=metrics([1,0,1,0],[.9,.8,.7,.1],['A','B','C','D'],2);assert m['roc_auc']==.75;assert m['pr_auc_average_precision']==pytest.approx(5/6);assert m['precision_at_k']==.5;assert m['lift_at_k']==1

def test_metric_ties_are_deterministic():
 m=metrics([0,1,0,1],[1,1,1,1],['D','A','C','B'],2);assert m['roc_auc']==.5;assert m['precision_at_k']==1;assert m['lift_at_k']==2

@pytest.mark.parametrize('y,s,k',[([0,0],[1,2],1),([0,1],[float('nan'),2],1),([0,1],[1,2],0)])
def test_invalid_metrics_fail_closed(y,s,k):
 with pytest.raises(ValueError):metrics(y,s,['A','B'],k)

def test_model_reproducibility_and_feature_allowlist(monkeypatch):
 monkeypatch.setenv("LOKY_MAX_CPU_COUNT","1")
 rng=np.random.default_rng(4);x=pd.DataFrame(rng.integers(1,100,(120,5)),columns=FEATURES);y=pd.Series((x.recency_days>50).astype(int));keys=[str(i) for i in range(40)]
 a,sa=evaluate(x[:80],y[:80],x[80:],y[80:],keys,k=20);b,sb=evaluate(x[:80],y[:80],x[80:],y[80:],keys,k=20)
 for n in a:
  np.testing.assert_array_equal(sa[n],sb[n]);assert a[n]['roc_auc']==b[n]['roc_auc']
 with pytest.raises(ValueError):evaluate(x.assign(kyc_status=1),y,x,y,list(x.index))

def test_provenance_definitions():
 assert VERSION=='historical-inactivity-v1';assert set(DEFINITIONS)==set(FEATURES);assert CONFIG['train_cutoff']=='2026-01-01';assert CONFIG['holdout_cutoff']=='2026-07-01';assert CONFIG['target_days']==90

def test_versioned_evaluation_artifact_real_source_if_present():
 """If produced, validate recorded provenance; no invented metrics when absent."""
 from pathlib import Path
 import json
 p=Path('outputs/phase5/evaluation/evaluation.json')
 if not p.exists():pytest.skip('Real-source evaluation artifact not available locally')
 from historical_evaluation import digest
 r=json.loads(p.read_text());assert r['artifact_version']==VERSION;assert r['experimental_only'] is True;assert r['evaluation_code_sha256']==digest('historical_evaluation.py');assert len(r['source_sha256'])==64;assert r['canonical_feature_sha256']==digest('outputs/customer_features.csv');assert not any(r['canonical_holdout_predictor_differences'].values());assert set(r['features'])==set(FEATURES)
 for name,model in r['models'].items():
  assert 0<=model['roc_auc']<=1 and 0<=model['pr_auc_average_precision']<=1;assert model['effective_k']==500;assert len(model['score_sha256'])==64;assert model['training_timestamp_utc'].endswith('+00:00')

def test_bootstrap_is_paired_and_reproducible():
 from historical_evaluation import bootstrap
 y=np.array([0,1,0,1,0,1,0,1]);s={'recency_only':np.arange(8,dtype=float),'logistic_regression':np.arange(8,dtype=float),'histogram_gradient_boosting':np.arange(8,dtype=float)};keys=list('ABCDEFGH')
 a=bootstrap(y,s,keys,20,42,k=2);b=bootstrap(y,s,keys,20,42,k=2);assert a==b;assert a['recency_minus_hgb_roc_auc_95pct']==[0.,0.]

@pytest.mark.parametrize('fault',['duplicate','ownership','unknown_type','bad_date'])
def test_source_audit_blocks_invalid_events(tmp_path,fault):
 import zipfile
 from historical_evaluation import audit_source
 f=pd.DataFrame({'Customer ID':['A','B'],'Account ID':['X','Y'],'account_customer_id':['A','B'],'Transaction ID':['T1','T2'],'transaction_date':['01/01/2025','02/01/2025'],'Type':['CASH_DEPOSIT','POS_PURCHASE'],'Amount (USD)':['1','2'],'Date':['01/01/2025','02/01/2025'],'onboarding_date':['01/01/2020']*2,'account_opened_date':['01/01/2020']*2})
 if fault=='duplicate':f.loc[1,'Transaction ID']='T1'
 if fault=='ownership':f.loc[1,'Account ID']='X'
 if fault=='unknown_type':f.loc[1,'Type']='UNKNOWN'
 if fault=='bad_date':f.loc[1,'transaction_date']='not a date'
 path=tmp_path/'synthetic.zip'
 with zipfile.ZipFile(path,'w') as z:z.writestr('synthetic.csv',f.to_csv(index=False))
 with pytest.raises(ValueError,match='audit failed'):audit_source(path)
