from dataclasses import replace
from engine import Case,evaluate

def test_supported_savings_review(): assert evaluate(Case('1'))['rating']=='SUPPORTED'
def test_insufficient_history_abstains(): assert evaluate(Case('1',qualifying_events_180d=1))['rating']=='ABSTAIN'
def test_borderline_history_caution(): assert evaluate(Case('1',qualifying_events_180d=3))['rating']=='CAUTION'
def test_broken_link_abstains(): assert evaluate(Case('1',account_link_valid=False))['rating']=='ABSTAIN'
def test_future_snapshot_abstains(): assert evaluate(Case('1',future_snapshot_as_history=True))['rating']=='ABSTAIN'
def test_unapproved_model_blocked(): assert evaluate(Case('1',uses_model_for_action=True))['rating']=='ABSTAIN'
def test_unverified_kyc_blocks(): assert evaluate(Case('1',kyc_status='Pending'))['rating']=='ABSTAIN'
def test_already_held_product_suppressed(): assert evaluate(Case('1',products_held=('Savings Account',)))['rating']=='ABSTAIN'
def test_automatic_outreach_blocked(): assert evaluate(Case('1',automatic_outreach=True))['rating']=='ABSTAIN'

import pytest

@pytest.mark.parametrize('identifier', ['', ' ', None, 'nan'])
def test_invalid_customer_identifier(identifier):
    assert evaluate(Case(identifier))['rating'] == 'ABSTAIN'

@pytest.mark.parametrize('status', ['Frozen', 'Dormant'])
def test_restricted_account_blocks(status):
    assert evaluate(Case('1', account_status=status))['rating'] == 'ABSTAIN'

def test_restricted_customer_blocks():
    assert evaluate(Case('1', customer_status='Restricted'))['rating'] == 'ABSTAIN'

@pytest.mark.parametrize('events,rating', [(0,'ABSTAIN'),(2,'CAUTION'),(4,'SUPPORTED')])
def test_history_boundaries(events,rating):
    assert evaluate(Case('1', qualifying_events_180d=events))['rating'] == rating

def test_missing_behaviour_blocks():
    assert evaluate(Case('1', behavioural_reason=''))['rating'] == 'ABSTAIN'

@pytest.mark.parametrize('field', ['staff_verification_required','human_review_required'])
def test_human_controls_required(field):
    assert evaluate(Case('1', **{field:False}))['rating'] == 'ABSTAIN'


def test_unsupported_product_blocks():
    assert evaluate(Case('1', proposed_product='Insurance'))['rating'] == 'ABSTAIN'
