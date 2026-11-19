"""Whitelisted historical JSON evidence only. No fitting, inference or deserialization."""
from dataclasses import dataclass
from pathlib import Path
import hashlib,json,math,re
from data_access import manifest_path

ROOT=Path(__file__).resolve().parent
ARTIFACT_PATH=ROOT/'outputs/phase5/evaluation/evaluation.json'
# Reviewed immutable local experiment receipt; a content pin is not a metric fallback.
TRUSTED_ARTIFACT_SHA256='ee516bb25c0e0c467b7d5d8fffdb9a8f4fe50bc76c2fd6d4c399376594a97200'
VERSION='historical-inactivity-v1'
CONFIG={'train_cutoff':'2026-01-01','holdout_cutoff':'2026-07-01','observation_days':180,'target_days':90,'minimum_events':2,'seed':42,'top_k':500}
FEATURES=('recency_days','qualifying_events_180d','events_90d','transaction_volume_180d_usd','deposit_events_180d')
MODEL_NAMES={'recency_only':'Recency-only baseline','logistic_regression':'Logistic regression','histogram_gradient_boosting':'Histogram gradient boosting'}
TARGET='1 iff zero known valid non-SERVICE FEE events in [cutoff,cutoff+90 days); observed inactivity, not churn/account closure'
LIVE_UNAVAILABLE='Unavailable — fitted preprocessing and model artifacts have not been saved or approved for live inference.'

@dataclass(frozen=True)
class HistoricalComparison:
    status:str
    code:str
    message:str
    rows:tuple=()
    training_customers:int=0
    holdout_customers:int=0
    shared_customers:int=0
    training_prevalence:float=0.
    holdout_prevalence:float=0.
    artifact_sha256:str=''
    source_sha256:str=''
    feature_sha256:str=''
    code_sha256:str=''
    version:str=''

class EvidenceInvalid(ValueError):pass

def _finite(v,minimum=0.,maximum=None):
    if type(v) not in (int,float) or not math.isfinite(v) or v<minimum or (maximum is not None and v>maximum):raise EvidenceInvalid('Invalid numeric historical metric.')
    return float(v)

def _hash(value):
    if not isinstance(value,str) or not re.fullmatch('[a-f0-9]{64}',value):raise EvidenceInvalid('Invalid historical fingerprint.')
    return value

def _cohort(value,cutoff,maximum):
    if not isinstance(value,dict) or value.get('cutoff')!=cutoff:raise EvidenceInvalid('Historical cohort cutoff is inconsistent.')
    n=value.get('customers');p=value.get('positives')
    if type(n) is not int or not 1<n<=maximum or type(p) is not int or not 0<p<n:raise EvidenceInvalid('Historical cohort sizes are inconsistent.')
    prevalence=_finite(value.get('prevalence'),0.,1.)
    if not math.isclose(prevalence,p/n,rel_tol=0.,abs_tol=1e-12):raise EvidenceInvalid('Historical prevalence is inconsistent.')
    _hash(value.get('features_sha256'));_hash(value.get('labels_sha256'))
    return n,prevalence

def load_historical_comparison(index,*,artifact_path=ARTIFACT_PATH,feature_path=ROOT/'outputs/customer_features.csv',expected_sha256=TRUSTED_ARTIFACT_SHA256):
    """Paths/pin are server-controlled; overrides exist for isolated tests, never widgets."""
    try:
        path=Path(artifact_path)
        if path.stat().st_size>131072:raise EvidenceInvalid('Historical artifact exceeds the metadata size limit.')
        raw=path.read_bytes();a=json.loads(raw)
        if not isinstance(a,dict):raise EvidenceInvalid('Historical artifact must be an object.')
        if a.get('artifact_version')!=VERSION or a.get('experimental_only') is not True:raise EvidenceInvalid('Unsupported experiment version or approval scope.')
        if a.get('configuration')!=CONFIG or a.get('target_definition')!=TARGET:raise EvidenceInvalid('Historical cutoff/target configuration is inconsistent.')
        if not isinstance(a.get('features'),dict) or set(a['features'])!=set(FEATURES):raise EvidenceInvalid('Historical feature contract is inconsistent.')
        artifact_hash=hashlib.sha256(raw).hexdigest()
        if artifact_hash!=expected_sha256:return HistoricalComparison('Stale','ARTIFACT_HASH_MISMATCH','Historical evidence differs from the reviewed experiment receipt; no metrics are shown.')
        manifest=json.loads(manifest_path(feature_path).read_bytes())
        if not isinstance(manifest,dict):raise EvidenceInvalid('Current source manifest is invalid.')
        feature_hash=_hash(a.get('canonical_feature_sha256'));source_hash=_hash(a.get('source_sha256'));code_hash=_hash(a.get('evaluation_code_sha256'))
        if index.lineage_issues or feature_hash!=index.dataset_hash or manifest.get('feature_sha256')!=index.dataset_hash or manifest.get('source_sha256')!=source_hash or manifest.get('rows')!=len(index.records) or manifest.get('cutoff')!=index.cutoff or index.cutoff!=CONFIG['holdout_cutoff']:
            return HistoricalComparison('Stale','DATASET_ASSOCIATION_MISMATCH','Historical evidence does not match the current validated dataset, source or cutoff; no metrics are shown.')
        if hashlib.sha256((ROOT/'historical_evaluation.py').read_bytes()).hexdigest()!=code_hash:
            return HistoricalComparison('Stale','EVALUATION_CODE_MISMATCH','Evaluation code differs from the historical experiment; no metrics are shown.')
        train_n,train_p=_cohort(a.get('train'),CONFIG['train_cutoff'],index.input_rows);hold_n,hold_p=_cohort(a.get('holdout'),CONFIG['holdout_cutoff'],index.input_rows)
        shared=a.get('shared_customers')
        if type(shared) is not int or not 0<=shared<=min(train_n,hold_n):raise EvidenceInvalid('Shared-customer cohort metadata is invalid.')
        models=a.get('models')
        if not isinstance(models,dict) or set(models)!=set(MODEL_NAMES):raise EvidenceInvalid('Historical model inventory is invalid.')
        rows=[]
        for key,label in MODEL_NAMES.items():
            m=models[key]
            if not isinstance(m,dict) or m.get('cohort_size')!=hold_n or not math.isclose(_finite(m.get('target_prevalence'),0.,1.),hold_p,abs_tol=1e-12):raise EvidenceInvalid('Model cohort association is inconsistent.')
            if type(m.get('requested_k')) is not int or type(m.get('effective_k')) is not int or m['requested_k']!=CONFIG['top_k'] or m['effective_k']!=min(CONFIG['top_k'],hold_n):raise EvidenceInvalid('Precision cohort capacity is inconsistent.')
            auc=_finite(m.get('roc_auc'),0.,1.);ap=_finite(m.get('pr_auc_average_precision'),0.,1.);precision=_finite(m.get('precision_at_k'),0.,1.);lift=_finite(m.get('lift_at_k'));_hash(m.get('score_sha256'))
            if not math.isclose(lift,precision/hold_p,rel_tol=1e-9):raise EvidenceInvalid('Lift/prevalence is inconsistent.')
            rows.append((label,auc,ap,precision,lift))
        return HistoricalComparison('Verified','VERIFIED_HISTORICAL_ONLY','Verified historical experimental evidence; not operational model approval.',tuple(rows),train_n,hold_n,shared,train_p,hold_p,artifact_hash,source_hash,feature_hash,code_hash,VERSION)
    except FileNotFoundError:
        return HistoricalComparison('Unavailable','HISTORICAL_EVIDENCE_MISSING','Trusted historical evidence or its source manifest is unavailable on this host. No fallback metrics are used.')
    except (OSError,ValueError,TypeError,KeyError,OverflowError):
        return HistoricalComparison('Unavailable','HISTORICAL_EVIDENCE_INVALID','Historical evidence is malformed, incomplete or inconsistent. No metrics are shown; inspect the trusted server artifact.')
