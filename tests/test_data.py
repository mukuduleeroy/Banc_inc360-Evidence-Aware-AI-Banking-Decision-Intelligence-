"""Synthetic fixtures verify chronology and reject invalid evidence."""
import csv
import zipfile
import pandas as pd
from build_data import run


def test_historical_cutoff_and_invalid_evidence(tmp_path):
    fields=['Customer ID','Account ID','account_customer_id','Transaction ID','transaction_date','Type','Amount (USD)','dr_cr_indicator','products_held','customer_status','account_status','kyc_status','service_reasons','customer_segment']
    def row(tid,day,**changes):
        d=dict(zip(fields,['SYNTHETIC-1','A1','SYNTHETIC-1',tid,day,'CASH_DEPOSIT','10','CR','Current Account','Active','Active','Verified','','Demo']))
        d.update(changes)
        return d
    rows=[row('1','01/06/2026'),row('2','02/06/2026'),row('2','02/06/2026'),row('3','01/07/2026'),row('4','31/12/2025'),row('5','03/06/2026',account_customer_id='BROKEN'),row('6','invalid')]
    source=tmp_path/'synthetic.csv'
    with source.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    archive=tmp_path/'synthetic.zip'
    with zipfile.ZipFile(archive,'w') as z:z.write(source,'synthetic.csv')
    audit=run(archive,tmp_path/'out')
    features=pd.read_csv(tmp_path/'out/customer_features.csv').iloc[0]
    assert features.qualifying_events_180d == 2
    assert features.recency_days == 29
    assert features.deposit_events_180d == 2
    assert audit['duplicate_transaction_ids'] == 1
    assert audit['invalid_links'] == 1
    assert audit['invalid_dates'] == 1
