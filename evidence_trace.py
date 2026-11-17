"""Honest feature-level provenance; no invented transaction identifiers."""
DERIVATIONS = {
    'qualifying_events_180d': ('HISTORICAL','Count valid known non-fee events in [cutoff-180 days, cutoff).'),
    'recency_days': ('HISTORICAL','Whole days from cutoff to latest valid non-fee event strictly before cutoff.'),
    'relationship_activity_percentile': ('HISTORICAL','Average percentile rank of 180-day absolute transaction volume over the observation-time cohort; rounded to four decimals.'),
    'behavioural_reason': ('HISTORICAL','Repeated qualifying cash-deposit evidence in the preceding 180 days; not salary or verified suitability.'),
    'customer_status': ('CURRENT_SNAPSHOT','Current source snapshot; effective date unavailable; not a historical predictor.'),
    'account_status': ('CURRENT_SNAPSHOT','Current account-state snapshot; effective date unavailable.'),
    'kyc_status': ('CURRENT_SNAPSHOT','Current KYC snapshot; effective date unavailable.'),
    'products_held': ('CURRENT_SNAPSHOT','Recorded current portfolio used to suppress an already-held product; effective date unavailable.'),
}

def references(customer_ref,dataset_hash,source_hash,cutoff):
    return [{'level':'FEATURE_LEVEL','feature':feature,'customer_ref':customer_ref,'artifact_sha256':dataset_hash,'source_sha256':source_hash,'cutoff':cutoff if kind=='HISTORICAL' else None,'temporal_kind':kind,'derivation':description,'source_event_references':[],'traceability_code':'NO_EVENT_LINEAGE_IN_FEATURE_ARTIFACT'} for feature,(kind,description) in DERIVATIONS.items()]

TRACEABILITY_NOTICE = ('Feature-level provenance only. The source ZIP has transaction identifiers, but the customer-feature artifact does not retain a verified event-to-feature reference mapping. No transaction identifiers are invented or stored; transaction-level replay is not implemented.')
