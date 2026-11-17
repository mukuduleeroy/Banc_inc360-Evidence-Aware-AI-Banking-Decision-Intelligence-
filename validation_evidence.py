"""Read measured local reports; missing or stale evidence never becomes a passing claim."""
from pathlib import Path
import json,hashlib
from xml.etree import ElementTree as E

ROOT=Path(__file__).resolve().parent

def json_report(path):
    try:
        value=json.loads(Path(path).read_text())
        return value if isinstance(value,dict) else None
    except (OSError,ValueError):return None

def test_report(path):
    try:
        content=Path(path).read_bytes();root=E.fromstring(content)
        suites=[root] if root.tag=='testsuite' else list(root.findall('testsuite'))
        if not suites: return None
        totals={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
        cases=list(root.iter('testcase'))
        if len(cases)!=totals['tests']:return None
        passed=sum(not any(t.tag in {'failure','error','skipped'} for t in case) for case in cases)
        if passed+totals['failures']+totals['errors']+totals['skipped']!=totals['tests']:return None
        return {**totals,'passed':passed,'timestamp':suites[0].attrib.get('timestamp','Unknown'),'artifact':str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else Path(path).name,'sha256':hashlib.sha256(content).hexdigest()}
    except (OSError,ValueError,E.ParseError):return None

def evidence_status(index,report):
    if not report:return 'Unavailable'
    before=report.get('canonical_sha256_before');after=report.get('canonical_sha256_after')
    if before!=index.dataset_hash or after!=index.dataset_hash:return 'Stale or different dataset'
    diffs=report.get('column_differences')
    return 'Matched source rebuild' if report.get('identical') is True and report.get('keys_equal') is True and isinstance(diffs,dict) and not any(diffs.values()) else 'Not reconciled'
