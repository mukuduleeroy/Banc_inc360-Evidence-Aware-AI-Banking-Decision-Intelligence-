"""Controlled synthetic chronology fixtures; never replace competition data."""
import csv
import zipfile
import pandas as pd
import pytest
from build_data import run
from data_access import FEATURE_COLUMNS

FIELDS=['Customer ID','Account ID','account_customer_id','Transaction ID','transaction_date','Type','Amount (USD)','dr_cr_indicator','products_held','customer_status','account_status','kyc_status','service_reasons','customer_segment']
def row(cid,tid,day,amount='100',**changes):
    value=dict(zip(FIELDS,[cid,'A-'+cid,cid,tid,day,'CASH_DEPOSIT',amount,'CR','Current Account','Active','Active','Verified','','SYNTHETIC']))
    value.update(changes);return value

def build(tmp_path,rows,name,cutoff='2026-07-01'):
    folder=tmp_path/name;folder.mkdir();source=folder/'synthetic.csv'
    with source.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    archive=folder/'synthetic.zip'
    with zipfile.ZipFile(archive,'w') as z:z.write(source,'synthetic.csv')
    audit=run(archive,folder/'out',cutoff)
    return pd.read_csv(folder/'out/customer_features.csv').set_index('customer_id'),audit

def test_future_only_customers_cannot_change_historical_percentile(tmp_path):
    rows=[row('SYNTHETIC-A','1','01/06/2026'),row('SYNTHETIC-B','2','01/06/2026','50')]
    old,_=build(tmp_path,rows,'old')
    new,audit=build(tmp_path,[row('SYNTHETIC-FUTURE','3','02/07/2026')]+rows,'new')
    pd.testing.assert_frame_equal(old,new)
    assert audit['post_cutoff_only_customers_excluded']==1

def test_snapshots_and_future_rows_do_not_change_history(tmp_path):
    rows=[row('SYNTHETIC-A','1','01/06/2026')]
    before,_=build(tmp_path,rows,'before')
    # Same ID first appears on a future row: must not suppress historical evidence.
    future=row('SYNTHETIC-A','1','02/07/2026','999',customer_status='Restricted',account_status='Frozen',kyc_status='Pending',products_held='Savings Account')
    after,_=build(tmp_path,[future]+rows,'after')
    historical=['qualifying_events_180d','events_90d','recency_days','transaction_volume_180d_usd','deposit_events_180d','relationship_activity_percentile']
    pd.testing.assert_frame_equal(before[historical],after[historical])
    assert after.iloc[0].account_status=='Frozen'

def test_training_and_holdout_observations_are_separate(tmp_path):
    rows=[row('SYNTHETIC-A','1','01/12/2025'),row('SYNTHETIC-B','2','01/06/2026')]
    train,_=build(tmp_path,rows,'train','2026-01-01');holdout,_=build(tmp_path,rows,'holdout')
    assert list(train.index)==['SYNTHETIC-A']
    assert set(holdout.index)=={'SYNTHETIC-A','SYNTHETIC-B'}
    assert train.loc['SYNTHETIC-A','qualifying_events_180d']==1
    assert holdout.loc['SYNTHETIC-A','qualifying_events_180d']==0

def test_exact_window_boundaries_and_service_fee_definition(tmp_path):
    rows=[row('SYNTHETIC-A','1','02/01/2026'),row('SYNTHETIC-A','2','01/01/2026'),row('SYNTHETIC-A','3','02/04/2026'),row('SYNTHETIC-A','4','01/07/2026'),row('SYNTHETIC-A','5','01/06/2026',Type='SERVICE FEE')]
    frame,_=build(tmp_path,rows,'boundaries')
    assert frame.iloc[0].qualifying_events_180d==2
    assert frame.iloc[0].events_90d==1
    assert set(frame.reset_index().columns)==set(FEATURE_COLUMNS)

def test_invalid_first_duplicate_does_not_suppress_valid_event(tmp_path):
    rows=[row('SYNTHETIC-A','1','bad-date'),row('SYNTHETIC-A','1','01/06/2026')]
    frame,audit=build(tmp_path,rows,'duplicates')
    assert frame.iloc[0].qualifying_events_180d==1 and audit['invalid_dates']==1

@pytest.mark.parametrize('changes',[{'Type':'UNKNOWN'},{'Amount (USD)':'bad'},{'Amount (USD)':'inf'}])
def test_invalid_events_do_not_count_as_history(tmp_path,changes):
    rows=[row('SYNTHETIC-A','1','01/06/2026'),row('SYNTHETIC-A','2','02/06/2026',**changes)]
    frame,audit=build(tmp_path,rows,'invalid')
    assert frame.iloc[0].qualifying_events_180d==1
    assert audit['invalid_amounts']+audit['unknown_transaction_types']==1

def test_conflicting_historical_account_ownership_excluded(tmp_path):
    rows=[row('SYNTHETIC-A','1','01/06/2026'),row('SYNTHETIC-B','2','02/06/2026',**{'Account ID':'A-SYNTHETIC-A'})]
    frame,audit=build(tmp_path,rows,'ownership')
    assert frame.empty and audit['ownership_conflict_customers']==2

def test_existing_output_cannot_be_silently_replaced(tmp_path):
    build(tmp_path,[row('SYNTHETIC-A','1','01/06/2026')],'existing')
    with pytest.raises(FileExistsError):run(tmp_path/'existing/synthetic.zip',tmp_path/'existing/out')

def test_unknown_later_account_snapshot_cannot_leave_active_default(tmp_path):
    rows=[row('SYNTHETIC-A','1','01/06/2026'),row('SYNTHETIC-A','2','02/07/2026',account_status='not known')]
    frame,_=build(tmp_path,rows,'snapshot-invalid')
    assert frame.iloc[0].account_status=='UNKNOWN'

@pytest.mark.parametrize('cutoff',['NaT','2026-07-01T00:00:00Z','2026-07-01T12:00:00'])
def test_invalid_or_timezone_ambiguous_cutoff_rejected(tmp_path,cutoff):
    with pytest.raises(ValueError):build(tmp_path,[row('SYNTHETIC-A','1','01/06/2026')],'cutoff',cutoff)

def test_malformed_identifiers_excluded_before_historical_ranking(tmp_path):
    rows=[row('SYNTHETIC-A','1','01/06/2026'),row('SYNTHETIC-B','2','01/06/2026','50')]
    before,_=build(tmp_path,rows,'valid-ids')
    after,audit=build(tmp_path,rows+[row('BAD ID','3','01/06/2026','99999')],'invalid-ids')
    pd.testing.assert_frame_equal(before,after)
    assert audit['invalid_identifiers']==1

def test_missing_cutoff_does_not_default_to_present_time(tmp_path):
    with pytest.raises(ValueError,match='required'):build(tmp_path,[row('SYNTHETIC-A','1','01/06/2026')],'missing-cutoff',None)
