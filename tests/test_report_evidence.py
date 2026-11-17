from validation_evidence import test_report as read_test_report,evidence_status
from data_access import build_index
import pandas as pd

def test_only_reconciled_xml_counts_are_displayable(tmp_path):
    p=tmp_path/'report.xml'
    assert read_test_report(p) is None
    p.write_text('<testsuites><testsuite tests="2" failures="0" errors="0" skipped="0"><testcase/><testcase/></testsuite></testsuites>')
    report=read_test_report(p)
    assert report['tests']==report['passed']==2
    p.write_text('<testsuite tests="99" failures="0"><testcase/></testsuite>')
    assert read_test_report(p) is None
    p.write_text('not xml')
    assert read_test_report(p) is None

def test_source_reconciliation_must_match_loaded_dataset(feature_row):
    index=build_index(pd.DataFrame([feature_row]),b'synthetic',dataset_hash='expected')
    assert evidence_status(index,None)=='Unavailable'
    report={'canonical_sha256_before':'different','canonical_sha256_after':'different','identical':True,'keys_equal':True,'column_differences':{'col':0}}
    assert evidence_status(index,report)=='Stale or different dataset'
    report.update(canonical_sha256_before='expected',canonical_sha256_after='expected')
    assert evidence_status(index,report)=='Matched source rebuild'
