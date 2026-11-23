"""Entirely invented transaction CSV scenarios. No competition rows are read."""
from pathlib import Path
import csv,io
from phase9_ingestion import SOURCE_FIELDS

def synthetic_rows():
    rows=[]
    for label,count,kyc in [('SUPPORTED',5,'Verified'),('CAUTION',3,'Verified'),('LOW_HISTORY',1,'Verified'),('RESTRICTED',5,'Pending')]:
        cid='SYNTHETIC-'+label
        for n in range(count):
            row=dict(zip(SOURCE_FIELDS,[cid,'SYNTH-ACCOUNT-'+label,cid,'SYNTH-TX-'+label+'-'+str(n),f'{n+1:02d}/06/2026','CASH_DEPOSIT','100.00','CR','Current Account','Active','Active',kyc,'','Retail']))
            rows.append(row)
    return rows

def csv_bytes(rows=None,fields=SOURCE_FIELDS):
    out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(synthetic_rows() if rows is None else rows);return out.getvalue().encode()

def write_examples(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    examples={'synthetic-valid.csv':csv_bytes(),'synthetic-invalid-date.csv':csv_bytes([{**synthetic_rows()[0],'transaction_date':'not-a-date'}]),'synthetic-unsupported-currency.csv':csv_bytes([{**r,'Currency':'ZAR'} for r in synthetic_rows()],(*SOURCE_FIELDS,'Currency')),'synthetic-missing-fields.csv':b'Customer ID,transaction_date\nSYNTHETIC-ONLY,01/06/2026\n'}
    for name,content in examples.items():
        path=folder/name
        with path.open('xb') as f:f.write(content)
    (folder/'README.md').write_text('All records are independently invented synthetic demonstration data. No competition/customer source is read or copied. Use observation date 2026-07-01. Valid CSV: 14 transactions, four customers; unchanged policy yields one SUPPORTED, one CAUTION, two ABSTAIN. Invalid examples must never activate. USD amounts are already normalized; no FX conversion is performed. Local controlled demonstration only.\n')

if __name__=='__main__':write_examples(Path(__file__).resolve().parent/'outputs/phase9/examples')
