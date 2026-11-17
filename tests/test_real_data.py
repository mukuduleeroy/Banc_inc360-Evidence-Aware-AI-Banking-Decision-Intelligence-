"""Local competition-data regression, never a synthetic replacement."""
from pathlib import Path
import hashlib
import pytest
from data_access import load_index

ROOT=Path(__file__).resolve().parents[1]

def test_supplied_competition_queue_reconciles_all_rows():
    path=ROOT/'outputs/customer_features.csv'
    if not path.is_file():pytest.skip('Authorized competition feature file is not available in this checkout.')
    before=hashlib.sha256(path.read_bytes()).hexdigest()
    index=load_index(path)
    # Manifest must be verified against the actual ZIP via scripts/reconcile_phase2.py.
    assert not index.lineage_issues, 'Run the source reconciliation; do not invent provenance.'
    assert len(index.records)+len(index.exclusions)==index.input_rows
    assert sum(index.counts.values())==len(index.records)
    assert index.counts['SUPPORTED']>0
    queue=index.table('SUPPORTED')
    assert len(queue)==index.counts['SUPPORTED'] and set(queue.rating)=={'SUPPORTED'}
    assert len(index.page())==min(25,len(queue))
    assert len({r.alias for r in index.records})==len(index.records)
    assert all(index.passport(alias)['rating']=='SUPPORTED' for alias in index.page().customer)
    assert before==hashlib.sha256(path.read_bytes()).hexdigest()
