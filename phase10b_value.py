"""Read-only explanation of existing activity percentile; no reranking/economic estimates."""
from pathlib import Path
import hashlib,json,re
import pandas as pd
from analytics import portfolio_frame,activity_band,numeric
from segment_context import banking_segment_frame,filter_banking_segment
from data_access import load_index,FEATURE_COLUMNS
from acceptance_checks import decision_fingerprint

ROOT=Path(__file__).resolve().parent
HIGH='High Relationship Activity — Potential Value Review'
OTHER='Outside high-activity review band'
UNAVAILABLE='Unavailable — insufficient activity evidence'
LIMITATION='This classification identifies customers with higher historical transaction activity. It does not establish confirmed profitability, customer lifetime value or future revenue.'
HIGH_BAND='Higher activity (80th+)'


def observation_window(cutoff):
    try:
        if not isinstance(cutoff,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',cutoff):raise ValueError()
        date=pd.Timestamp(cutoff)
        if pd.isna(date) or date.tz is not None:raise ValueError()
        return {'start_inclusive':str((date-pd.Timedelta(days=180)).date()),'end_exclusive':cutoff,'days':180}
    except (ValueError,TypeError,OverflowError):return None


def _classify(percentile,volume,window_available):
    p=numeric(percentile,percentile=True);v=numeric(volume)
    if p is None or v is None or not window_available:return UNAVAILABLE
    return HIGH if activity_band(p)==HIGH_BAND else OTHER


def classify_activity(percentile,volume,cutoff):
    return _classify(percentile,volume,observation_window(cutoff) is not None)


def value_frame(index):
    """Detached alias-safe frame; original ranks/bands/decisions/priorities preserved."""
    if index.lineage_issues:raise ValueError('Verified source lineage is required for the activity-value proxy.')
    original=portfolio_frame(index);context=banking_segment_frame(index)
    frame=filter_banking_segment(original,context,'All')
    frame['banking_segment']=frame.customer.map(context.set_index('customer').banking_segment)
    valid_window=observation_window(index.cutoff) is not None
    frame['value_proxy_classification']=[_classify(p,v,valid_window) for p,v in zip(frame.relationship_activity_percentile,frame.transaction_volume_180d_usd)]
    return frame


def value_reconciliation(index):
    frame=value_frame(index);counts={name:int(frame.value_proxy_classification.eq(name).sum()) for name in (HIGH,OTHER,UNAVAILABLE)}
    higher=int(frame.activity_band.eq(HIGH_BAND).sum())
    valid=all((c!=HIGH or b==HIGH_BAND) for c,b in zip(frame.value_proxy_classification,frame.activity_band)) and sum(counts.values())==len(index.records) and frame.customer.is_unique
    return {'population':'original source-derived customer population only','customers':len(index.records),'global_ranking_denominator':len(index.records),'existing_higher_activity_band':higher,'classifications':counts,'unavailable_evidence':counts[UNAVAILABLE],'reconciled':bool(valid),'observation_window':observation_window(index.cutoff),'dataset_sha256':index.dataset_hash,'policy_sha256':index.policy_hash,'limitation':LIMITATION}


def selected_value_explanation(index,alias):
    frame=value_frame(index);row=frame.loc[frame.customer.eq(alias)]
    if len(row)!=1:raise ValueError('Selected customer alias is unavailable or ambiguous.')
    r=row.iloc[0];p=numeric(r.relationship_activity_percentile,percentile=True);v=numeric(r.transaction_volume_180d_usd)
    why=('Existing global activity percentile '+format(p,'.4f')+' is in the accepted Higher activity (80th+) band, meeting the unchanged >=80th percentile boundary.' if r.value_proxy_classification==HIGH else 'Existing activity evidence is below the unchanged Higher activity band.' if r.value_proxy_classification==OTHER else 'Percentile, observed USD activity or observation date is missing/invalid; no positive classification is made.')
    return {'customer':alias,'banking_segment':r.banking_segment,'original_activity_band':r.activity_band,'global_activity_percentile':p,'historical_usd_activity':v,'known_product_breadth':numeric(r.product_breadth,integer=True),'recorded_accounts':numeric(r.account_count,integer=True),'classification':r.value_proxy_classification,'explanation':why,'metric':'Existing global average-tie percentile of absolute qualifying 180-day USD transaction turnover; rounded to four decimals by the original builder.','ranking_population':len(index.records),'threshold':'Existing Higher activity band: global percentile >= 0.8. No segment-relative reranking.','observation_window':observation_window(index.cutoff),'source_segment_effective_date':None,'snapshot_effective_date':None,'dataset_sha256':index.dataset_hash,'policy_sha256':index.policy_hash,'limitation':LIMITATION,'operational_permission':False}


def load_accepted_index():
    """Canonical read-only load with existing key, never alias-key creation or data fallback."""
    path=ROOT/'outputs/customer_features.csv';manifest=path.with_suffix('.manifest.json');key=ROOT/'outputs/.presentation_alias_key'
    reference=json.loads((ROOT/'tests/fixtures/reference_local_baseline.json').read_bytes())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=reference['feature_sha256'] or hashlib.sha256(manifest.read_bytes()).hexdigest()!=reference['manifest_sha256']:raise ValueError('Accepted source fingerprints do not match. No proxy fallback is permitted.')
    secret=key.read_bytes()
    if len(secret)!=32:raise ValueError('Existing private alias configuration is unavailable.')
    index=load_index(path,key=secret)
    if index.lineage_issues or index.exclusions or index.policy_hash!=reference['policy_sha256'] or len(index.records)!=reference['customers'] or index.counts!=reference['counts'] or decision_fingerprint(index)!=reference['decision_fingerprint'] or len(FEATURE_COLUMNS)!=16:raise ValueError('Accepted baseline integrity cannot be verified. No source-derived classification is shown.')
    return index
