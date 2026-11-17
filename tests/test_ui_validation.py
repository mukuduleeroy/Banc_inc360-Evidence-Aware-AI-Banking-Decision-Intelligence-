"""Controlled synthetic corrupted imports verify fail-closed UI behavior."""
from pathlib import Path
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from data_access import load_index
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('changes',[{'products_held':'[malformed'},{'account_status':None},{'kyc_status':'UNKNOWN'},{'qualifying_events_180d':float('nan')}])
def test_invalid_import_cannot_populate_actionable_queue(feature_row,write_features,monkeypatch,changes):
    path=write_features(pd.DataFrame([dict(feature_row,**changes)]))
    monkeypatch.setenv('BANCINC_FEATURES_PATH',str(path))
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not app.exception
    app.switch_page('views/manager_work_queue.py').run()
    assert not app.exception
    metrics={m.label:m.value for m in app.metric}
    assert int(metrics['Actionable manager-review cases'])==0
    assert metrics['Decision rating']=='ABSTAIN'
    assert app.dataframe[0].value.empty
    assert load_index(path).counts['ABSTAIN']==1
    assert any('No cases match' in i.value for i in app.info)
