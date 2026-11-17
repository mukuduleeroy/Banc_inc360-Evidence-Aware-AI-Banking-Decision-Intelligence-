"""Explicit synthetic feature fixtures for validation/queue unit tests."""
import hashlib
import json
import pytest
from data_access import BUILDER_VERSION, EVENT_DEFINITION, manifest_path

@pytest.fixture
def feature_row():
    return dict(customer_id='SYNTHETIC-1',qualifying_events_180d=5,events_90d=3,recency_days=45,transaction_volume_180d_usd=100.,deposit_events_180d=2,product_gap=True,behavioural_reason='SYNTHETIC repeated deposits',products_held='[]',customer_status='Active',account_status='Active',kyc_status='Verified',service_issue=False,customer_segment='SYNTHETIC',account_count=1,relationship_activity_percentile=.7)

@pytest.fixture
def write_features(tmp_path):
    def write(frame, name='features.csv'):
        path=tmp_path/name;frame.to_csv(path,index=False)
        # Explicitly synthetic local fixture; source hash is a fixture token, never real-data evidence.
        manifest=dict(schema_version=1,builder_version=BUILDER_VERSION,event_definition=EVENT_DEFINITION,verification='source_rebuild',feature_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(b'SYNTHETIC TEST SOURCE').hexdigest(),cutoff='2026-07-01',rows=len(frame))
        manifest_path(path).write_text(json.dumps(manifest));return path
    return write
