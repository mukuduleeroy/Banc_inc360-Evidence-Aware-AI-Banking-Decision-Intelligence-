"""Aggregate actual validated local metrics. No customer records are exported."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from data_access import load_index
from analytics import metrics,portfolio_frame,distribution,reason_distribution
path=ROOT/'outputs/customer_features.csv';before=hashlib.sha256(path.read_bytes()).hexdigest();index=load_index(path);frame=portfolio_frame(index)
result={'dataset_sha256':index.dataset_hash,'policy_sha256':index.policy_hash,'cutoff':index.cutoff,'metrics':metrics(index),'distributions':{column:dict(zip(table.iloc[:,0].astype(str),table.Customers.astype(int))) for column in ['rating','frequency_band','recency_band','activity_band','savings_gap','product_breadth','kyc_status','account_status'] for table in [distribution(frame,column)]},'abstention_reason_counts':reason_distribution(index).to_dict('records'),'canonical_unchanged':before==hashlib.sha256(path.read_bytes()).hexdigest()}
(ROOT/'outputs/phase3/metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
