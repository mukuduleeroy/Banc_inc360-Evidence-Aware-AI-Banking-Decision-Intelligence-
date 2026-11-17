"""Validated feature imports, private identity mapping and complete cached decision indexes."""
from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path
import hashlib
import hmac
import io
import json
import os
import secrets
import re
import pandas as pd
from engine import Case, evaluate, POLICY_VERSION
from evidence import identifier, number, holdings, issue

FEATURE_COLUMNS = ('customer_id', 'qualifying_events_180d', 'events_90d', 'recency_days', 'transaction_volume_180d_usd', 'deposit_events_180d', 'product_gap', 'behavioural_reason', 'products_held', 'customer_status', 'account_status', 'kyc_status', 'service_issue', 'customer_segment', 'account_count', 'relationship_activity_percentile')
BUILDER_VERSION = 'phase2-cohort-1'
EVENT_DEFINITION = 'known-nonfee-finite-amount-v1'

class FeatureValidationError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def boolean(value):
    if type(value) is bool:
        return value
    if isinstance(value, str) and value.casefold() in {'true', 'false'}:
        return value.casefold() == 'true'
    return None

def row_case(values, extra_issues=()):
    """Both passports and queue use this adapter; no missing-count imputation."""
    errors = list(extra_issues)
    values = dict(values)
    # CSV numeric tokens are unambiguous serialization, not missing-value imputation.
    for name in ('qualifying_events_180d','recency_days','relationship_activity_percentile','events_90d','deposit_events_180d','account_count','transaction_volume_180d_usd'):
        raw = values.get(name)
        if isinstance(raw, str) and re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?', raw):
            try: values[name] = float(raw)
            except (ValueError, OverflowError): pass
    for key in ('events_90d', 'deposit_events_180d', 'account_count', 'transaction_volume_180d_usd'):
        if number(values.get(key), integer=key != 'transaction_volume_180d_usd') is None:
            errors.append(issue('G1', 'INVALID_' + key.upper(), 'Required feature ' + key + ' is unavailable or outside its domain.'))
    n = number(values.get('qualifying_events_180d'), integer=True)
    for key in ('events_90d', 'deposit_events_180d'):
        count = number(values.get(key), integer=True)
        if n is not None and count is not None and count > n:
            errors.append(issue('G1', 'INCONSISTENT_EVENT_COUNTS', 'Subwindow/deposit count exceeds total qualifying history.'))
    service = boolean(values.get('service_issue'))
    products = holdings(values.get('products_held'))
    gap = boolean(values.get('product_gap'))
    if gap is None or (products is not None and gap != ('savings account' not in {p.casefold() for p in products})):
        errors.append(issue('G5', 'INCONSISTENT_PRODUCT_GAP', 'Stored product gap is missing or conflicts with ownership evidence.'))
    reason = values.get('behavioural_reason')
    if reason is None or (not isinstance(reason, str) and pd.isna(reason)):
        reason = ''
    return Case(customer_id=values.get('customer_id'), qualifying_events_180d=values.get('qualifying_events_180d'), recency_days=values.get('recency_days'), relationship_activity_percentile=values.get('relationship_activity_percentile'), service_issue=service, products_held=values.get('products_held'), behavioural_reason=reason, customer_status=values.get('customer_status'), account_status=values.get('account_status'), kyc_status=values.get('kyc_status'), validation_issues=tuple(errors))

def presentation_alias(customer_id, key):
    return 'C-' + hmac.new(key, customer_id.encode(), hashlib.sha256).hexdigest()[:24].upper()

def alias_key(path=None):
    """Stable local secret, never committed or displayed. Existing mapping survives reruns."""
    path = Path(path) if path else Path(__file__).parent / 'outputs/.presentation_alias_key'
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(fd, 'wb') as f:
            f.write(secrets.token_bytes(32))
    key = path.read_bytes()
    if len(key) != 32:
        raise FeatureValidationError('INVALID_ALIAS_KEY', 'Local presentation identity configuration is invalid.')
    return key

def policy_fingerprint(version=POLICY_VERSION):
    digest = hashlib.sha256(version.encode())
    for name in ('engine.py', 'evidence.py', 'data_access.py'):
        digest.update(Path(__file__).with_name(name).read_bytes())
    return digest.hexdigest()

def manifest_path(path):
    return Path(path).with_suffix('.manifest.json')

def provenance_issues(content, manifest):
    bad = []
    def fail(code, text): bad.append(issue('G1', code, text))
    if not isinstance(manifest, dict):
        fail('MISSING_LINEAGE', 'Feature provenance manifest is missing or unreadable; recommendations are withheld.')
        return tuple(bad)
    if manifest.get('feature_sha256') != hashlib.sha256(content).hexdigest():
        fail('FEATURE_HASH_MISMATCH', 'Feature content does not match its verified manifest.')
    try:
        raw_cutoff = manifest['cutoff']
        if not isinstance(raw_cutoff, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', raw_cutoff):
            raise ValueError()
        cutoff = pd.Timestamp(raw_cutoff)
        if pd.isna(cutoff) or cutoff.tz is not None:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        fail('INVALID_CUTOFF', 'Observation cutoff is missing or invalid.')
    if manifest.get('schema_version') != 1 or manifest.get('builder_version') != BUILDER_VERSION or manifest.get('event_definition') != EVENT_DEFINITION or manifest.get('verification') not in {'source_rebuild', 'source_rebuild_compared'}:
        fail('UNVERIFIED_LINEAGE', 'Feature schema, builder or verification evidence is not recognized.')
    source_hash = manifest.get('source_sha256')
    if not isinstance(source_hash, str) or len(source_hash) != 64 or any(c not in '0123456789abcdef' for c in source_hash):
        fail('INVALID_SOURCE_HASH', 'Source content fingerprint is unavailable.')
    return tuple(bad)

@dataclass(frozen=True)
class DecisionRecord:
    alias: str
    values: tuple
    rating: str
    priority: float
    reason_codes: tuple
    invalid: bool

@dataclass(frozen=True)
class DecisionIndex:
    records: tuple
    input_rows: int
    exclusions: tuple
    lineage_errors_json: str
    dataset_hash: str
    policy_hash: str
    cutoff: str

    @property
    def lineage_issues(self):
        return tuple(json.loads(self.lineage_errors_json))

    @property
    def counts(self):
        return {rating: sum(r.rating == rating for r in self.records) for rating in ('SUPPORTED', 'CAUTION', 'ABSTAIN')}

    @property
    def invalid_records(self):
        return sum(r.invalid for r in self.records)

    def table(self, rating=None, search=''):
        rows = [dict(customer=r.alias, priority=round(r.priority, 3), rating=r.rating, action='Eligible for staff review only' if r.rating == 'SUPPORTED' else 'Manual investigation required' if r.rating == 'CAUTION' else 'Withhold sales offer; investigate') for r in self.records if (rating is None or r.rating == rating) and search.upper() in r.alias]
        return pd.DataFrame(rows, columns=['customer', 'priority', 'rating', 'action'])

    def page(self, page=1, page_size=25, rating='SUPPORTED', search=''):
        if page < 1 or page_size < 1:
            raise ValueError('Page and page size must be positive.')
        return self.table(rating, search).iloc[(page - 1) * page_size:page * page_size].reset_index(drop=True)

    def passport(self, alias):
        record = next(r for r in self.records if r.alias == alias)
        p = evaluate(row_case(dict(zip(FEATURE_COLUMNS, record.values)), self.lineage_issues))
        p['customer_id'] = record.alias
        p['lineage'] = {'dataset_sha256': self.dataset_hash, 'policy_sha256': self.policy_hash, 'cutoff': self.cutoff, 'snapshot_as_of': 'unknown; current dataset snapshot, not historical evidence'}
        return p

    def customer_values(self, alias):
        record = next(r for r in self.records if r.alias == alias)
        return dict(zip(FEATURE_COLUMNS, record.values))

def build_index(frame, key, lineage_issues=(), dataset_hash='', policy_hash='', cutoff='unknown'):
    missing = set(FEATURE_COLUMNS) - set(frame.columns)
    if missing:
        raise FeatureValidationError('MISSING_REQUIRED_FIELDS', 'Required feature columns are missing: ' + ', '.join(sorted(missing)))
    valid_ids = frame.customer_id.map(identifier)
    duplicates = frame.customer_id.duplicated(keep=False) & valid_ids
    exclusions = tuple((int(i), 'DUPLICATE_CUSTOMER_ID' if bool(duplicates.iloc[i]) else 'INVALID_CUSTOMER_ID') for i in range(len(frame)) if bool(duplicates.iloc[i]) or not bool(valid_ids.iloc[i]))
    excluded = {i for i, code in exclusions}
    records = []
    aliases = set()
    for i, values in enumerate(frame[list(FEATURE_COLUMNS)].itertuples(index=False, name=None)):
        if i in excluded:
            continue
        # Detach accepted in-memory portfolio lists from caller-owned mutable cells.
        values = tuple(tuple(v) if isinstance(v, list) else v for v in values)
        case = row_case(dict(zip(FEATURE_COLUMNS, values)), lineage_issues)
        p = evaluate(case)
        alias = presentation_alias(case.customer_id, key)
        if alias in aliases:
            raise FeatureValidationError('ALIAS_COLLISION', 'Presentation identity collision detected; dataset cannot be displayed safely.')
        aliases.add(alias)
        records.append(DecisionRecord(alias, values, p['rating'], p['priority_score'], tuple(p['reason_codes']), bool(p['validation_issues'])))
    records.sort(key=lambda r: (-r.priority, r.alias))
    return DecisionIndex(tuple(records), len(frame), exclusions, json.dumps(lineage_issues), dataset_hash, policy_hash, cutoff)

@lru_cache(maxsize=2)
def _cached_index(content, manifest_content, key, policy_hash):
    try:
        manifest = json.loads(manifest_content)
    except (ValueError, TypeError):
        manifest = None
    try:
        frame = pd.read_csv(io.BytesIO(content), dtype={'customer_id': str})
    except (ValueError, pd.errors.ParserError) as exc:
        raise FeatureValidationError('UNREADABLE_FEATURES', 'Feature CSV cannot be parsed; rebuild it from the authorized source.') from None
    lineage = list(provenance_issues(content, manifest))
    if isinstance(manifest, dict) and (type(manifest.get('rows')) is not int or manifest['rows'] != len(frame)):
        lineage.append(issue('G1', 'MANIFEST_ROW_COUNT_MISMATCH', 'Manifest population does not match the imported features.'))
    return build_index(frame, key, tuple(lineage), hashlib.sha256(content).hexdigest(), policy_hash, manifest.get('cutoff', 'unknown') if isinstance(manifest, dict) else 'unknown')

def load_index(path, key=None, policy_version=POLICY_VERSION):
    path = Path(path)
    try:
        content = path.read_bytes()
    except OSError:
        raise FeatureValidationError('MISSING_FEATURES', 'Customer features are unavailable; configure BANCINC_FEATURES_PATH or rebuild them.') from None
    try:
        manifest = manifest_path(path).read_bytes()
    except OSError:
        manifest = b''
    return _cached_index(content, manifest, key if key is not None else alias_key(), policy_fingerprint(policy_version))
