"""Run Streamlit's real script runtime without a browser; synthetic audit data only."""
from pathlib import Path
import json
import os
import tempfile
import sys
from streamlit.testing.v1 import AppTest

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from engine import DEMO_CASES
results={}
at=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
assert not at.exception, at.exception
assert at.metric[0].label == 'Qualifying events / 180d'
assert at.metric[-1].value in ('SUPPORTED','CAUTION','ABSTAIN')
assert len(at.dataframe) >= 3
results['real_customer_indicators_passport_queue']=True
at.radio[0].set_value('Synthetic gate demonstrations').run()
assert not at.exception
assert at.metric[0].value == 'SUPPORTED'
at.text_input[0].set_value('Synthetic verification only').run()
at.button[0].click().run()
assert len(at.session_state['audit']) == 1
results['human_decision_session_log']=True
for i in [1,3,5]:
    at.selectbox[0].select(DEMO_CASES[i]).run()
    assert not at.exception
    assert at.metric[0].value == 'ABSTAIN'
results['kyc_duplicate_product_restricted_customer_suppression']=True
queue=at.dataframe[1].value
assert set(queue['rating']) <= {'SUPPORTED'}
results['queue_supported_only']=True
os.environ['BANCINC_FEATURES_PATH']=str(Path(tempfile.gettempdir())/'bancinc-intentionally-missing.csv')
missing=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
assert not missing.exception
assert len(missing.warning) == 1
results['missing_file_demo_fallback']=True
(root/'outputs/ui_verification.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
