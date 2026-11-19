"""Read-only local acceptance evidence. Not imported by application decision paths."""
from pathlib import Path
import hashlib,json
from data_access import FEATURE_COLUMNS,load_index,manifest_path

ROOT=Path(__file__).resolve().parent
REFERENCE=ROOT/'tests/fixtures/reference_local_baseline.json'

def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def decision_fingerprint(index):
    """Hash all keyed decisions in memory; never export the underlying customer identifiers."""
    position=FEATURE_COLUMNS.index('customer_id')
    rows=sorted((str(r.values[position]),r.rating,r.priority,list(r.reason_codes),r.invalid) for r in index.records)
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def verify_local_baseline():
    reference=json.loads(REFERENCE.read_text());path=ROOT/'outputs/customer_features.csv'
    if not path.is_file():raise AssertionError('Authorized local dataset is missing; full-data acceptance is unavailable.')
    assert sha256(path)==reference['feature_sha256'],'Canonical dataset differs from the reviewed local baseline.'
    assert sha256(manifest_path(path))==reference['manifest_sha256'],'Canonical manifest differs from the reviewed local baseline.'
    index=load_index(path)
    assert not index.lineage_issues,'Source provenance is not validated.'
    assert index.policy_hash==reference['policy_sha256'],'Decision policy differs from the reviewed local baseline.'
    assert len(index.records)==reference['customers'] and index.input_rows==reference['customers']
    assert not index.exclusions and not index.invalid_records
    assert index.counts==reference['counts'],'Unexpected decision-count changes.'
    fingerprint=decision_fingerprint(index)
    assert fingerprint==reference['decision_fingerprint'],'Unexpected customer-level decision/priority/reason changes.'
    assert len(index.table('SUPPORTED'))==index.counts['SUPPORTED']
    assert sum(index.counts.values())==len(index.records)
    return {'customers':len(index.records),'counts':index.counts,'feature_sha256':index.dataset_hash,'manifest_sha256':reference['manifest_sha256'],'policy_sha256':index.policy_hash,'decision_fingerprint':fingerprint,'full_population_decisions_unchanged':True,'invalid_records':index.invalid_records,'quarantined_records':len(index.exclusions),'scope':'verified local technical regression baseline, not bank approval or data-publication permission'}


def source_snapshot(root=ROOT):
    """Hash application/test/config assets only; never read customer data or secret files."""
    root=Path(root).resolve();paths=set(root.glob('*.py'))|set(root.glob('requirements*.txt'))
    for directory in ('tests','scripts','views'):
        paths.update((root/directory).rglob('*.py'))
    paths.update((root/'tests/fixtures').glob('*.json'))
    paths.update(p for p in (root/'assets').rglob('*') if p.is_file())
    if (root/'.streamlit/config.toml').exists():paths.add(root/'.streamlit/config.toml')
    result={}
    for path in sorted(paths):
        if not path.is_file() or '__pycache__' in path.parts:continue
        assert path.resolve().is_relative_to(root),'Source symlink escapes the project root.'
        result[str(path.relative_to(root))]=sha256(path)
    assert result,'No application/test sources found for acceptance.'
    return result


def verify_run_manifest(junit,manifest,root=ROOT):
    """Tie a passing test run to current source content and its exact JUnit bytes."""
    data=json.loads(Path(manifest).read_text())
    assert data.get('pytest_exit_code')==0 and data.get('status')=='PASS','Regression runner did not complete successfully.'
    assert data.get('before_source_hashes')==data.get('after_source_hashes')==source_snapshot(root),'Sources changed during or after regression; rerun the full suite.'
    assert data.get('junit_sha256')==sha256(junit),'JUnit evidence differs from the completed regression run.'
    return {'source_files_verified':len(data['before_source_hashes']),'source_unchanged_during_and_after_run':True,'junit_matches_run_manifest':True,'started_utc':data.get('started_utc'),'finished_utc':data.get('finished_utc')}
