"""Pure visual semantics/contrast and native UI checks; no banking policy changes."""
from pathlib import Path
import hashlib,json
import pytest
from design_system import COLORS,STATUS_COLORS,stylesheet,GATE_LABELS,gate_cards,replay_highlight


def luminance(color):
 rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
 return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),rgb))

def contrast(a,b):
 x,y=sorted([luminance(a),luminance(b)]);return (y+.05)/(x+.05)

@pytest.mark.parametrize('foreground,background',[('text','surface'),('muted','surface'),('muted','background'),('primary','surface'),('sidebar_muted','navy'),('surface','primary'),('supported_text','supported_bg'),('caution_text','caution_bg'),('abstain_text','abstain_bg'),('error_text','error_bg')])
def test_reading_and_status_text_contrast(foreground,background):assert contrast(COLORS[foreground],COLORS[background])>=4.5

def test_semantics_not_color_only():
 assert set(STATUS_COLORS)=={'SUPPORTED','CAUTION','ABSTAIN'};assert GATE_LABELS['ABSTAIN']=='BLOCK · ABSTAIN';assert GATE_LABELS['PASS']=='PASS';assert GATE_LABELS['PENDING']=='PENDING'

def test_css_offline_keyboard_and_responsive_contract():
 css=stylesheet();assert '@import' not in css and 'url(' not in css;assert 'input:not([role="combobox"]):focus-visible' in css;assert '[data-baseweb="select"]:focus-within' in css;assert 'prefers-reduced-motion' in css;assert 'tabular-nums' in css;assert 'max-width:600px' in css;assert 'display:none' not in css

def test_theme_matches_canonical_tokens():
 import toml
 theme=toml.loads(Path('.streamlit/config.toml').read_text())['theme'];assert theme['primaryColor']==COLORS['primary'];assert theme['backgroundColor']==COLORS['background'];assert theme['sidebar']['backgroundColor']==COLORS['navy']

def test_gate_markup_escaped_and_engine_status_preserved(monkeypatch):
 import design_system
 from engine import evaluate,DEMO_CASES
 captured=[];monkeypatch.setattr(design_system.st,'html',captured.append);p=evaluate(DEMO_CASES[1]);before=json.dumps(p,sort_keys=True);gate_cards(p['gates']);assert json.dumps(p,sort_keys=True)==before;markup=captured[0];assert markup.count('<article')==6;assert 'BLOCK · ABSTAIN' in markup
 gate_cards([dict(gate='G1 <unsafe>',status='PASS',reason='<script>bad</script>',reason_codes=['<bad>'])]);assert '<script>' not in captured[-1] and '&lt;script&gt;' in captured[-1]

def test_replay_visual_does_not_mutate_or_expose_unknown_fields(monkeypatch):
 import design_system
 captured=[];monkeypatch.setattr(design_system.st,'html',captured.append)
 p={'baseline':{'rating':'SUPPORTED','evidence':{'original_values':{'kyc_status':'Verified','customer_id':'RAW'}}},'simulated':{'rating':'ABSTAIN','evidence':{'original_values':{'kyc_status':'Pending','customer_id':'RAW'}}},'modified_fields':['kyc_status']};before=json.dumps(p,sort_keys=True);replay_highlight(p);assert json.dumps(p,sort_keys=True)==before;assert 'RAW' not in ''.join(captured);assert 'SUPPORTED → ABSTAIN' in captured[0];assert 'SIMULATED' in captured[1] and 'Verified' in captured[1] and 'Pending' in captured[1]

def test_independent_student_branding_no_official_assets():
 text=Path('design_system.py').read_text();assert 'Independent student hackathon prototype' in text and 'not operated by BancABC' in text;assert 'BancABC' not in Path('assets/brand.svg').read_text()


def test_sidebar_caption_styles_do_not_leak_to_main():
 css=stylesheet();assert '[data-testid="stSidebar"] [data-testid="stMain"]' not in css;assert '[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:var(--banc-sidebar-muted)!important;}' in css
