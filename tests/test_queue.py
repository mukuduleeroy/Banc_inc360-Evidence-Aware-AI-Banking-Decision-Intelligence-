import json
from dataclasses import FrozenInstanceError
import pandas as pd
import pytest
import data_access as data

KEY=b'synthetic test key only'

def test_complete_evaluation_and_pagination_after_eligibility(feature_row):
    rows=[dict(feature_row,customer_id=f'SYNTHETIC-{i:05}',customer_status='Restricted',recency_days=90) for i in range(1700)]
    rows += [dict(feature_row,customer_id=f'SYNTHETIC-ELIGIBLE-{i}',recency_days=1) for i in range(31)]
    index=data.build_index(pd.DataFrame(rows),KEY)
    assert len(index.records)==1731
    assert index.counts=={'SUPPORTED':31,'CAUTION':0,'ABSTAIN':1700}
    first,second=index.page(1,25),index.page(2,25)
    assert len(first)==25 and len(second)==6
    assert set(first.rating)|set(second.rating)=={'SUPPORTED'}
    assert not set(first.customer)&set(second.customer)

def test_stable_order_and_collision_free_aliases(feature_row):
    frame=pd.DataFrame([dict(feature_row,customer_id=f'SYNTHETIC-{i:06}') for i in range(2200)])
    a=data.build_index(frame,KEY);b=data.build_index(frame.sample(frac=1,random_state=7),KEY)
    assert a.table().equals(b.table())
    assert len({r.alias for r in a.records})==2200
    assert all('SYNTHETIC' not in r.alias for r in a.records)
    alias=a.records[0].alias
    assert a.passport(alias)['customer_id']==alias
    assert a.customer_values(alias)['customer_id']==b.customer_values(alias)['customer_id']

def test_detect_alias_collision_instead_of_silent_reassignment(feature_row,monkeypatch):
    monkeypatch.setattr(data,'presentation_alias',lambda *args:'COLLISION')
    with pytest.raises(data.FeatureValidationError,match='collision'):
        data.build_index(pd.DataFrame([feature_row,dict(feature_row,customer_id='SYNTHETIC-2')]),KEY)

@pytest.mark.parametrize('conflicting',[False,True])
def test_all_duplicate_identity_rows_quarantined(feature_row,conflicting):
    rows=[feature_row,dict(feature_row,kyc_status='Pending' if conflicting else 'Verified'),dict(feature_row,customer_id='SYNTHETIC-UNIQUE')]
    index=data.build_index(pd.DataFrame(rows),KEY)
    assert len(index.records)==1 and len(index.exclusions)==2
    assert all(code=='DUPLICATE_CUSTOMER_ID' for pos,code in index.exclusions)
    assert len(index.records)+len(index.exclusions)==index.input_rows

@pytest.mark.parametrize('identifier',[None,'','nan','with space'])
def test_invalid_identifiers_quarantined(feature_row,identifier):
    index=data.build_index(pd.DataFrame([dict(feature_row,customer_id=identifier)]),KEY)
    assert not index.records and index.exclusions[0][1]=='INVALID_CUSTOMER_ID'

def test_missing_required_field_is_coded_failure(feature_row):
    frame=pd.DataFrame([feature_row]).drop(columns='kyc_status')
    with pytest.raises(data.FeatureValidationError) as exc:data.build_index(frame,KEY)
    assert exc.value.code=='MISSING_REQUIRED_FIELDS'

def test_row_errors_are_withheld_not_dropped(feature_row):
    index=data.build_index(pd.DataFrame([dict(feature_row,products_held='[bad'),dict(feature_row,customer_id='SYNTHETIC-2',account_status=None)]),KEY)
    assert index.counts['ABSTAIN']==2 and index.invalid_records==2
    assert index.page().empty

@pytest.mark.parametrize('field,value',[('events_90d',7),('deposit_events_180d',-1),('transaction_volume_180d_usd',float('inf')),('service_issue','yes'),('product_gap',False)])
def test_additional_feature_domains(feature_row,field,value):
    index=data.build_index(pd.DataFrame([dict(feature_row,**{field:value})]),KEY)
    assert index.counts['ABSTAIN']==1 and index.invalid_records==1

def test_content_policy_and_manifest_cache_invalidation(feature_row,write_features):
    path=write_features(pd.DataFrame([feature_row]));data._cached_index.cache_clear()
    a=data.load_index(path,KEY);assert data.load_index(path,KEY) is a
    changed=dict(feature_row,kyc_status='Pending');write_features(pd.DataFrame([changed]))
    b=data.load_index(path,KEY)
    assert b is not a and b.counts['ABSTAIN']==1 and b.dataset_hash!=a.dataset_hash
    c=data.load_index(path,KEY,policy_version='changed-policy-token')
    assert c is not b and c.policy_hash!=b.policy_hash
    manifest=json.loads(data.manifest_path(path).read_text());manifest['cutoff']='2026-01-01';data.manifest_path(path).write_text(json.dumps(manifest))
    d=data.load_index(path,KEY,policy_version='changed-policy-token')
    assert d is not c and d.cutoff=='2026-01-01'
    with pytest.raises(FrozenInstanceError):d.records[0].rating='SUPPORTED'

def test_unverified_or_changed_import_fails_closed(feature_row,write_features):
    path=write_features(pd.DataFrame([feature_row]));data.manifest_path(path).unlink()
    assert data.load_index(path,KEY).counts['ABSTAIN']==1
    path=write_features(pd.DataFrame([feature_row]));path.write_bytes(path.read_bytes()+b'\n')
    index=data.load_index(path,KEY)
    assert index.counts['ABSTAIN']==1 and index.lineage_issues[0]['code']=='FEATURE_HASH_MISMATCH'
    issues=index.lineage_issues;issues[0]['code']='mutated'
    assert index.lineage_issues[0]['code']=='FEATURE_HASH_MISMATCH'

def test_alias_secret_is_stable_and_private(tmp_path):
    path=tmp_path/'secret';first=data.alias_key(path)
    assert first==data.alias_key(path) and len(first)==32
    assert path.stat().st_mode & 0o777 == 0o600

def test_mixed_csv_column_does_not_invalidate_valid_numeric_tokens(feature_row):
    # A corrupt CSV cell causes pandas to read the entire column as object strings.
    rows=[dict(feature_row,qualifying_events_180d='5'),dict(feature_row,customer_id='SYNTHETIC-2',qualifying_events_180d='bad')]
    index=data.build_index(pd.DataFrame(rows),KEY)
    assert index.counts['SUPPORTED']==1 and index.counts['ABSTAIN']==1

@pytest.mark.parametrize('change',[{'cutoff':'not-a-date'},{'source_sha256':None},{'verification':'unverified'},{'rows':2}])
def test_invalid_manifest_evidence_abstains(feature_row,write_features,change):
    path=write_features(pd.DataFrame([feature_row]))
    manifest=json.loads(data.manifest_path(path).read_text());manifest.update(change);data.manifest_path(path).write_text(json.dumps(manifest))
    index=data.load_index(path,KEY)
    assert index.counts['ABSTAIN']==1 and index.invalid_records==1

def test_index_detaches_mutable_in_memory_portfolio(feature_row):
    portfolio=['Current Account']
    index=data.build_index(pd.DataFrame([dict(feature_row,products_held=portfolio)]),KEY)
    portfolio.append('Savings Account')
    assert index.records[0].rating=='SUPPORTED'
    assert index.passport(index.records[0].alias)['rating']=='SUPPORTED'

@pytest.mark.parametrize('cutoff',[None,'July 1, 2026'])
def test_cutoff_manifest_requires_explicit_iso_date(feature_row,write_features,cutoff):
    path=write_features(pd.DataFrame([feature_row]));manifest=json.loads(data.manifest_path(path).read_text());manifest['cutoff']=cutoff;data.manifest_path(path).write_text(json.dumps(manifest))
    index=data.load_index(path,KEY)
    assert index.counts['ABSTAIN']==1 and 'INVALID_CUTOFF' in index.records[0].reason_codes
